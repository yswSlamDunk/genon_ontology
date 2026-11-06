"""Copilot — 오른쪽 대화창. 말을 받아 (1) 데이터 질문이면 답하기 (2) 바꾸자는 말이면 변경 제안 (3) 그 밖엔 지금 상태 설명.

바꾸는 것은 바로 적용하지 않고 "변경 신청" 카드로 돌려줌 → 사람이 신청 → 변경 이력에서 승인해야 적용.
"""
import json

from . import docs, history, llm, onto, qa, rules
from .db import kv_get, one


def _state() -> str:
    v = onto.view()
    return (f"구축 의도: {v['intent'] or '(없음)'}\n개체 {len(v['objects'])}개: {', '.join(o['label'] for o in v['objects'])[:600]}\n"
            f"관계 {len(v['relations'])}개 · 아직 개체가 아닌 표: {', '.join(v['loose_tables']) or '없음'}\n"
            f"읽을 칸: {', '.join(f['label'] for f in docs.fields()) or '없음'} · 규칙 {len(rules.listing())}개 · "
            f"지표 {len(qa.metrics())}개 · 골든 질문 {len(qa.golden())}개 · 승인 대기 {history.pending_count()}건")


def reply(text: str, page: str = "", who: dict | None = None) -> dict:
    if not llm.available():
        return {"kind": "text", "text": "LLM 키가 없어 Copilot을 쓸 수 없습니다."}
    if who and who.get("role") == "현업":  # 쓰는 사람: 질문만
        try:
            r = qa.ask(text, who)
        except Exception as e:
            return {"kind": "text", "text": f"요청 처리에 실패했습니다. {str(e)[:200]}"}
        return _answer(r)
    d = llm.chat_json(
        "너는 온톨로지 작업 공간의 Copilot이다. 사용자 말을 하나로 분류한다. "
        "ask=데이터 값에 대한 질문(특정 건 · 금액 · 여부 등), add_relation=두 개체를 이으라는 요청, add_rule=업무 규칙을 만들자는 요청, "
        "add_field=문서에서 읽을 칸을 더하자는 요청, add_metric=자주 볼 여러 건 계산(지표)을 저장하자는 요청, explain=작업 공간 상태 · 기능 설명 요청. "
        "몇 건 · 합계 · 순위 같은 데이터 질문은 ask다. "
        '형식: {"kind":"ask|add_relation|add_rule|add_field|add_metric|explain","rule_kind":"판단|분류","answer":"explain일 때 2~3문장 답(지금 상태만 근거로)"}',
        f"지금 화면: {page}\n작업 공간 상태:\n{_state()}\n사용자: {text}")
    k = d.get("kind")
    try:
        if k == "ask":
            return _answer(qa.ask(text, who))
        if k == "add_metric":
            m = qa.metric_compile(text)
            return {"kind": "proposal", "title": f"지표 추가 · {m['name']}", "layer": "지표", "op": {"type": "add_metric", "metric": {x: m[x] for x in ("name", "text", "spec")}},
                    "lines": [m["plain"], f"지금 값: {json.dumps(m['preview']['rows'][:3], ensure_ascii=False)[:160]}"], "why": "여러 건 계산을 지표로 저장하면 같은 질문에 늘 같은 계산식을 씁니다."}
        if k == "add_relation":
            s = onto.suggest_relation(text)
            op = {"type": "add_rel", "rel": {x: s[x] for x in ("a_tbl", "a_col", "b_tbl", "b_col", "name")}}
            return {"kind": "proposal", "title": f"관계 추가 · {s['a_label']} → {s['b_label']}", "layer": "개체 · 관계", "op": op,
                    "lines": [f"{s['a_tbl']}.{s['a_col']} → {s['b_tbl']}.{s['b_col']}", f"값 겹침 {s['ov']['hit']} / {s['ov']['a']}"],
                    "why": s.get("why", "")}
        if k == "add_rule":
            kind = d.get("rule_kind") if d.get("rule_kind") in ("판단", "분류") else "판단"
            c = rules.compile_text(text, kind)
            op = {"type": "add_rule", "rule": {"kind": kind, "name": c.get("name"), "text": text, "start": c["start"], "when": c["when"], "then": c.get("then")}}
            return {"kind": "proposal", "title": f"{kind} 규칙 추가 · {c.get('name')}", "layer": "규칙", "op": op,
                    "lines": [f"시작: {onto.label(c['start'])}"] + [f"{w['obj']}.{w['col']} {w['op']} {w.get('value') if 'value' in w else w['ref']['obj'] + '.' + w['ref']['col']}" for w in c["when"]] + [f"→ {c.get('then')}"],
                    "why": "실행 가능" if c["check"]["ok"] else "주의: " + ", ".join(c["check"]["why"])}
        if k == "add_field":
            f = llm.chat_json('문서에서 읽을 칸 하나를 정한다. 형식: {"name":"영문 소문자_밑줄","label":"한국어 이름","desc":"AI에게 줄 설명(형식 포함)"}', text)
            return {"kind": "proposal", "title": f"읽을 칸 추가 · {f.get('label')}", "layer": "읽을 칸", "op": {"type": "add_field", "field": f},
                    "lines": [f"{f.get('name')} — {f.get('desc')}"], "why": ""}
    except Exception as e:
        return {"kind": "text", "text": f"요청 처리에 실패했습니다. {str(e)[:200]}"}
    return {"kind": "text", "text": d.get("answer") or "무엇을 도와드릴까요?"}


def _answer(r: dict) -> dict:
    return {"kind": "answer", "ask_id": r["id"], "status": r["status"], "answer": r["answer"], "detail": r.get("detail", ""),
            "evidence": r.get("evidence", [])[:4], "missing": r.get("missing", []), "table": r.get("table"), "mode": r.get("mode")}


def propose(title: str, layer: str, op: dict, lines: list[str]) -> int:
    if op.get("type") not in ("add_rel", "add_rule", "add_field", "add_metric", "add_calc"):
        raise ValueError("신청할 수 없는 변경입니다.")
    return history.propose(title, layer, op, {"lines": lines})
