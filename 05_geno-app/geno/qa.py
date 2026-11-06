"""질문 답하기 · 지표 · 골든 질문.

질문은 두 모양:
- 한 건(one): 값 하나로 시작 개체를 찾고 정해진 길(관계)을 따라감 → 규칙 실행 → 필요하면 이어진 문서 본문만 검색(그래프로 거르고 벡터로 고름).
- 여러 건(set): 세기 · 합계 · 평균 · 순위 · ~별 · 목록. 계산은 프로그램이 SQL로 함(LLM이 세지 않음). 다른 개체 조건은 관계를 따라 EXISTS로.
1) 질문 틀 찾기: LLM이 질문을 "틀 + 값"으로 나눔. 같은 틀이 이미 있으면 저장된 길을 그대로 씀 → 묻는 말투가 달라도 같은 답.
2) 길이 없으면 "미연결"로 멈추고 추측하지 않음.
3) 답 쓰기: LLM 1회 — 모은 값 · 계산 결과 · 규칙 결과 · 본문 조각만 넣어 문장으로.
지표(metric) = 이름 붙여 저장한 여러 건 계산. 같은 지표를 물으면 늘 같은 계산식을 씀.
"""
import json
import re
import time

from . import history, llm, onto, rules
from .db import connect, kv_get, kv_set, now, one, ot, q, rows
from .graph import follow, path
from .onto import cond_sql, label, objects, relations

FNS = ["count", "sum", "avg", "min", "max", "list"]


def _brief() -> str:
    out = []
    for x in objects():
        ps = [p for p in x["props"] if not p["hidden"]]
        cols = ", ".join(p["col"] + (f"({p['label']}" + (f"·{p['desc'][:40]}" if p["desc"] else "") + (f"·동의어 {p['syn']}" if p["syn"] else "") + ")" if p["label"] != p["col"] or p["desc"] or p["syn"] else "") for p in ps[:30])
        ex = mask(x["name"], onto.sample(x["name"], 2), {"role": "현업"})
        ex = [{p["col"]: r.get(p["col"]) for p in ps[:12]} for r in ex]
        out.append(f"- {x['name']}({x['label']}{' · ' + x['desc'][:60] if x.get('desc') else ''}) 키={x['key']} {x['nrows']}줄: {cols}\n  예: {json.dumps(ex, ensure_ascii=False)[:400]}")
    r = "\n".join(f"- {x['a_tbl']}({label(x['a_tbl'])}).{x['a_col']} = {x['b_tbl']}({label(x['b_tbl'])}).{x['b_col']}" for x in relations())
    m = "\n".join(f"- {x['name']}: {x['text']}" for x in rows("SELECT name, text FROM metric ORDER BY id"))
    return f"개체:\n{chr(10).join(out)}\n관계:\n{r or '(없음)'}\n지표(정해 둔 계산):\n{m or '(없음)'}"


def _instr() -> str:
    """에이전트 지시문 — 모든 질문에 늘 적용할 기준(Fabric 데이터 에이전트 지시문처럼)."""
    t = (kv_get("agent_instr", "") or "").strip()
    it = (kv_get("intent", "") or "").strip()
    if it:  # 구축 의도(무엇에 답하려는지)도 늘 함께
        t = f"구축 의도: {it}\n{t}".strip()
    return f"\n에이전트 지시문(모든 질문에 늘 지킬 것 · 위 기본 규칙과 다르면 지시문을 따름. 단 숫자는 결과표 · 모은 값 그대로):\n{t}" if t else ""


def mask(obj: str, rs: list[dict], who: dict | None) -> list[dict]:
    """현업에게는 민감 속성 값을 가림."""
    if not who or who.get("role") != "현업":
        return rs
    sens = {r["col"] for r in rows("SELECT col FROM prop WHERE obj=? AND sensitive=1", (obj,))}
    return [{k: ("●●●" if k in sens and v not in (None, "") else v) for k, v in r.items()} for r in rs] if sens else rs


def mask_text(t: str, who: dict | None) -> str:
    """현업에게는 본문 속 주민등록번호 · 전화번호 모양도 가림."""
    if not who or who.get("role") != "현업":
        return t
    import re
    t = re.sub(r"\b\d{6}-?[1-4]\d{6}\b", "●●●●●●-●●●●●●●", t)
    return re.sub(r"\b01\d-?\d{3,4}-?\d{4}\b", "●●●-●●●●-●●●●", t)


SET_SPEC = ('set이면: {"mode":"set","tpl":"","target":"세거나 나열할 개체","filters":[{"obj":"","col":"","op":"","value":""}],'
            '"group":{"obj":"","col":""} 또는 null,"measure":{"fn":"count|sum|avg|min|max|list","obj":"","col":""},"order":"desc|asc","limit":10,"metric":"쓴 지표 이름 또는 빈 글자","want":""} '
            "— target은 세거나 합치는 대상이다(예: '피보험자별 계약 수' → target=계약, group=피보험자 쪽 이름 열). group은 ~별로 나눌 열(다른 개체 열도 됨, 사람이 읽을 이름 열을 고름). "
            "filters에는 다른 개체 조건도 쓸 수 있다(관계는 프로그램이 따라감). 기간은 날짜 열에 >= <= 조건 두 개로. count면 col은 빈 글자. ")


def plan(question: str) -> dict:
    tpls = rows("SELECT name, plan, params FROM tpl ORDER BY name")
    tlist = "\n".join(f"- {t['name']}: {t['params']}" for t in tpls) or "(없음)"
    d = llm.chat_json(
        "질문을 온톨로지 위에서 답할 계획으로 바꾼다. 개체 · 열 이름은 주어진 그대로(괄호 안은 업무 이름 · 설명 · 동의어). 연산자는 " + " ".join(onto.OPS) + ". "
        "mode는 둘 중 하나: one = 특정 건 하나(질문 속 값으로 찾는 시작 개체)에서 출발해 관계를 따라가는 질문, "
        "set = 여러 건을 세거나 합치거나 순위 · 목록 · ~별로 보는 질문(몇 건, 합계, 평균, 상위 N, 비율). "
        "tpl은 질문 틀 이름 = 무엇을 묻는지 + 시작 개체(값은 뺌, 예: '지급액(청구)', '질병군별 청구 건수(청구)'). 이미 있는 틀과 묻는 뜻이 같으면 그 이름을 그대로 쓴다. "
        'one이면: {"mode":"one","tpl":"","start":{"obj":"","col":"","value":""},"hops":[["가","나"]],"want":"","text":"문서 본문에서 찾아야 할 내용이면 검색어, 아니면 빈 글자"} '
        "— hops는 시작 개체에서부터 차례로 지나갈 개체 짝. 업무상 맞는 길을 고른다. 이번 건에만 해당하는 사실은 그 건에 직접 이어진 개체에서 찾고 "
        "여러 건의 기록을 모은 표(이력 · 통계)로 대신하지 않는다. 지금 관계가 없는 짝이라도 답에 꼭 필요하면 넣는다. 같은 개체를 두 번 지나며 좁혀도 된다. "
        + SET_SPEC + "지표 목록에 같은 뜻이 있으면 metric에 그 이름을 쓴다. "
        '온톨로지로 답할 수 없는 질문이면 {"error":"이유"}',
        f"질문: {question}\n이미 있는 질문 틀:\n{tlist}\n{_brief()}{_instr()}")
    if d.get("error"):
        return d
    d["mode"] = "set" if d.get("mode") == "set" else "one"
    _norm_plan(d)
    if not str(d.get("tpl") or "").strip():  # 틀 이름이 비면 다른 빈 이름 틀과 섞이지 않게 질문으로 이름을 지음
        d["tpl"] = re.sub(r"[A-Za-z]*-?\d[\w-]*", "{값}", question).strip()[:40]
    t = next((x for x in tpls if x["name"] == d.get("tpl") and x["name"]), None)
    if t:  # 같은 틀 → 저장된 길 · 계산을 씀(값만 바꿈)
        p = json.loads(t["plan"])
        if p.get("mode", "one") == "one" and d["mode"] == "one" and (p.get("hops") or not d.get("hops")):  # 저장된 길이 비었는데 새 계획엔 길이 있으면 새 길을 씀(틀도 새로 저장)
            d["start"]["obj"], d["start"]["col"], d["hops"], d["want"] = p["start"]["obj"], p["start"]["col"], p["hops"], p["want"]
            d["text"] = d.get("text") or p.get("text", "")
            d["reused"] = True
        elif p.get("mode") == "set" and d["mode"] == "set":
            newv = {(f.get("obj"), f.get("col"), f.get("op")): f.get("value") for f in d.get("filters", [])}
            for f in p["filters"]:
                f["value"] = newv.get((f["obj"], f["col"], f["op"]), f["value"])
            d.update({k: p[k] for k in ("target", "filters", "group", "measure", "order", "metric", "want") if k in p})
            d["limit"] = d.get("limit") or p.get("limit")
            d["reused"] = True
    _norm_plan(d)
    if not d.get("reused"):
        keep = ({"mode": "one", "start": {"obj": d["start"]["obj"], "col": d["start"]["col"]}, "hops": d.get("hops", []), "want": d["want"], "text": d.get("text", "")}
                if d["mode"] == "one" else {k: d.get(k) for k in ("mode", "target", "filters", "group", "measure", "order", "limit", "metric", "want")})
        params = f"{label(d['start']['obj'])}.{d['start']['col']}" if d["mode"] == "one" else "여러 건 · " + ", ".join(f"{f.get('obj')}.{f.get('col')}" for f in d.get("filters", [])[:3])
        connect().execute("INSERT OR REPLACE INTO tpl VALUES (?,?,?,?)", (d["tpl"], json.dumps(keep, ensure_ascii=False), params, now()))
        d["reused"] = False
    return d


def _norm_plan(d: dict) -> None:
    """라벨로 온 개체 · 열 이름을 실제 이름으로."""
    R, C = onto.resolve, onto.resolve_col
    if d.get("start"):
        d["start"]["obj"] = R(d["start"].get("obj"))
        d["start"]["col"] = C(d["start"]["obj"], d["start"].get("col"))
    raw = [h for h in d.get("hops") or [] if isinstance(h, list) and len(h) == 2]
    names = {o["name"] for o in objects()}
    hops = [[R(a), R(b)] for a, b in raw]
    if hops and any(b not in names for _, b in hops) and all(a in names for a, _ in hops):
        # AI가 [엔터티, 열] 모양으로 줄 때 — 엔터티 순서만 뽑아 [가, 나] 짝으로 다시 만듦
        seq = [d["start"]["obj"]] if d.get("start") else []
        for a, _ in hops:
            if not seq or seq[-1] != a:
                seq.append(a)
        hops = [[x, y] for x, y in zip(seq, seq[1:])]
    d["hops"] = hops
    if d.get("target"):
        d["target"] = R(d["target"])
    for f in d.get("filters") or []:
        f["obj"] = R(f.get("obj"))
        f["col"] = C(f["obj"], f.get("col"))
    for k in ("group", "measure"):
        g = d.get(k)
        if isinstance(g, dict) and g.get("obj"):
            g["obj"] = R(g["obj"])
            g["col"] = C(g["obj"], g.get("col"))


def _compact(got: dict, who=None) -> str:
    out = []
    for t, rs in got.items():
        if rs:
            hid = {r["col"] for r in rows("SELECT col FROM prop WHERE obj=? AND hidden=1", (t,))}
            rs2 = [{k: v for k, v in r.items() if k not in hid} for r in mask(t, rs, who)]
            out.append(f"[{label(t)}] {len(rs)}행" + (" (앞 30행)" if len(rs) > 30 else "") + " " + json.dumps(rs2[:30], ensure_ascii=False)[:4000])
    return "\n".join(out)


# ── 여러 건 계산 ──
def _exists(target: str, obj: str, conds: list[dict]) -> str:
    """대상 줄마다: 관계로 이어진 obj 줄 중 조건이 모두 맞는 줄이 있나(같은 줄에서 함께 맞아야 함)."""
    p = path(target, obj)
    if p is None:
        raise LookupError(obj)
    parts, where = [], []
    for i, (n, m, ac, bc, r) in enumerate(p):
        a = f"e{i}"
        if i == 0:
            parts.append(f"{ot(m)} {a}")
            where.append(f"{a}.{q(bc)} = t0.{q(ac)}")
        else:
            parts.append(f"JOIN {ot(m)} {a} ON {a}.{q(bc)} = e{i - 1}.{q(ac)}")
    last = f"e{len(p) - 1}"
    where += [cond_sql(last, c["col"], c["op"], c["value"]) for c in conds]
    return f"EXISTS (SELECT 1 FROM {' '.join(parts)} WHERE {' AND '.join(where)})"


def run_set(spec: dict, who=None) -> dict:
    """여러 건 계산 → SQL 한 번. 결과 행 · 보낸 SQL · 미연결."""
    objs = {o["name"]: o for o in objects()}
    T = spec.get("target")
    if T not in objs:
        raise ValueError(f"대상 개체 {T}이(가) 온톨로지에 없습니다.")
    key = objs[T]["key"]
    alias, joins, missing = {T: "t0"}, [], []

    def join_to(obj):
        if obj in alias:
            return alias[obj]
        p = path(T, obj)
        if p is None:
            raise LookupError(obj)
        for n, m, ac, bc, r in p:
            if m in alias:
                continue
            a = f"t{len(alias)}"
            alias[m] = a
            joins.append(f"LEFT JOIN {ot(m)} {a} ON {a}.{q(bc)} = {alias[n]}.{q(ac)}")
        return alias[obj]

    where, groups = [], {}
    for f in spec.get("filters") or []:
        if f.get("obj") not in objs or f.get("col") not in objs[f["obj"]]["cols"]:
            raise ValueError(f"조건의 열을 찾을 수 없습니다: {f.get('obj')}.{f.get('col')}")
        if f["obj"] == T:
            where.append(cond_sql("t0", f["col"], f["op"], f["value"]))
        else:
            groups.setdefault(f["obj"], []).append(f)
    for obj, cs in groups.items():
        try:
            where.append(_exists(T, obj, cs))
        except LookupError:
            missing.append([T, obj])
    m = spec.get("measure") or {"fn": "count"}
    fn = m.get("fn") if m.get("fn") in FNS else "count"
    g = spec.get("group") or None
    try:
        ga = join_to(g["obj"]) if g and g.get("obj") else None
        ma = join_to(m["obj"]) if m.get("obj") and m["obj"] != T and fn not in ("count", "list") else "t0"
    except LookupError as e:
        missing.append([T, str(e)])
        ga = ma = None
    if missing:
        return {"missing": missing, "rows": [], "sql": None}
    w = (" WHERE " + " AND ".join(where)) if where else ""
    lim = max(1, min(int(spec.get("limit") or 10), 50))
    order = "ASC" if spec.get("order") == "asc" else "DESC"
    base = f"FROM {ot(T)} t0 {' '.join(joins)}{w}"
    num = lambda a, c: f"CAST(REPLACE({a}.{q(c)}, ',', '') AS REAL)"  # noqa: E731
    if fn == "list":
        o = objs[T]
        show = [p["col"] for p in o["props"] if not p["hidden"]][:8]
        sql = f"SELECT DISTINCT {', '.join('t0.' + q(c) for c in show)} {base} LIMIT {lim}"
        cols = show
    else:
        val = f"COUNT(DISTINCT t0.{q(key)})" if fn == "count" else f"ROUND({fn.upper()}({num(ma, m['col'])}), 2)"
        if ga:
            gk = objs[g["obj"]]["key"]
            # 이름 열로 나눠도 묶는 기준은 키 — 이름이 같은 다른 대상(동명이인)이 합쳐지지 않게
            go = objs[g["obj"]]
            st_ = one(f"SELECT COUNT(*) n, COUNT(DISTINCT {q(g['col'])}) d FROM {ot(g['obj'])}")
            namey = g["col"] != gk and (g["col"] == go.get("title") or st_["d"] >= 0.8 * max(st_["n"], 1))  # 이름처럼 거의 다른 값이면 대상마다
            by = f"{ga}.{q(gk)}, {ga}.{q(g['col'])}" if namey else f"{ga}.{q(g['col'])}"
            sql = f"SELECT {ga}.{q(g['col'])} AS grp, {ga}.{q(gk)} AS gkey, {val} AS val {base} GROUP BY {by} ORDER BY val {order} LIMIT {lim}"
            cols = ["grp", "val"]
        else:
            sql = f"SELECT {val} AS val {base}"
            cols = ["val"]
    rs = [{k: (int(v) if isinstance(v, float) and v.is_integer() else v) for k, v in r.items()} for r in rows(sql)]
    if rs and "gkey" in rs[0]:
        names = [r["grp"] for r in rs]
        for r in rs:
            if names.count(r["grp"]) > 1 and r["grp"] != r["gkey"]:
                r["grp"] = f"{r['grp']} ({r['gkey']})"
            r.pop("gkey")
    total = one(f"SELECT COUNT(DISTINCT t0.{q(key)}) n {base}")["n"]
    return {"rows": mask(T, rs, who) if fn == "list" else rs, "cols": cols, "sql": sql, "total": total, "missing": [], "fn": fn,
            "group": g, "measure": m}


def _plab(obj: str, col: str) -> str:
    r = one("SELECT label FROM prop WHERE obj=? AND col=?", (obj, col))
    return r["label"] if r and r["label"] else col


def _set_text(spec: dict) -> str:
    """계산을 쉬운 말로 — 업무 이름(라벨)으로."""
    m = spec.get("measure") or {}
    fn = {"count": "건수", "sum": "합계", "avg": "평균", "min": "최소", "max": "최대", "list": "목록"}.get(m.get("fn"), "건수")
    conds = [f"{label(f['obj'])} {_plab(f['obj'], f['col'])} {f['op']} {f['value']}" for f in spec.get("filters") or []]
    g = spec.get("group")
    what = f"{_plab(m.get('obj') or spec.get('target'), m['col'])} " if m.get("col") and fn not in ("건수", "목록") else ""
    return (f"{label(spec.get('target'))} {what}{fn}" + (f" · {label(g['obj'])} {_plab(g['obj'], g['col'])}별" if g and g.get("obj") else "")
            + (" · 조건: " + ", ".join(conds) if conds else ""))


def ask(question: str, who: dict | None = None) -> dict:
    t0 = time.time()
    if not objects():
        raise ValueError("온톨로지가 비어 있어 답변할 수 없습니다. 데이터 소스를 연결하고 온톨로지를 설계해 주세요.")
    p = plan(question)
    steps = [{"title": "질문 틀 찾기", "detail": (f"\"{p.get('tpl')}\" ({'저장된 틀 사용' if p.get('reused') else '새 틀'} · {'여러 건 계산' if p.get('mode') == 'set' else '한 건'})" if not p.get("error") else p["error"]),
              "sql": None, "ms": int((time.time() - t0) * 1000)}]
    res = {"q": question, "tpl": p.get("tpl"), "mode": p.get("mode", "one"), "steps": steps, "hot": {"nodes": [], "rels": []}, "missing": [], "who": (who or {}).get("name")}
    if p.get("error"):
        res.update(status="no", answer="답변 불가", detail=p["error"], evidence=[])
        return _save(res)
    if p["mode"] == "set":
        return _ask_set(question, p, res, who)
    st = p["start"]
    if st["obj"] not in {o["name"] for o in objects()}:
        res.update(status="no", answer="답변 불가", detail=f"시작 개체 {st['obj']}이(가) 온톨로지에 없습니다.", evidence=[])
        return _save(res)
    t1 = time.time()
    names = {o["name"] for o in objects()}
    hops = [h for h in p.get("hops", []) if isinstance(h, list) and len(h) == 2 and h[0] in names and h[1] in names]
    g = follow(st["obj"], st["col"], str(st["value"]), hops)
    for s in g["steps"]:
        steps.append({"title": s["title"], "detail": f"{s['n']}행", "sql": s["sql"], "ms": int((time.time() - t1) * 1000)})
    # 본문을 찾는 질문이면, 읽은 값(doc_extract)까지 관계가 없어도 이미 모은 줄의 문서 번호로 본문을 찾을 수 있음 — 그 끊김은 넘어감
    if p.get("text") and any(r.get("doc_id") for rs in g["got"].values() for r in rs):
        g["missing"] = [m for m in g["missing"] if "doc_extract" not in m]
    res["hot"] = {"nodes": [k for k, v in g["got"].items() if v] or [st["obj"]], "rels": g["used"]}
    res["missing"] = [[a, b] for a, b in g["missing"]]
    if not g["got"].get(st["obj"]):
        res.update(status="no", answer="값 없음", detail=f"{label(st['obj'])}.{st['col']} = {st['value']}인 행이 없습니다.", evidence=[])
        return _save(res)
    for a, b in g["missing"]:
        steps.append({"title": f"{label(a)} → {label(b)}", "detail": "미연결 · 이 관계가 온톨로지에 없어 중단", "sql": None, "ms": 0, "broken": True})
    rr = rules.run_for(st["obj"], st["col"], str(st["value"]))
    if rr:
        txt = "; ".join(f"{r['name']}: {'해당 → ' + (r.get('then') or '') if r['hit'] else ('실행 불가 · ' + ', '.join(r.get('why', [])) if r['hit'] is None else '미해당')}" for r in rr)
        steps.append({"title": "규칙 실행 (프로그램)", "detail": txt, "sql": None, "ms": 0})
    res["rules"] = rr
    # 계산 속성이 들어간 값이면 계산 과정(식 · 들어간 값 · 출처 · 예상 여부)을 실행 단계에 붙임
    calc_used = []
    try:
        from . import whatif
        for t, rs_ in g["got"].items():
            cc = whatif.calc_cols(t) if rs_ else []
            if not cc or len(rs_) > 3:
                continue
            kc = next(o for o in objects() if o["name"] == t)["key"]
            for r_ in rs_[:2]:
                its = whatif.mask_items(whatif.explain(t, r_[kc]), who)
                if its:
                    calc_used.append({"obj": t, "obj_label": label(t), "key": r_[kc], "items": its})
    except Exception:
        calc_used = []
    if calc_used:
        steps.append({"title": "계산 속성 (프로그램)", "detail": " · ".join(f"{c['obj_label']} {c['key']}: " + ", ".join(i["label"] for i in c["items"]) for c in calc_used), "sql": None, "ms": 0, "calc": calc_used})
        res["estimated"] = any(i["estimated"] for c in calc_used for i in c["items"])
    if g["missing"]:
        res.update(status="broken", answer="답변 불가", detail="필요한 개체까지 관계가 없어 답변을 중단했습니다. 추측해서 답변하지 않습니다.",
                   evidence=[f"찾은 값: {label(t)} {len(v)}행" for t, v in g["got"].items() if v])
        return _save(res)
    chunks = []
    if p.get("text"):  # 그래프로 거르고(이어진 문서만) 벡터로 고름
        from . import docs
        ids = sorted({str(r["doc_id"]) for rs in g["got"].values() for r in rs if r.get("doc_id")})
        t3 = time.time()
        chunks = [{**c, "text": mask_text(c["text"], who)} for c in docs.search(p["text"], ids or None, k=3)]
        steps.append({"title": "문서 본문 검색", "detail": (f"그래프로 좁힌 문서 {len(ids)}건 안에서" if ids else "이어진 문서가 없어 전체 문서에서") + f" · 조각 {len(chunks)}개 · {docs.search_mode()}",
                      "sql": None, "ms": int((time.time() - t3) * 1000)})
    res["chunks"] = chunks
    t2 = time.time()
    d = llm.chat_json(
        "주어진 값 · 규칙 결과 · 문서 본문 조각만으로 질문에 답한다. 없는 사실은 만들지 않는다. 규칙이 걸렸으면 규칙 결과를 따른다. 걸리지 않은 규칙은 말하지 않는다. "
        "●●●은 가려진 값이니 추측하지 않는다. 금액은 '600만 원'처럼 읽기 쉽게 쓴다. "
        '형식: {"answer":"한 줄 결론(숫자 · 판단)","detail":"한 문장 설명","evidence":["근거 문장(어느 개체의 어떤 값 · 어느 문서 몇 쪽인지)"]}' + _instr(),
        f"질문: {question}\n답해야 할 것: {p.get('want')}\n모은 값:\n{_compact(g['got'], who)}\n"
        f"걸린 규칙: {json.dumps([r for r in rr if r['hit']], ensure_ascii=False)[:2000] or '없음'}\n"
        + ("문서 본문 조각:\n" + "\n".join(f"[{c['doc_id']} {c['page']}쪽] {c['text']}" for c in chunks) if chunks else ""))
    steps.append({"title": "답 쓰기 (LLM 1회)", "detail": "모은 값 · 규칙 결과" + (" · 본문 조각" if chunks else "") + "만 넣음", "sql": None, "ms": int((time.time() - t2) * 1000)})
    res.update(status="ok", answer=d.get("answer", ""), detail=d.get("detail", ""), evidence=d.get("evidence", []))
    return _save(res)


def _ask_set(question: str, p: dict, res: dict, who) -> dict:
    steps = res["steps"]
    if p.get("metric"):
        m = one("SELECT * FROM metric WHERE name=?", (p["metric"],))
        if m:
            ms = json.loads(m["spec"])
            extra = [f for f in p.get("filters") or [] if (f.get("obj"), f.get("col")) not in {(x["obj"], x["col"]) for x in ms.get("filters") or []}]
            p = {**p, **{k: ms.get(k) for k in ("target", "measure")}, "filters": (ms.get("filters") or []) + extra, "group": p.get("group") or ms.get("group")}
            steps.append({"title": f"지표 사용 · {m['name']}", "detail": m["text"], "sql": None, "ms": 0})
    t1 = time.time()
    try:
        r = run_set(p, who)
    except ValueError as e:
        res.update(status="no", answer="답변 불가", detail=str(e), evidence=[])
        return _save(res)
    if r["missing"]:
        res["missing"] = r["missing"]
        for a, b in r["missing"]:
            steps.append({"title": f"{label(a)} → {label(b)}", "detail": "미연결 · 이 관계가 온톨로지에 없어 중단", "sql": None, "ms": 0, "broken": True})
        res.update(status="broken", answer="답변 불가", detail="필요한 개체까지 관계가 없어 답변을 중단했습니다. 추측해서 답변하지 않습니다.", evidence=[])
        return _save(res)
    steps.append({"title": "여러 건 계산 (프로그램)", "detail": f"{_set_text(p)} · 대상 {r['total']}건 · 결과 {len(r['rows'])}행", "sql": r["sql"], "ms": int((time.time() - t1) * 1000)})
    used = {p["target"]} | {f["obj"] for f in p.get("filters") or []} | ({p["group"]["obj"]} if p.get("group") and p["group"].get("obj") else set())
    res["hot"] = {"nodes": sorted(used), "rels": [rel["id"] for rel in relations() if rel["a_tbl"] in used and rel["b_tbl"] in used]}
    res["table"] = {"cols": r["cols"], "rows": r["rows"], "fn": r["fn"], "group": r["group"], "measure": r["measure"], "total": r["total"]}
    res["spec"] = {k: p.get(k) for k in ("target", "filters", "group", "measure", "order", "limit")}
    t2 = time.time()
    d = llm.chat_json(
        "프로그램이 계산한 결과표만으로 질문에 답한다. 숫자는 결과표 값을 쓰고 새로 계산하지 않는다. 없는 사실은 만들지 않는다. "
        "금액은 '5억 2,669만 3,300원'처럼 한국식 단위로, 건수는 '16건'처럼. 순위 질문에서 값이 모두 같으면 같다고 말한다. "
        '형식: {"answer":"한 줄 결론","detail":"한 문장 설명","evidence":["근거 문장"]}' + _instr(),
        f"질문: {question}\n계산: {_set_text(p)}\n조건에 맞는 대상: {r['total']}건\n결과표({', '.join(r['cols'])}):\n{json.dumps(r['rows'], ensure_ascii=False)[:5000]}")
    steps.append({"title": "답 쓰기 (LLM 1회)", "detail": "계산 결과표만 넣음", "sql": None, "ms": int((time.time() - t2) * 1000)})
    ev = [f"계산: {_set_text(p)}"]
    res.update(status="ok", answer=d.get("answer", ""), detail=d.get("detail", ""), evidence=ev)
    return _save(res)


# ── 지표 ──
def metrics() -> list[dict]:
    out = []
    for m in rows("SELECT * FROM metric ORDER BY id"):
        m["spec"] = json.loads(m["spec"])
        m["plain"] = _set_text(m["spec"])
        out.append(m)
    return out


def metric_compile(text: str) -> dict:
    if not text.strip():
        raise ValueError("지표 정의를 입력해 주세요.")
    if not objects():
        raise ValueError("온톨로지 설계에서 개체를 먼저 생성해 주세요.")
    d = llm.chat_json(
        "지표(여러 건 계산) 정의 문장을 계산 JSON으로 바꾼다. 개체 · 열 이름은 주어진 그대로. 연산자는 " + " ".join(onto.OPS) + ". " + SET_SPEC
        + '형식: {"name":"짧은 지표 이름","target":"","filters":[],"group":null,"measure":{"fn":"","obj":"","col":""},"order":"desc","limit":10} 바꿀 수 없으면 {"error":"이유"}',
        f"지표 정의: {text}\n{_brief()}")
    if d.get("error"):
        raise ValueError(d["error"])
    _norm_plan(d)
    r = run_set(d)
    if r["missing"]:
        raise ValueError("관계가 없어 계산할 수 없습니다: " + ", ".join(f"{label(a)} → {label(b)}" for a, b in r["missing"]))
    return {"name": d.get("name") or text[:20], "text": text.strip(), "spec": {k: d.get(k) for k in ("target", "filters", "group", "measure", "order", "limit")},
            "plain": _set_text(d), "preview": {"cols": r["cols"], "rows": r["rows"][:10], "sql": r["sql"], "total": r["total"]}}


def metric_insert(m: dict, by: str) -> int:
    if one("SELECT 1 FROM metric WHERE name=?", (m["name"],)):
        raise ValueError(f"같은 이름의 지표가 있습니다: {m['name']}")
    return connect().execute("INSERT INTO metric (name, text, spec, by, at) VALUES (?,?,?,?,?)",
                             (m["name"], m["text"], json.dumps(m["spec"], ensure_ascii=False), by, now())).lastrowid


def metric_add(m: dict, by="사람") -> int:
    mid = metric_insert(m, by)
    history.record(f"지표 생성 · {m['name']}", "지표", by, {"정의": m["text"], "계산": _set_text(m["spec"])})
    return mid


def metric_remove(mid: int, by="사람") -> None:
    m = one("SELECT * FROM metric WHERE id=?", (mid,))
    if m:
        connect().execute("DELETE FROM metric WHERE id=?", (mid,))
        history.record(f"지표 삭제 · {m['name']}", "지표", by, {"정의": m["text"]})


def metric_run(mid: int, who=None) -> dict:
    m = one("SELECT * FROM metric WHERE id=?", (mid,))
    if not m:
        raise ValueError("지표가 없습니다.")
    r = run_set(json.loads(m["spec"]), who)
    if r["missing"]:
        raise ValueError("관계가 없어 계산할 수 없습니다: " + ", ".join(f"{label(a)} → {label(b)}" for a, b in r["missing"]))
    return {"cols": r["cols"], "rows": r["rows"], "sql": r["sql"], "total": r["total"]}


def _save(res: dict) -> dict:
    res["id"] = connect().execute("INSERT INTO ask (q, tpl, result, at, who) VALUES (?,?,?,?,?)",
                                  (res["q"], res.get("tpl"), json.dumps(res, ensure_ascii=False), now(), res.get("who"))).lastrowid
    return res


def asks(limit: int = 100, who: str | None = None) -> list[dict]:
    out = []
    sql, args = ("SELECT * FROM ask WHERE who=? ORDER BY id DESC LIMIT ?", (who, limit)) if who else ("SELECT * FROM ask ORDER BY id DESC LIMIT ?", (limit,))
    for a in rows(sql, args):
        r = json.loads(a["result"])
        out.append({"id": a["id"], "q": a["q"], "tpl": a["tpl"], "at": a["at"], "status": r.get("status"), "answer": r.get("answer"), "mode": r.get("mode", "one"), "who": a["who"]})
    return out


def ask_detail(aid: int) -> dict | None:
    a = one("SELECT * FROM ask WHERE id=?", (aid,))
    if not a:
        return None
    r = json.loads(a["result"])
    r["same_tpl"] = one("SELECT COUNT(*) n FROM ask WHERE tpl=?", (a["tpl"],))["n"] if a["tpl"] else 0
    return r


# ── 에이전트 설정: 지시문 · 예시 질문(질문 틀) ──
def agent() -> dict:
    out = []
    for t in rows("SELECT name, plan, params, at FROM tpl ORDER BY at DESC"):
        p = json.loads(t["plan"])
        n = one("SELECT COUNT(*) n, MAX(id) last FROM ask WHERE tpl=?", (t["name"],))
        last = one("SELECT q FROM ask WHERE id=?", (n["last"],)) if n["last"] else None
        how = _set_text(p) if p.get("mode") == "set" else " → ".join([label(p["start"]["obj"])] + [label(b) for _, b in p.get("hops", [])]) + (f" · {p.get('want')}" if p.get("want") else "")
        out.append({"name": t["name"], "mode": p.get("mode", "one"), "how": how, "uses": n["n"], "example": last["q"] if last else "", "at": t["at"]})
    return {"instr": kv_get("agent_instr", ""), "templates": out}


def set_instr(text: str, by: str = "사람") -> None:
    if len(text) > 5000:
        raise ValueError("지시문은 5,000자까지 쓸 수 있습니다.")
    kv_set("agent_instr", text.strip())
    history.record("에이전트 지시문 수정", "에이전트", by, {"지시문": text.strip()[:200] or "(비움)"})


def tpl_remove(name: str, by: str = "사람") -> None:
    connect().execute("DELETE FROM tpl WHERE name=?", (name,))
    history.record(f"예시 질문 틀 삭제 · {name}", "에이전트", by, {"틀": name})


# ── 골든 질문 ──
def golden() -> list[dict]:
    return rows("SELECT * FROM golden ORDER BY id")


def golden_add(q: str, want: str, by: str = "사람") -> int:
    if not q.strip() or not want.strip():
        raise ValueError("질문과 정답을 모두 입력해 주세요.")
    gid = connect().execute("INSERT INTO golden (q, want, at) VALUES (?,?,?)", (q.strip(), want.strip(), now())).lastrowid
    history.record("골든 질문 생성", "골든 질문", by, {"q": q, "want": want})
    return gid


def golden_remove(gid: int) -> None:
    connect().execute("DELETE FROM golden WHERE id=?", (gid,))


def golden_vote(gid: int, vote: str) -> None:
    connect().execute("UPDATE golden SET vote=? WHERE id=?", (vote, gid))


def _grade(want: str, got: str) -> str:
    d = llm.chat_json('정답과 시스템 답의 결론(지급 여부 · 금액 · 판단)이 같은지 본다. 숫자 표기 차이(30000000 = 3,000만 원)는 같은 것으로 본다. '
                      '같은 뜻의 다른 말(지급 보류 = 확인 필요 = 바로 지급 불가)도 같은 결론이다. 결론이 같으면 맞음, 결론은 같은데 중요한 이유가 빠졌으면 일부, 다르면 틀림. 형식: {"ok":"맞음|일부|틀림"}', f"정답: {want}\n시스템 답: {got}")
    return d.get("ok", "틀림")


def golden_run() -> dict:
    out = []
    for g in golden():
        try:
            r = ask(g["q"])
            got = r["answer"] + (f" — {r['detail']}" if r.get("detail") else "")
            ok = _grade(g["want"], got) if r["status"] == "ok" else "틀림"
            connect().execute("UPDATE golden SET got=?, ok=?, ask_id=?, run_at=?, vote=NULL WHERE id=?", (got, ok, r["id"], now(), g["id"]))
        except Exception as e:
            connect().execute("UPDATE golden SET got=?, ok='틀림', run_at=? WHERE id=?", (f"오류: {str(e)[:120]}", now(), g["id"]))
        out.append(g["id"])
    gs = golden()
    return {"total": len(gs), "pass": sum(g["ok"] == "맞음" for g in gs)}
