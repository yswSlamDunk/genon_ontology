"""계산 과정 펼쳐 보기 · 가정 바꿔 보기(What-if).

- explain: 개체 한 건의 계산 속성마다 식 · 들어간 값(원본 표 · 줄) · 중간 결과 · 결과.
  들어간 값이 비었거나 사람 확인 전(문서 읽기 검수 대기)이면 "예상".
- run: 값 몇 개를 임시로 바꾼 복사본 DB에서 계산 속성 · 규칙 판정 · 골든 질문 답을 다시 구해 "지금 / 바꾸면"으로.
  원본 DB는 바꾸지 않음. 가정은 이름을 붙여 scenario 표에 저장.
"""
import json
import re
import sqlite3
import tempfile
from pathlib import Path

from . import history, onto, rules
from .db import DATA, DB_OVERRIDE, connect, dt, now, one, ot, q, rows
from .onto import _rel_between, cond_sql, label, objects

KIND = {"expr": "같은 줄 계산", "agg": "이어진 줄 집계", "lookup": "이어진 값 가져오기"}
FN = {"count": "개수", "sum": "합계", "avg": "평균", "min": "최솟값", "max": "최댓값"}


def _obj(name: str) -> dict:
    o = next((x for x in objects() if x["name"] == name), None)
    if not o:
        raise ValueError(f"개체 {name}이(가) 없습니다.")
    return o


def _pending() -> set[tuple[str, str]]:
    """문서 읽기에서 사람 확인을 기다리는 값(문서 · 칸)."""
    from . import docs
    try:
        return {(r["doc_id"], r["field"]) for r in docs.review_list()}
    except Exception:
        return set()


def _plab(o: dict, col: str) -> str:
    return next((p["label"] for p in o["props"] if p["col"] == col), col)


def _input(o: dict, col: str, row: dict, pend: set, base_key: str) -> dict:
    """들어간 값 하나 — 값 · 출처(원본 표 · 줄) · 상태."""
    v = row.get(col)
    calc = next((p for p in o["props"] if p["col"] == col and p["calc"]), None)
    st = "확정"
    if v is None or str(v).strip() == "":
        st = "빈 값"
    elif o["base"] == "doc_extract" and (str(row.get("doc_id")), col) in pend:
        st = "사람 확인 전"
    elif calc:
        st = "계산 속성"
    return {"obj": o["name"], "obj_label": o["label"], "col": col, "label": _plab(o, col), "value": v,
            "src": f"{o['base']} · {o['key']} = {row.get(o['key'])}", "row": row.get(base_key), "state": st}


def explain(name: str, key: str, cols: list[str] | None = None) -> list[dict]:
    """개체 한 건(키 값)의 계산 속성 풀이."""
    o = _obj(name)
    row = one(f"SELECT * FROM {ot(name)} WHERE CAST({q(o['key'])} AS TEXT)=?", (str(key),))
    if not row:
        raise ValueError(f"{o['label']} {key}을(를) 찾을 수 없습니다.")
    pend = _pending()
    out = []
    for p in o["props"]:
        if not p["calc"] or (cols and p["col"] not in cols):
            continue
        spec = json.loads(p["calc"]) if isinstance(p["calc"], str) else p["calc"]
        k = spec.get("kind")
        item = {"col": p["col"], "label": p["label"], "kind": KIND.get(k, k), "text": spec.get("text") or spec.get("plain") or "",
                "result": row.get(p["col"]), "inputs": [], "steps": []}
        try:
            if k == "expr":
                e = str(spec.get("sql", ""))
                used = [c for c in dict.fromkeys(re.findall(r'"([^"]+)"', e)) if c in row]
                item["inputs"] = [_input(o, c, row, pend, o["key"]) for c in used]
                filled = e
                for c in used:
                    filled = filled.replace(f'"{c}"', repr(row.get(c)) if row.get(c) is not None else "빈 값")
                item["formula"] = e
                item["steps"] = [f"값 넣기: {filled}", f"결과: {row.get(p['col'])}"]
            else:
                other = _obj(spec["obj"])
                lk = _rel_between(name, other["name"])
                if not lk:
                    raise ValueError("관계가 없어 풀 수 없습니다.")
                src, flt = onto._src(other["name"])
                where = [f"x.{q(lk[1])} = ?"] + ([flt] if flt else []) + [cond_sql("x", w["col"], w["op"], w["value"]) for w in spec.get("where", [])]
                rs = rows(f"SELECT * FROM {src} x WHERE {' AND '.join(where)} LIMIT 50", (row.get(lk[0]),))
                cond = f"{other['label']}.{_plab(other, lk[1])} = {o['label']}.{_plab(o, lk[0])}({row.get(lk[0])})" + "".join(f" · {_plab(other, w['col'])} {w['op']} {w['value']}" for w in spec.get("where", []))
                item["formula"] = (f"{other['label']}의 {_plab(other, spec.get('col'))}" if k == "lookup" else f"{other['label']} {('줄 ' if spec.get('fn', 'count') == 'count' else _plab(other, spec.get('col')) + ' ')}{FN.get(spec.get('fn', 'count'), spec.get('fn'))}") + f" (조건: {cond})"
                col = spec.get("col") if k == "lookup" or spec.get("fn", "count") != "count" else other["key"]
                item["inputs"] = [_input(other, col, r, pend, other["key"]) for r in rs[: (1 if k == "lookup" else 50)]]
                if k == "agg":
                    nums = [r.get(col) for r in rs]
                    item["steps"] = [f"이어진 {other['label']} {len(rs)}줄 찾음", (f"{FN.get(spec.get('fn'), '')}: " + " + ".join(str(v) for v in nums[:12]) + (" …" if len(nums) > 12 else "") if spec.get("fn", "count") == "sum" else f"{FN.get(spec.get('fn', 'count'))} 계산"), f"결과: {row.get(p['col'])}"]
                else:
                    item["steps"] = [f"이어진 {other['label']} {len(rs)}줄 중 첫 줄의 값", f"결과: {row.get(p['col'])}"]
        except Exception as e:
            item["error"] = str(e)[:160]
        bad = [i for i in item["inputs"] if i["state"] in ("빈 값", "사람 확인 전")]
        item["estimated"] = bool(bad) or item["result"] is None
        item["why"] = [f"{i['obj_label']} {i['label']} {i['state']}" for i in bad][:5] + (["결과가 비어 있음"] if item["result"] is None else [])
        out.append(item)
    return out


def mask_items(items: list[dict], who: dict | None) -> list[dict]:
    """현업에게는 민감 속성으로 들어간 값을 가림."""
    if not who or who.get("role") != "현업":
        return items
    sens = {(r["obj"], r["col"]) for r in rows("SELECT obj, col FROM prop WHERE sensitive=1")}
    for it in items:
        for i in it.get("inputs", []):
            if (i["obj"], i["col"]) in sens and i["value"] not in (None, ""):
                i["value"] = "●●●"
        it["steps"] = [s for s in it.get("steps", []) if not s.startswith("값 넣기")] if any((i["obj"], i["col"]) in sens for i in it.get("inputs", [])) else it.get("steps", [])
    return items


def calc_cols(name: str) -> list[str]:
    return [p["col"] for p in _obj(name)["props"] if p["calc"]]


# ── 가정 바꿔 보기 ──
def _copy() -> str:
    """원본 DB를 임시 파일로 통째 복사(원본은 그대로)."""
    tmp = tempfile.NamedTemporaryFile(prefix="geno_whatif_", suffix=".db", delete=False)
    tmp.close()
    src = connect()
    dst = sqlite3.connect(tmp.name)
    src.backup(dst)
    dst.close()
    return tmp.name


def _calc_rows(obj: str, keys: list) -> dict:
    o = _obj(obj)
    cc = [c for c in calc_cols(obj)]
    if not cc or not keys:
        return {}
    ph = ",".join("?" * len(keys))
    rs = rows(f"SELECT {q(o['key'])} AS k, {', '.join(q(c) for c in cc)} FROM {ot(obj)} WHERE CAST({q(o['key'])} AS TEXT) IN ({ph})", [str(k) for k in keys])
    return {str(r["k"]): {c: r[c] for c in cc} for r in rs}


def _affected(changes: list[dict]) -> dict[str, set]:
    """바꾼 줄 + 그 줄을 계산에 쓰는(agg · lookup) 다른 개체의 이어진 줄."""
    aff: dict[str, set] = {}
    objs = objects()
    for ch in changes:
        o = _obj(ch["obj"])
        aff.setdefault(o["name"], set()).add(str(ch["key"]))
        row = one(f"SELECT * FROM {dt(o['base'])} WHERE CAST({q(o['key'])} AS TEXT)=?", (str(ch["key"]),)) or {}
        for x in objs:
            for p in x["props"]:
                if not p["calc"]:
                    continue
                spec = json.loads(p["calc"]) if isinstance(p["calc"], str) else p["calc"]
                if spec.get("obj") != o["name"]:
                    continue
                lk = _rel_between(x["name"], o["name"])
                if not lk:
                    continue
                vals = {str(row.get(lk[1]))} | ({str(ch["value"])} if ch["col"] == lk[1] else set())
                for r in rows(f"SELECT {q(x['key'])} k FROM {ot(x['name'])} WHERE CAST({q(lk[0])} AS TEXT) IN ({','.join('?' * len(vals))}) LIMIT 20", list(vals)):
                    aff.setdefault(x["name"], set()).add(str(r["k"]))
    return aff


def _check(changes: list[dict]) -> list[dict]:
    out = []
    for ch in changes:
        o = _obj(ch.get("obj"))
        base_cols = {p["col"] for p in o["props"] if not p["calc"]}
        if ch.get("col") not in base_cols:
            raise ValueError(f"{o['label']}의 {ch.get('col')}은(는) 바꿀 수 없는 칸입니다(계산 속성은 원본 값을 바꿔 주세요).")
        if not one(f"SELECT 1 FROM {dt(o['base'])} WHERE CAST({q(o['key'])} AS TEXT)=?", (str(ch.get("key")),)):
            raise ValueError(f"{o['label']} {ch.get('key')}을(를) 찾을 수 없습니다.")
        old = one(f"SELECT {q(ch['col'])} v FROM {dt(o['base'])} WHERE CAST({q(o['key'])} AS TEXT)=?", (str(ch["key"]),))["v"]
        out.append({"obj": o["name"], "obj_label": o["label"], "key": str(ch["key"]), "col": ch["col"], "label": _plab(o, ch["col"]), "before": old, "value": str(ch.get("value", ""))})
    if not out:
        raise ValueError("바꿀 값을 하나 이상 넣어 주세요.")
    return out


def _snapshot(aff: dict, rule_ids: list[int]) -> dict:
    calcs = {obj: _calc_rows(obj, sorted(keys)) for obj, keys in aff.items()}
    rs = {}
    for rid in rule_ids:
        try:
            rs[rid] = rules.test(rid)["hits"]
        except Exception as e:
            rs[rid] = {"error": str(e)[:100]}
    return {"calcs": calcs, "rules": rs}


def run(changes: list[dict], with_golden: bool = False) -> dict:
    changes = _check(changes)
    aff = _affected(changes)
    live = [r for r in rules.listing() if r["on_"] and r["check"]["ok"]]
    before = _snapshot(aff, [r["id"] for r in live])
    path = _copy()
    tok = DB_OVERRIDE.set(path)
    try:
        con = connect()
        for ch in changes:
            o = _obj(ch["obj"])
            con.execute(f"UPDATE {dt(o['base'])} SET {q(ch['col'])}=? WHERE CAST({q(o['key'])} AS TEXT)=?", (ch["value"], ch["key"]))
        after = _snapshot(aff, [r["id"] for r in live])
        gold = []
        if with_golden:
            from . import qa
            for g in qa.golden():
                try:
                    r = qa.ask(g["q"])
                    got = r["answer"] + (f" — {r['detail']}" if r.get("detail") else "")
                    ok = qa._grade(g["want"], got) if r["status"] == "ok" else "틀림"
                except Exception as e:
                    got, ok = f"오류: {str(e)[:80]}", "틀림"
                gold.append({"q": g["q"], "want": g["want"], "before": g["got"] or "-", "ok_before": g["ok"], "after": got, "ok_after": ok})
    finally:
        DB_OVERRIDE.reset(tok)
        Path(path).unlink(missing_ok=True)
    calc_out = []
    for obj, keys in aff.items():
        o = _obj(obj)
        for k in sorted(keys):
            for c in calc_cols(obj):
                b, a = before["calcs"].get(obj, {}).get(k, {}).get(c), after["calcs"].get(obj, {}).get(k, {}).get(c)
                calc_out.append({"obj": obj, "obj_label": o["label"], "key": k, "col": c, "label": _plab(o, c), "before": b, "after": a, "changed": str(b) != str(a)})
    rule_out = []
    for r in live:
        b, a = before["rules"].get(r["id"]), after["rules"].get(r["id"])
        if isinstance(b, dict) or isinstance(a, dict):
            rule_out.append({"name": r["name"], "start": label(r["cond"]["start"]), "error": (b or a).get("error") if isinstance(b or a, dict) else ""})
            continue
        rule_out.append({"name": r["name"], "start": label(r["cond"]["start"]), "before": len(b), "after": len(a),
                         "added": [x for x in a if x not in b], "removed": [x for x in b if x not in a], "changed": set(a) != set(b)})
    return {"changes": changes, "calcs": calc_out, "rules": rule_out, "golden": gold, "with_golden": with_golden, "at": now()}


def save(name: str, changes: list[dict], result: dict, by: str = "사람") -> int:
    if not name.strip():
        raise ValueError("가정 이름을 입력해 주세요.")
    sid = connect().execute("INSERT INTO scenario (name, changes, result, by, at) VALUES (?,?,?,?,?)",
                            (name.strip(), json.dumps(changes, ensure_ascii=False), json.dumps(result, ensure_ascii=False), history._who(by), now())).lastrowid
    history.record(f"가정 저장 · {name.strip()}", "가정", by, {"바꾼 값": "; ".join(f"{c.get('obj_label', c.get('obj'))} {c.get('key')} {c.get('label', c.get('col'))} → {c.get('value')}" for c in result.get("changes", changes))[:300]})
    return sid


def listing() -> list[dict]:
    out = []
    for s in rows("SELECT * FROM scenario ORDER BY id DESC"):
        s["changes"], s["result"] = json.loads(s["changes"] or "[]"), json.loads(s["result"] or "{}")
        out.append(s)
    return out


def remove(sid: int, by: str = "사람") -> None:
    s = one("SELECT name FROM scenario WHERE id=?", (sid,))
    connect().execute("DELETE FROM scenario WHERE id=?", (sid,))
    if s:
        history.record(f"가정 삭제 · {s['name']}", "가정", by, {"이름": s["name"]})
