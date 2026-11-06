"""온톨로지 — 개체 · 속성 · 관계. 구축 의도.

개체 정의 층: 개체 = 원본 표 + 조건(한 표에서 여러 개체) + 계산 속성 → "o:<개체>" 뷰. 표 이름과 개체를 떼어 놓음.
속성마다 업무 이름 · 타입 · 설명 · 동의어 · 숨김 · 민감을 둠 → 질문 · 규칙 AI가 열 이름 대신 이 뜻을 봄.
AI 설계: LLM이 표 · 열 · 예시 값을 보고 개체 이름과 관계 초안을 냄(LLM이 없으면 "열 이름이 다른 표의 키와 같으면 잇기").
관계마다 "값 겹침"과 1:1 · 1:N · N:M을 프로그램이 직접 세서 보여 줌 — 근거 없는 관계를 거르려고.
같은 대상 묶기(개체 해소): 여러 열을 견줘 같은 대상 짝을 찾고, 확정한 짝은 매핑 표(개체)로 저장해 관계로 이음.
"""
import difflib
import json
import re

from . import naming, history, llm, sources
from .db import clean_name, connect, dt, kv_get, kv_set, now, one, ot, q, rows

OPS = ["=", "!=", "<", "<=", ">", ">=", "포함", "안 포함"]
TYPES = ["글자", "숫자", "날짜"]


# ── 개체 뷰 ──
def lit(v) -> str:
    return "'" + str(v).replace("'", "''") + "'"


def _isnum(v) -> bool:
    return bool(re.fullmatch(r"-?\d+(\.\d+)?", str(v).replace(",", "").strip()))


def cond_sql(alias: str, col: str, op: str, val) -> str:
    """조건 하나 → SQL 조각(값은 글자로 박아 넣음 — 뷰에는 ?를 못 씀)."""
    c = f"{alias}.{q(col)}" if alias else q(col)
    if op not in OPS:
        raise ValueError(f"모르는 연산자입니다: {op}")
    if op in ("포함", "안 포함"):
        return f"{c} {'NOT ' if op == '안 포함' else ''}LIKE {lit('%' + str(val) + '%')}"
    if _isnum(val) and op not in ("=", "!="):
        return f"CAST(REPLACE({c}, ',', '') AS REAL) {op} {str(val).replace(',', '')}"
    return f"{c} {'<>' if op == '!=' else op} {lit(val)}"


def _rel_between(a: str, b: str):
    for r in relations():
        if r["a_tbl"] == a and r["b_tbl"] == b:
            return r["a_col"], r["b_col"]
        if r["b_tbl"] == a and r["a_tbl"] == b:
            return r["b_col"], r["a_col"]
    return None


def _src(name: str) -> tuple[str, str]:
    """다른 개체를 계산에 쓸 때: (원본 표 SQL, 그 개체의 조건 SQL) — 계산 속성끼리 서로 물지 않게 원본 표를 씀."""
    o = one("SELECT * FROM obj WHERE name=?", (name,))
    if not o:
        raise ValueError(f"개체 {name}이(가) 없습니다.")
    flt = " AND ".join(cond_sql("x", f["col"], f["op"], f["value"]) for f in json.loads(o["filter"] or "[]"))
    return dt(o["base"] or name), flt


def calc_sql(name: str, spec: dict) -> tuple[str, str]:
    """계산 속성 → (층, SQL). 층 inner = 원본 줄(b)에서 계산, outer = 같은 줄의 다른 칸(계산 포함)으로 계산."""
    k = spec.get("kind")
    if k in ("lookup", "agg"):
        other = spec["obj"]
        lk = _rel_between(name, other)
        if not lk:
            raise ValueError(f"{label(name)}과(와) {label(other)} 사이에 관계가 없어 계산할 수 없습니다.")
        src, flt = _src(other)
        where = [f"x.{q(lk[1])} = b.{q(lk[0])}"] + ([flt] if flt else [])
        where += [cond_sql("x", w["col"], w["op"], w["value"]) for w in spec.get("where", [])]
        w = " AND ".join(where)
        if k == "lookup":
            return "inner", f"(SELECT x.{q(spec['col'])} FROM {src} x WHERE {w} LIMIT 1)"
        fn = spec.get("fn", "count")
        if fn == "count":
            return "inner", f"(SELECT COUNT(*) FROM {src} x WHERE {w})"
        if fn not in ("sum", "avg", "min", "max"):
            raise ValueError(f"모르는 집계입니다: {fn}")
        return "inner", f"(SELECT {fn.upper()}(CAST(REPLACE(x.{q(spec['col'])}, ',', '') AS REAL)) FROM {src} x WHERE {w})"
    if k == "expr":
        e = str(spec.get("sql", ""))
        if re.search(r";|--|\b(select|insert|update|delete|drop|attach|pragma|create|alter)\b", e, re.I):
            raise ValueError("계산식에 쓸 수 없는 말이 있습니다.")
        return "outer", f"({e})"
    raise ValueError("계산 종류를 알 수 없습니다.")


def build_view(name: str, extra: tuple[str, dict] | None = None) -> str:
    """개체 뷰 SQL. extra = (열 이름, 계산) — 미리 보기용으로 하나 더 붙여 봄."""
    o = one("SELECT * FROM obj WHERE name=?", (name,))
    base = o["base"] or name
    inner, outer = ["b.*"], []
    calcs = [(p["col"], json.loads(p["calc"])) for p in rows("SELECT col, calc FROM prop WHERE obj=? AND calc IS NOT NULL ORDER BY ord", (name,))]
    if extra:
        calcs.append(extra)
    for col, spec in calcs:
        lay, sql = calc_sql(name, spec)
        (inner if lay == "inner" else outer).append(f"{sql} AS {q(col)}")
    flt = json.loads(o["filter"] or "[]")
    where = " AND ".join(cond_sql("b", f["col"], f["op"], f["value"]) for f in flt)
    sql = f"SELECT {', '.join(inner)} FROM {dt(base)} b" + (f" WHERE {where}" if where else "")
    return f"SELECT i.*{''.join(', ' + x for x in outer)} FROM ({sql}) i"


def rebuild(name: str | None = None) -> None:
    """개체 뷰 다시 만들기(이름이 없으면 모두). 깨진 계산이 있으면 그 계산만 빼고 만듦."""
    con = connect()
    names = [name] if name else [r["name"] for r in rows("SELECT name FROM obj")]
    if not name:
        have = {r["name"] for r in rows("SELECT name FROM sqlite_master WHERE type='view' AND name LIKE 'o:%'")}
        for v in have - {"o:" + n for n in names}:
            con.execute(f"DROP VIEW IF EXISTS {q(v)}")
    for n in names:
        con.execute(f"DROP VIEW IF EXISTS {ot(n)}")
        o = one("SELECT base FROM obj WHERE name=?", (n,))
        if not o or not sources.table(o["base"] or n):
            continue
        try:
            con.execute(f"CREATE VIEW {ot(n)} AS {build_view(n)}")
            con.execute(f"SELECT * FROM {ot(n)} LIMIT 1").fetchall()
        except Exception:
            con.execute(f"DROP VIEW IF EXISTS {ot(n)}")
            o2 = one("SELECT * FROM obj WHERE name=?", (n,))
            con.execute(f"CREATE VIEW {ot(n)} AS SELECT * FROM {dt(o2['base'] or n)}")


def _view_cols(name: str) -> list[str]:
    try:
        cur = connect().execute(f"SELECT * FROM {ot(name)} LIMIT 0")
        return [d[0] for d in cur.description]
    except Exception:
        return []


def props(name: str) -> list[dict]:
    o = one("SELECT * FROM obj WHERE name=?", (name,))
    t = sources.table(o["base"] or name) if o else None
    btype = dict(zip(t["cols"], t["types"])) if t else {}
    meta = {p["col"]: p for p in rows("SELECT * FROM prop WHERE obj=?", (name,))}
    out = []
    for c in _view_cols(name):
        m = meta.get(c, {})
        calc = json.loads(m["calc"]) if m.get("calc") else None
        ty = m.get("type") or ("숫자" if calc and calc.get("kind") == "agg" else btype.get(c, "글자"))
        named = bool(m.get("label")) and m.get("label") != c
        # 업무 이름이 없으면 설명 · 동의어 · 사전으로 만든 한글 이름(영어 칸 이름을 화면에 그대로 내지 않음)
        out.append({"col": c, "label": m.get("label") if named else naming.plain(c, "", m.get("desc") or "", m.get("syn") or ""), "named": named, "type": ty,
                    "desc": m.get("desc") or "", "syn": m.get("syn") or "", "hidden": bool(m.get("hidden")), "sensitive": bool(m.get("sensitive")),
                    "calc": calc, "text": (calc or {}).get("text", "")})
    return out


def objects() -> list[dict]:
    out = []
    for o in rows("SELECT * FROM obj ORDER BY name"):
        base = o["base"] or o["name"]
        t = sources.table(base)
        if not t:
            continue
        ps = props(o["name"])
        if not ps:
            rebuild(o["name"])
            ps = props(o["name"])
        try:
            n = one(f"SELECT COUNT(*) n FROM {ot(o['name'])}")["n"]
        except Exception:
            n = t["nrows"]
        out.append({**o, "label": _olabel(o), "base": base, "filter": json.loads(o["filter"] or "[]"), "cols": [p["col"] for p in ps], "types": [p["type"] for p in ps],
                    "props": ps, "nrows": n, "source_id": t["source_id"], "derived": base != o["name"]})
    return out


def resolve(x) -> str | None:
    """개체 이름 또는 업무 이름(라벨) → 개체 이름. LLM이 라벨로 답할 때가 있어서."""
    if not x:
        return x
    cands = [str(x).strip()] + [t.strip() for t in re.split(r"[()]", str(x)) if t.strip()]  # "paid_history(지급이력)"도 받음
    for c in cands:
        for o in rows("SELECT name, label FROM obj"):
            if c in (o["name"], o["label"]) or c.lower() == o["name"].lower():
                return o["name"]
    return x


def resolve_col(obj: str, c):
    """열 이름 또는 속성 업무 이름 → 열 이름."""
    if not c or not obj:
        return c
    cols = _view_cols(obj)
    if c in cols:
        return c
    for t in [t.strip() for t in re.split(r"[()]", str(c)) if t.strip()]:
        if t in cols:
            return t
    for p in rows("SELECT col, label FROM prop WHERE obj=?", (obj,)):
        if c == p["label"]:
            return p["col"]
    return c


def relations() -> list[dict]:
    return rows("SELECT * FROM rel ORDER BY id")


def _olabel(o: dict) -> str:
    """엔터티 형식 이름 — 사람 · AI가 붙인 한글 이름, 없으면(테이블 이름 그대로면) 사전으로 옮긴 이름."""
    lab = o.get("label") or o["name"]
    return naming.plain(o["name"]) if lab == o["name"] and re.fullmatch(r"[a-z0-9_]+", lab) else lab


def label(name: str) -> str:
    o = one("SELECT name, label FROM obj WHERE name=?", (name,))
    return _olabel(o) if o else name


def sample(name: str, n: int = 5) -> list[dict]:
    return rows(f"SELECT * FROM {ot(name)} LIMIT {int(n)}")


def overlap(a_tbl, a_col, b_tbl, b_col) -> dict:
    try:
        a = {r["v"] for r in rows(f"SELECT DISTINCT {q(a_col)} v FROM {ot(a_tbl)} WHERE {q(a_col)}<>''")}
        b = {r["v"] for r in rows(f"SELECT DISTINCT {q(b_col)} v FROM {ot(b_tbl)} WHERE {q(b_col)}<>''")}
    except Exception:
        return {"a": 0, "hit": 0}
    return {"a": len(a), "hit": len(a & b), "b": len(b)}


def _uniq(obj: str, col: str) -> bool:
    try:
        r = one(f"SELECT COUNT(*) n, COUNT(DISTINCT {q(col)}) d FROM {ot(obj)} WHERE {q(col)}<>''")
        return r["n"] == r["d"]
    except Exception:
        return False


def cardinality(r: dict) -> str:
    """관계 짝 수 — 앞이 하나면 1, 여럿이면 N. (앞 열 값이 겹치지 않으면 앞 쪽 한 줄이 뒤 쪽 한 줄과만 이어짐)"""
    a1, b1 = _uniq(r["a_tbl"], r["a_col"]), _uniq(r["b_tbl"], r["b_col"])
    return {(True, True): "1:1", (False, True): "N:1", (True, False): "1:N"}.get((a1, b1), "N:M")


def key_check(name: str, col: str) -> dict:
    """키 점검 — 값이 겹치거나 빈 줄이 있으면 키로 쓸 때 다른 줄이 한 개체로 합쳐짐."""
    r = one(f"SELECT COUNT(*) n, COUNT(DISTINCT {q(col)}) d, SUM({q(col)}='' OR {q(col)} IS NULL) e FROM {ot(name)}")
    dups = rows(f"SELECT {q(col)} v, COUNT(*) c FROM {ot(name)} WHERE {q(col)}<>'' GROUP BY {q(col)} HAVING c>1 ORDER BY c DESC LIMIT 5")
    ok = not dups and not r["e"]
    out = {"rows": r["n"], "distinct": r["d"], "empty": r["e"] or 0, "dups": dups, "ok": ok}
    if not ok:  # 고칠 방법 — 값이 모두 다른 열 하나, 없으면 두 열을 합쳐 다른 짝
        cols = [p["col"] for p in props(name) if not p["calc"]]
        uniq = lambda expr: (lambda x: x["n"] == x["d"] and not x["e"])(one(f"SELECT COUNT(*) n, COUNT(DISTINCT {expr}) d, SUM(({expr}) IS NULL OR ({expr})='') e FROM {ot(name)}"))
        out["single"] = [c for c in cols if c != col and uniq(q(c))][:3]
        out["pair"] = [] if out["single"] else [[a, b] for i, a in enumerate(cols) for b in cols[i + 1:] if uniq(f"{q(a)} || '-' || {q(b)}")][:3]
    return out


def compound_key(name: str, cols: list[str], by="사람") -> str:
    """두 열을 합친 키 — 계산 속성(가-나)을 만들어 키로 씀(Fabric 복합 키처럼)."""
    have = {p["col"] for p in props(name) if not p["calc"]}
    if len(cols) != 2 or not set(cols) <= have:
        raise ValueError("합칠 열 두 개를 골라 주세요.")
    col = clean_name("key_" + "_".join(cols))
    lab = " + ".join(next((p["label"] for p in props(name) if p["col"] == c), c) for c in cols)
    if col not in _view_cols(name):
        _insert_calc(name, col, f"{lab} 키", {"kind": "expr", "sql": f'"{cols[0]}" || \'-\' || "{cols[1]}"', "text": f"{lab}을 이어 붙인 키", "plain": f"{lab}을 '-'로 이어 붙임"})
    if not key_check(name, col)["ok"]:
        raise ValueError("합쳐도 값이 겹쳐 키로 쓸 수 없습니다.")
    connect().execute("UPDATE obj SET key=? WHERE name=?", (col, name))
    history.record(f"키 변경 · {label(name)} → {lab} 합친 키", "개체 · 관계", by, {"키": col})
    return col


def view() -> dict:
    objs = objects()
    for o in objs:
        try:
            o["key_ok"] = key_check(o["name"], o["key"])["ok"]
        except Exception:
            o["key_ok"] = False
    names = {o["name"] for o in objs}
    rels = []
    for r in relations():
        if r["a_tbl"] in names and r["b_tbl"] in names:
            rels.append({**r, "ov": overlap(r["a_tbl"], r["a_col"], r["b_tbl"], r["b_col"]), "card": cardinality(r)})
    pend = [json.loads(c["op"]) for c in rows("SELECT op FROM change WHERE status='pending'")]
    prel = [o for o in pend if o.get("type") == "add_rel"]
    bases = {o["base"] for o in objs}
    loose = [t for t in sources.table_names() if t not in names and t not in bases]
    return {"objects": objs, "relations": rels, "pending_rel": prel, "loose_tables": loose, "intent": kv_get("intent", "")}


# ── 바꾸기 ──
def _valid(a_tbl, a_col, b_tbl, b_col) -> None:
    for t, c in ((a_tbl, a_col), (b_tbl, b_col)):
        if c not in _view_cols(t):
            raise ValueError(f"{t}.{c} 열이 없습니다.")


def _add_rel(r: dict, by: str) -> int:
    _valid(r["a_tbl"], r["a_col"], r["b_tbl"], r["b_col"])
    for x in relations():
        if {(x["a_tbl"], x["a_col"]), (x["b_tbl"], x["b_col"])} == {(r["a_tbl"], r["a_col"]), (r["b_tbl"], r["b_col"])}:
            return x["id"]
    return connect().execute("INSERT INTO rel (name, a_tbl, a_col, b_tbl, b_col, by, at) VALUES (?,?,?,?,?,?,?)",
                              (r.get("name") or label(r["b_tbl"]), r["a_tbl"], r["a_col"], r["b_tbl"], r["b_col"], by, now())).lastrowid


def apply_op(op: dict) -> None:
    """승인된 변경을 실제로 적용."""
    t = op["type"]
    if t == "add_rel":
        _add_rel(op["rel"], "사람 승인")
    elif t == "remove_rel":
        connect().execute("DELETE FROM rel WHERE id=?", (op["id"],))
    elif t == "restore":
        history.restore(op["snap"])
    elif t == "add_rule":
        from . import rules
        rules.insert(op["rule"])
    elif t == "add_field":
        from . import docs
        docs.insert_field(op["field"])
    elif t == "set_intent":
        kv_set("intent", op["text"])
    elif t == "add_calc":
        _insert_calc(op["obj"], op["col"], op["label"], op["calc"])
    elif t == "add_metric":
        from . import qa
        qa.metric_insert(op["metric"], "사람 승인")
    else:
        raise ValueError(f"모르는 변경 종류: {t}")


def add_relation(a_tbl, a_col, b_tbl, b_col, name="", by="사람") -> dict:
    rid = _add_rel({"a_tbl": a_tbl, "a_col": a_col, "b_tbl": b_tbl, "b_col": b_col, "name": name}, by)
    history.record(f"관계 추가 · {label(a_tbl)} → {label(b_tbl)}", "개체 · 관계", by, {"add": f"{a_tbl}.{a_col} → {b_tbl}.{b_col}"})
    return {"id": rid}


def remove_relation(rid: int) -> None:
    r = one("SELECT * FROM rel WHERE id=?", (rid,))
    if r:
        connect().execute("DELETE FROM rel WHERE id=?", (rid,))
        history.record(f"관계 삭제 · {label(r['a_tbl'])} → {label(r['b_tbl'])}", "개체 · 관계", "사람",
                       {"remove": f"{r['a_tbl']}.{r['a_col']} → {r['b_tbl']}.{r['b_col']}"})


def set_label(name: str, lab: str, by="사람") -> None:
    connect().execute("UPDATE obj SET label=? WHERE name=?", (lab, name))
    history.record(f"개체 이름 · {name} → {lab}", "개체 · 관계", by, {"label": [name, lab]})


def set_intent(text: str, by="사람") -> None:
    kv_set("intent", text)
    history.record("구축 의도 수정", "구축 의도", by, {"intent": text})


# ── AI 설계 ──
def _tables_brief(names: list[str]) -> str:
    out = []
    for n in names:
        t = sources.table(n)
        ex = sources.sample(n, 3)
        cols = ", ".join(f"{c}({ty})" for c, ty in zip(t["cols"], t["types"]))
        out.append(f"- {n} ({t['nrows']}행): {cols}\n  예: {json.dumps(ex, ensure_ascii=False)[:600]}")
    return "\n".join(out)


def candidates(names: list[str], top: int = 60) -> list[dict]:
    """값이 겹치는 열 짝 — 가 열의 값 80% 이상이 나 열에 있고, 나 열이 거의 키(값이 안 겹침)인 것. AI에게 힌트로 줌."""
    vals, keyish = {}, {}
    for n in names:
        t = sources.table(n)
        for c in t["cols"]:
            v = [r["v"] for r in rows(f"SELECT {q(c)} v FROM {dt(n)} WHERE {q(c)}<>''")]
            sv = set(v)
            if not sv or len(sv) > 5000 or max(len(x) for x in sv) > 60:
                continue
            vals[(n, c)] = sv
            keyish[(n, c)] = len(sv) >= 0.9 * max(len(v), 1)
    out = []
    for (a, ac), A in vals.items():
        for (b, bc), B in vals.items():
            if a == b or not keyish[(b, bc)] or len(A) < 2:
                continue
            hit = len(A & B)
            if hit >= max(2, 0.8 * len(A)):
                out.append({"a_tbl": a, "a_col": ac, "b_tbl": b, "b_col": bc, "hit": hit, "a": len(A)})
    out.sort(key=lambda x: (-(x["hit"] / x["a"]), -x["hit"]))
    return out[:top]


def _fallback(names: list[str]) -> dict:
    cols = {n: sources.table(n)["cols"] for n in names}
    keys = {}
    for n in names:
        k = cols[n][0]
        if k not in keys or k == f"{n}_id" or k == n:
            keys[k] = n
    rels = []
    for n in names:
        for c in cols[n]:
            t = keys.get(c)
            if t and t != n:
                rels.append({"a_tbl": n, "a_col": c, "b_tbl": t, "b_col": c, "name": t})
    return {"objects": [{"table": n, "label": n, "key": cols[n][0]} for n in names], "relations": rels}


def draft(instruction: str = "", tables: list[str] | None = None) -> dict:
    """tables를 주면 그 표만 개체로 씀(고르지 않은 표는 개체에서 빠짐)."""
    names = sources.table_names()
    if tables:
        names = [n for n in names if n in set(tables)]
    if not names:
        raise ValueError("데이터 소스에서 표를 먼저 가져와 주세요." if not tables else "개체로 쓸 표를 하나 이상 골라 주세요.")
    by = "AI"
    if llm.available():
        sysm = ("너는 온톨로지 설계자다. 회사 표들을 보고 개체(표 하나 = 개체 하나)의 한국어 이름과 키 열, 그리고 표 사이 관계를 JSON으로 낸다. "
                "관계는 한 표의 열 값이 다른 표의 열 값과 같은 것을 가리킬 때만 만든다. 열 이름은 반드시 주어진 그대로 쓴다. "
                '형식: {"objects":[{"table":"","label":"","key":""}],"relations":[{"a_tbl":"","a_col":"","b_tbl":"","b_col":"","name":"관계 이름(한국어, 짧게)"}],"intent":"이 데이터로 무엇을 하려는지 한 문장"}')
        cand = "\n".join(f"- {c['a_tbl']}.{c['a_col']} → {c['b_tbl']}.{c['b_col']} (값 {c['hit']}/{c['a']}개 겹침)" for c in candidates(names))
        user = (f"지시: {instruction or '이 표들로 온톨로지를 설계해 줘'}\n"
                f"구축 의도: {kv_get('intent', '') or '(아직 없음)'}\n표:\n{_tables_brief(names)}\n"
                f"프로그램이 센 값 겹침 후보(뜻이 맞는 것만 관계로 써라):\n{cand or '(없음)'}")
        try:
            d = llm.chat_json(sysm, user, timeout=180)
        except Exception as e:
            d, by = _fallback(names), f"규칙 (LLM 실패: {str(e)[:60]})"
    else:
        d, by = _fallback(names), "규칙 (LLM 없음)"
    con = connect()
    # 사람이 만든 개체(조건 · 매핑 표 · 판정 결과)는 남기고 AI · 규칙이 만든 표 개체만 다시 만듦
    keep = {o["name"] for o in rows("SELECT name FROM obj WHERE (base IS NOT NULL AND base<>name) OR (by NOT LIKE 'AI%' AND by NOT LIKE '규칙 (%' AND by<>'시스템')")}
    for n in [o["name"] for o in rows("SELECT name FROM obj")]:
        if n not in keep:
            con.execute("DELETE FROM obj WHERE name=?", (n,))
    for r in relations():
        if r["a_tbl"] not in keep and r["b_tbl"] not in keep:
            con.execute("DELETE FROM rel WHERE id=?", (r["id"],))
    for o in d.get("objects", []):
        if o.get("table") in names and o["table"] not in keep:
            t = sources.table(o["table"])
            key = o.get("key") if o.get("key") in t["cols"] else t["cols"][0]
            con.execute("INSERT OR REPLACE INTO obj (name, label, key, by, at, base) VALUES (?,?,?,?,?,?)", (o["table"], o.get("label") or o["table"], key, by, now(), o["table"]))
    for n in names:  # 빠진 표도 개체로
        if not one("SELECT 1 FROM obj WHERE name=? OR (base=? AND filter IS NULL)", (n, n)):
            con.execute("INSERT INTO obj (name, label, key, by, at, base) VALUES (?,?,?,?,?,?)", (n, n, sources.table(n)["cols"][0], by, now(), n))
    con.execute("DELETE FROM prop WHERE obj NOT IN (SELECT name FROM obj)")
    rebuild()
    made, bad = 0, []
    for r in d.get("relations", []):
        try:
            _add_rel(r, by)
            made += 1
        except Exception:
            bad.append(r)
    if d.get("intent") and not kv_get("intent"):
        kv_set("intent", d["intent"])
    history.record(f"AI 설계 초안 · 개체 {len(names)}개 · 관계 {made}개", "개체 · 관계", by, {"objects": len(names), "relations": made, "dropped": bad})
    return {"objects": len(names), "relations": made, "dropped": len(bad), "by": by}


def suggest_relation(text: str) -> dict:
    """Copilot: "가와 나를 이어 줘" → 열 고르기 + 값 겹침 근거. 적용은 승인 후."""
    v = view()

    def ex(o, c):
        return "/".join(str(r["v"]) for r in rows(f"SELECT DISTINCT {q(c)} v FROM {ot(o)} WHERE {q(c)}<>'' LIMIT 3"))[:60]
    brief = "\n".join(f"- {o['name']}({o['label']}): " + ", ".join(f"{c}[{ex(o['name'], c)}]" for c in o["cols"]) for o in v["objects"])
    have = "\n".join(f"- {r['a_tbl']}.{r['a_col']} = {r['b_tbl']}.{r['b_col']}" for r in v["relations"])
    d = llm.chat_json(
        '사용자가 이으라고 한 두 개체 사이의 새 관계를 고른다. 개체는 한국어 이름 · 표 이름 · 뜻(동의어 포함, 예: 담보=보장)으로 찾는다. '
        '이미 있는 관계는 다시 고르지 않는다. 열 이름은 주어진 그대로. [] 안은 값 예시. 형식: {"a_tbl":"","a_col":"","b_tbl":"","b_col":"","name":"","why":"한 문장"} '
        '고를 수 없으면 {"error":"이유"}', f"요청: {text}\n개체:\n{brief}\n이미 있는 관계:\n{have or '(없음)'}")
    if d.get("error"):
        raise ValueError(d["error"])
    _valid(d["a_tbl"], d["a_col"], d["b_tbl"], d["b_col"])
    for x in v["relations"]:
        if {(x["a_tbl"], x["a_col"]), (x["b_tbl"], x["b_col"])} == {(d["a_tbl"], d["a_col"]), (d["b_tbl"], d["b_col"])}:
            raise ValueError(f"이미 있는 관계입니다: {d['a_tbl']}.{d['a_col']} = {d['b_tbl']}.{d['b_col']}")
    d["ov"] = overlap(d["a_tbl"], d["a_col"], d["b_tbl"], d["b_col"])
    d["a_label"], d["b_label"] = label(d["a_tbl"]), label(d["b_tbl"])
    return d


def draft_intent() -> str:
    names = sources.table_names()
    if not names or not llm.available():
        raise ValueError("표를 가져오고 LLM을 연결해야 초안을 생성할 수 있습니다.")
    d = llm.chat_json('표들을 보고 이 데이터로 무엇을 하려는지 구축 의도를 한국어 한두 문장으로. 형식: {"intent":""}', _tables_brief(names))
    return d.get("intent", "")


# ── 개체 정의 층: 개체 · 속성 · 계산 속성 ──
def add_object(label_: str, base: str, flt: list[dict], key: str = "", by="사람") -> dict:
    """원본 표에서 조건으로 개체 하나를 떼어 냄(예: 문서 표 중 진단서만 → 진단서 개체)."""
    t = sources.table(base)
    if not label_.strip():
        raise ValueError("개체 이름을 입력해 주세요.")
    if not t:
        raise ValueError("원본 표를 선택해 주세요.")
    for f in flt:
        if f.get("col") not in t["cols"] or f.get("op") not in OPS:
            raise ValueError("조건의 열 · 연산자를 확인해 주세요.")
    name, i = clean_name(label_), 2
    while one("SELECT 1 FROM obj WHERE name=?", (name,)) or (sources.table(name) and name != base):
        name, i = f"{clean_name(label_)}_{i}", i + 1
    key = key if key in t["cols"] else t["cols"][0]
    connect().execute("INSERT INTO obj (name, label, key, by, at, base, filter) VALUES (?,?,?,?,?,?,?)",
                      (name, label_.strip(), key, by, now(), base, json.dumps(flt, ensure_ascii=False)))
    rebuild(name)
    n = one(f"SELECT COUNT(*) n FROM {ot(name)}")["n"]
    history.record(f"개체 생성 · {label_.strip()}", "개체 · 관계", by,
                   {"원본 표": base, "조건": " AND ".join(f"{f['col']} {f['op']} {f['value']}" for f in flt) or "없음", "행": n})
    return {"name": name, "nrows": n}


def remove_object(name: str, by="사람") -> None:
    o = one("SELECT * FROM obj WHERE name=?", (name,))
    if not o:
        return
    con = connect()
    con.execute("DELETE FROM obj WHERE name=?", (name,))
    con.execute("DELETE FROM prop WHERE obj=?", (name,))
    con.execute("DELETE FROM rel WHERE a_tbl=? OR b_tbl=?", (name, name))
    con.execute(f"DROP VIEW IF EXISTS {ot(name)}")
    history.record(f"개체 삭제 · {o['label']}", "개체 · 관계", by, {"개체": o["label"]})


def save_def(name: str, d: dict, by="사람") -> None:
    """개체 정의 저장 — 이름 · 설명 · 키 · 표시 속성 · 속성마다 업무 이름 · 타입 · 설명 · 동의어 · 숨김 · 민감."""
    o = one("SELECT * FROM obj WHERE name=?", (name,))
    if not o:
        raise ValueError("개체가 없습니다.")
    cols = _view_cols(name)
    key = d.get("key") if d.get("key") in cols else o["key"]
    title = d.get("title") if d.get("title") in cols else None
    con = connect()
    con.execute("UPDATE obj SET label=?, desc=?, key=?, title=? WHERE name=?", ((d.get("label") or o["label"]).strip(), d.get("desc", ""), key, title, name))
    changed = []
    for i, p in enumerate(d.get("props", [])):
        if p.get("col") not in cols:
            continue
        old = one("SELECT * FROM prop WHERE obj=? AND col=?", (name, p["col"])) or {}
        ty = p.get("type") if p.get("type") in TYPES else None
        vals = (p.get("label") or p["col"], ty, p.get("desc", ""), p.get("syn", ""), int(bool(p.get("hidden"))), int(bool(p.get("sensitive"))))
        if tuple(old.get(k) for k in ("label", "type", "desc", "syn", "hidden", "sensitive")) != vals:
            changed.append(p.get("label") or p["col"])
        con.execute("INSERT INTO prop (obj, col, label, type, desc, syn, hidden, sensitive, calc, ord) VALUES (?,?,?,?,?,?,?,?,?,?) "
                    "ON CONFLICT(obj, col) DO UPDATE SET label=excluded.label, type=excluded.type, desc=excluded.desc, syn=excluded.syn, "
                    "hidden=excluded.hidden, sensitive=excluded.sensitive", (name, p["col"], *vals, old.get("calc"), old.get("ord") or 100 + i))
    diff = {"개체": d.get("label") or o["label"], "키": key, "표시 속성": title or "-"}
    if changed:
        diff["속성"] = ", ".join(changed[:8]) + (f" 외 {len(changed) - 8}개" if len(changed) > 8 else "")
    history.record(f"개체 정의 수정 · {d.get('label') or o['label']}", "개체 · 관계", by, diff)


def calc_compile(name: str, text: str) -> dict:
    """계산 속성 문장 → 계산 정의(JSON). 판단은 프로그램이 SQL로 함."""
    if not text.strip():
        raise ValueError("계산 내용을 입력해 주세요.")
    me = next((o for o in objects() if o["name"] == name), None)
    if not me:
        raise ValueError("개체가 없습니다.")
    near = []
    for r in relations():
        other = r["b_tbl"] if r["a_tbl"] == name else r["a_tbl"] if r["b_tbl"] == name else None
        if other:
            src, _ = _src(other)
            ob = next((o for o in objects() if o["name"] == other), None)
            if ob:
                near.append(f"- {other}({ob['label']}): " + ", ".join(f"{p['col']}({p['label']}·{p['type']})" for p in ob["props"] if not p["calc"]))
    mine = ", ".join(f"{p['col']}({p['label']}·{p['type']})" for p in me["props"])
    d = llm.chat_json(
        "개체에 붙일 계산 속성 하나를 정의한다. 종류는 셋 중 하나. "
        'expr = 이 개체 같은 줄의 열로 하는 계산(SQLite 식, 열 이름은 큰따옴표. 날짜 차이는 julianday("가")-julianday("나"), 숫자는 CAST("열" AS REAL)): {"kind":"expr","sql":""} · '
        'agg = 이어진 개체의 줄을 세거나 합침: {"kind":"agg","obj":"이어진 개체 이름","fn":"count|sum|avg|min|max","col":"합칠 열(count면 빈 글자)","where":[{"col":"","op":"","value":""}]} · '
        'lookup = 이어진 개체의 값 하나를 가져옴: {"kind":"lookup","obj":"","col":""}. '
        "이어진 개체의 값으로 날짜 차이를 구해야 하면, 먼저 lookup 속성이 필요하다고 error로 알려 준다. 연산자는 " + " ".join(OPS) + ". "
        "where에는 업무 조건만 쓴다(예: status = 지급). 두 개체를 잇는 조건(키가 같다)은 쓰지 않는다 — 관계는 프로그램이 따라간다. "
        '형식: {"col":"영문 소문자_밑줄 열 이름","label":"한국어 이름","calc":{...},"plain":"계산을 쉬운 말 한 줄로"} 만들 수 없으면 {"error":"이유"}',
        f"요청: {text}\n이 개체 {name}({me['label']})의 열: {mine}\n이어진 개체:\n" + ("\n".join(near) or "(없음)"))
    if d.get("error"):
        raise ValueError(d["error"])
    if d.get("calc", {}).get("obj"):
        d["calc"]["obj"] = resolve(d["calc"]["obj"])
        d["calc"]["col"] = resolve_col(d["calc"]["obj"], d["calc"].get("col"))
        both = set(_view_cols(name)) | set(_view_cols(d["calc"]["obj"]))  # "열 = 열 이름" 같은 잇는 조건은 버림
        d["calc"]["where"] = [w for w in d["calc"].get("where") or [] if str(w.get("value")) not in both]
    d["col"] = clean_name(d.get("col") or "calc")
    if d["col"] in _view_cols(name):
        d["col"] += "_2"
    d["calc"]["text"] = text.strip()
    d["preview"] = calc_preview(name, d["col"], d["calc"])
    return d


def calc_preview(name: str, col: str, spec: dict) -> list[dict]:
    o = one("SELECT key, title FROM obj WHERE name=?", (name,))
    sql = build_view(name, (col, spec))
    try:
        rs = rows(f"SELECT * FROM ({sql}) LIMIT 5")
    except Exception as e:
        raise ValueError(f"계산을 실행하지 못했습니다. {str(e)[:120]}")
    show = o["title"] or o["key"]
    return [{"key": r.get(show), "value": r.get(col)} for r in rs]


def _insert_calc(name: str, col: str, lab: str, spec: dict) -> None:
    calc_preview(name, col, spec)
    n = one("SELECT COALESCE(MAX(ord),0)+1 n FROM prop WHERE obj=?", (name,))["n"]
    connect().execute("INSERT OR REPLACE INTO prop (obj, col, label, type, desc, syn, hidden, sensitive, calc, ord) VALUES (?,?,?,?,?,?,?,?,?,?)",
                      (name, col, lab, None, spec.get("plain", ""), "", 0, 0, json.dumps(spec, ensure_ascii=False), max(n, 1000)))
    rebuild(name)


def add_calc(name: str, col: str, lab: str, spec: dict, by="사람") -> None:
    _insert_calc(name, col, lab, spec)
    history.record(f"계산 속성 추가 · {label(name)}.{lab}", "개체 · 관계", by, {"계산": spec.get("text") or json.dumps(spec, ensure_ascii=False)})


def remove_calc(name: str, col: str, by="사람") -> None:
    connect().execute("DELETE FROM prop WHERE obj=? AND col=? AND calc IS NOT NULL", (name, col))
    rebuild(name)
    history.record(f"계산 속성 삭제 · {label(name)}.{col}", "개체 · 관계", by, {"remove": col})


# ── 같은 대상 묶기(개체 해소 · Entity Resolution) ──
def _norm(v: str, how: str) -> str:
    v = str(v or "").strip()
    if how == "exact":
        return v
    return re.sub(r"[\s\-_.()·,/]", "", v).lower()


def er_run(a: str, b: str, pairs: list[list[str]], how: str = "loose", limit: int = 3000) -> dict:
    """두 개체에서 같은 대상 짝 찾기. pairs = [[가 열, 나 열], …] 여러 열을 함께 견줌. how = exact · loose(표기 차이 무시) · similar(비슷함 0.85 이상)."""
    if not pairs:
        raise ValueError("견줄 열을 1쌍 이상 선택해 주세요.")
    ka, kb = one("SELECT key FROM obj WHERE name=?", (a,))["key"], one("SELECT key FROM obj WHERE name=?", (b,))["key"]
    ra, rb = rows(f"SELECT * FROM {ot(a)} LIMIT {limit}"), rows(f"SELECT * FROM {ot(b)} LIMIT {limit}")
    sig = lambda r, cs: [_norm(r.get(c), how) for c in cs]  # noqa: E731
    ca, cb = [p[0] for p in pairs], [p[1] for p in pairs]
    out = []
    if how in ("exact", "loose"):
        idx = {}
        for r in rb:
            s_ = sig(r, cb)
            if all(s_):
                idx.setdefault(tuple(s_), []).append(r)
        for r in ra:
            s_ = sig(r, ca)
            for m in idx.get(tuple(s_), []) if all(s_) else []:
                out.append({"a_key": r[ka], "b_key": m[kb], "score": 1.0, "a": [r.get(c) for c in ca], "b": [m.get(c) for c in cb]})
    else:
        block = {}
        for r in rb:
            s_ = sig(r, cb)
            if all(s_):
                block.setdefault(s_[0][:1], []).append((s_, r))
        for r in ra:
            s_ = sig(r, ca)
            if not all(s_):
                continue
            for t_, m in block.get(s_[0][:1], []):
                sc = min(difflib.SequenceMatcher(None, x, y).ratio() for x, y in zip(s_, t_))
                if sc >= 0.85:
                    out.append({"a_key": r[ka], "b_key": m[kb], "score": round(sc, 2), "a": [r.get(c) for c in ca], "b": [m.get(c) for c in cb]})
    ca_, cb_ = {}, {}
    for x in out:
        ca_[x["a_key"]] = ca_.get(x["a_key"], 0) + 1
        cb_[x["b_key"]] = cb_.get(x["b_key"], 0) + 1
    for x in out:  # 한쪽 대상이 여러 짝과 이어지면 확인 필요(예: 이름만으로 견줬는데 동명이인)
        x["multi"] = ca_[x["a_key"]] > 1
    out.sort(key=lambda x: (not x["multi"], x["score"]))
    return {"pairs": out[:500], "total": len(out), "multi": sum(x["multi"] for x in out), "a_rows": len(ra), "b_rows": len(rb)}


def er_apply(a: str, b: str, pairs: list[dict], cols: list[list[str]], how: str, by="사람") -> dict:
    """확정한 짝을 매핑 표로 저장 → 개체 하나 + 관계 둘(가 ↔ 매핑 ↔ 나)."""
    if not pairs:
        raise ValueError("저장할 짝이 없습니다.")
    la, lb = label(a), label(b)
    tname = clean_name(f"same_{a}_{b}")
    sources.save_table(tname, ["a_key", "b_key", "score", "how"], [[p["a_key"], p["b_key"], p.get("score", 1), how] for p in pairs], None)
    con = connect()
    con.execute("DELETE FROM obj WHERE name=?", (tname,))
    con.execute("DELETE FROM rel WHERE a_tbl=? OR b_tbl=?", (tname, tname))
    con.execute("INSERT INTO obj (name, label, key, by, at, base, desc) VALUES (?,?,?,?,?,?,?)",
                (tname, f"{la} = {lb}", "a_key", by, now(), tname, "같은 대상 묶기로 확정한 짝(" + ", ".join(f"{x}={y}" for x, y in cols) + ")"))
    rebuild(tname)
    ka, kb = one("SELECT key FROM obj WHERE name=?", (a,))["key"], one("SELECT key FROM obj WHERE name=?", (b,))["key"]
    _add_rel({"a_tbl": tname, "a_col": "a_key", "b_tbl": a, "b_col": ka, "name": "같은 대상"}, by)
    _add_rel({"a_tbl": tname, "a_col": "b_key", "b_tbl": b, "b_col": kb, "name": "같은 대상"}, by)
    history.record(f"같은 대상 묶기 · {la} = {lb} {len(pairs)}쌍", "개체 · 관계", by,
                   {"견준 열": ", ".join(f"{x} = {y}" for x, y in cols), "기준": {"exact": "정확히 같음", "loose": "표기 차이 무시", "similar": "비슷함"}.get(how, how), "짝": len(pairs)})
    return {"name": tname, "pairs": len(pairs)}
