"""규칙 — 사람이 문장으로 쓰면 LLM이 조건(JSON)으로 바꾸고, 판단은 프로그램이 조건대로 실행.

조건 모양:
{"start": "시작 개체(표 이름)",
 "when": [{"obj": "표", "col": "열", "op": "=|!=|<|<=|>|>=|포함|안 포함", "value": "글자"}  또는
          {"obj": "표", "col": "열", "op": "<", "ref": {"obj": "표", "col": "열"}}],
 "then": "결과 문구"}
판단 규칙(kind=판단)은 걸리면 결과를 붙이고, 분류 규칙(kind=분류)은 순서대로 보고 처음 걸린 곳으로 보냄.
건수 · 합계 · 날짜 차이가 필요하면 개체의 계산 속성으로 먼저 만들고, 규칙은 그 속성을 비교함.
전체 판정: 시작 개체의 모든 건에 켜진 규칙을 돌려 결과를 "판정 결과" 개체(표)로 저장 → 다음 질문 · 규칙에서 사실로 다시 씀.
"""
import json
import re

from . import history, llm
from .db import clean_name, connect, now, one, ot, rows
from .graph import gather, path
from .onto import label, objects, relations

OPS = ["=", "!=", "<", "<=", ">", ">=", "포함", "안 포함"]


def listing() -> list[dict]:
    out = []
    for r in rows("SELECT * FROM rule ORDER BY kind, ord, id"):
        r["cond"] = json.loads(r["cond"] or "{}")
        r["check"] = check(r["cond"])
        out.append(r)
    return out


def check(c: dict) -> dict:
    """조건에 쓴 개체까지 길이 있는지 — 없으면 '길 끊김'."""
    names = {o["name"]: o for o in objects()}
    bad, need = [], set()
    st = c.get("start")
    if st not in names:
        return {"ok": False, "why": [f"시작 개체 {st} 없음"], "objs": []}
    for w in c.get("when", []):
        for o, col in [(w.get("obj"), w.get("col"))] + ([(w["ref"]["obj"], w["ref"]["col"])] if w.get("ref") else []):
            if o not in names:
                bad.append(f"개체 {o} 없음")
            elif col not in names[o]["cols"]:
                bad.append(f"{label(o)}.{col} 열 없음")
            elif path(st, o) is None:
                bad.append(f"미연결 · {label(st)} → {label(o)}")
            need.add(o)
    return {"ok": not bad, "why": bad, "objs": sorted(need)}


def compile_text(text: str, kind: str) -> dict:
    objs = objects()
    if not objs:
        raise ValueError("온톨로지 설계에서 개체를 먼저 생성해 주세요.")
    brief = "\n".join(f"- {o['name']}({o['label']}): " + ", ".join(f"{p['col']}({p['label']}·{p['type']}{'·계산' if p['calc'] else ''})" for p in o["props"] if not p["hidden"]) for o in objs)
    rels = "\n".join(f"- {r['a_tbl']}.{r['a_col']} = {r['b_tbl']}.{r['b_col']}" for r in relations())
    d = llm.chat_json(
        "사람이 쓴 업무 규칙 문장을 실행 가능한 조건 JSON으로 바꾼다. 개체 · 열 이름은 주어진 그대로. 연산자는 " + " ".join(OPS) + " 중 하나. "
        "start는 규칙을 한 건씩 적용할 개체(예: 청구 · 주문)의 표 이름이며 비우지 않는다. "
        "표끼리 잇는 조건(키가 같다 등)은 쓰지 않는다 — 관계는 프로그램이 따라간다. 업무 조건만 쓴다. "
        "두 열을 비교하면 value 대신 ref를 {\"obj\":\"표\",\"col\":\"열\"} 모양으로 쓴다. 조건은 모두 AND이고, 같은 개체의 조건들은 같은 줄에서 함께 맞아야 한다. "
        "건수 · 합계 · 날짜 차이가 필요한데 그런 열(계산 속성)이 없으면 error에 '계산 속성 필요: (무엇)'이라고 쓴다. "
        '형식: {"name":"짧은 이름","start":"","when":[{"obj":"","col":"","op":"","value":""}],"then":"결과 문구"} 바꿀 수 없으면 {"error":"이유"}',
        f"규칙 종류: {kind}\n문장: {text}\n개체:\n{brief}\n관계:\n{rels or '(없음)'}")
    if d.get("error"):
        raise ValueError(d["error"])
    from .onto import resolve, resolve_col
    for w in d.get("when", []):  # ref를 "표.열" 글자로 줄 때가 있어 고쳐 줌
        if isinstance(w.get("ref"), str) and "." in w["ref"]:
            o, c = w["ref"].split(".", 1)
            w["ref"] = {"obj": o, "col": c}
        w["obj"] = resolve(w.get("obj"))
        w["col"] = resolve_col(w["obj"], w.get("col"))
        if isinstance(w.get("ref"), dict):
            w["ref"]["obj"] = resolve(w["ref"].get("obj"))
            w["ref"]["col"] = resolve_col(w["ref"]["obj"], w["ref"].get("col"))
    d["start"] = resolve(d.get("start"))
    if not d.get("start") and d.get("when"):
        d["start"] = d["when"][0]["obj"]
    d["check"] = check(d)
    return d


def insert(r: dict) -> int:
    n = one("SELECT COALESCE(MAX(ord),0)+1 n FROM rule WHERE kind=?", (r["kind"],))["n"]
    cond = {k: r[k] for k in ("start", "when", "then") if k in r}
    return connect().execute("INSERT INTO rule (kind, name, text, cond, ord, on_, at) VALUES (?,?,?,?,?,?,?)",
                             (r["kind"], r.get("name") or r["text"][:20], r["text"], json.dumps(cond, ensure_ascii=False), n, int(r.get("on", 1)), now())).lastrowid


def add(rule: dict, by: str = "사람") -> int:
    rid = insert(rule)
    history.record(f"규칙 생성 · {rule.get('name') or rule['text'][:20]}", "규칙", by, {"text": rule["text"], "kind": rule["kind"]})
    return rid


def remove(rid: int, by: str = "사람") -> None:
    r = one("SELECT * FROM rule WHERE id=?", (rid,))
    if r:
        connect().execute("DELETE FROM rule WHERE id=?", (rid,))
        history.record(f"규칙 삭제 · {r['name']}", "규칙", by, {"text": r["text"]})


def toggle(rid: int, on: bool, by: str = "사람") -> None:
    connect().execute("UPDATE rule SET on_=? WHERE id=?", (int(on), rid))
    r = one("SELECT name FROM rule WHERE id=?", (rid,))
    history.record(f"규칙 {'사용' if on else '미사용'} · {r['name']}", "규칙", by, {"on": on})


# ── 실행 ──
def _num(v):
    s = str(v).replace(",", "").strip()
    if re.fullmatch(r"-?\d+(\.\d+)?", s):
        return float(s)
    return s  # 날짜(YYYY-MM-DD)는 글자 비교로 순서가 맞음


def _cmp(a, op, b) -> bool:
    if a in (None, "") or b in (None, ""):
        return False
    if op in ("포함", "안 포함"):
        hit = str(b) in str(a)
        return hit if op == "포함" else not hit
    x, y = _num(a), _num(b)
    if type(x) is not type(y):
        x, y = str(a), str(b)
    return {"=": x == y, "!=": x != y, "<": x < y, "<=": x <= y, ">": x > y, ">=": x >= y}[op]


def _row_ok(row: dict, w: dict, got: dict) -> bool:
    right = [r.get(w["ref"]["col"]) for r in got.get(w["ref"]["obj"], [])] if w.get("ref") else [w.get("value")]
    return any(_cmp(row.get(w["col"]), w["op"], b) for b in right)


def evaluate(c: dict, got: dict) -> dict:
    """모은 값(got)으로 조건을 봄. 같은 개체에 걸린 조건은 한 줄이 모두 맞아야 함(예: 문항 Q1이면서 답 '아니오'). 조건마다 본 값을 남김(근거)."""
    groups = {}
    for w in c.get("when", []):
        groups.setdefault(w["obj"], []).append(w)
    seen, ok = [], True
    for obj, ws in groups.items():
        rs = got.get(obj, [])
        good = [r for r in rs if all(_row_ok(r, w, got) for w in ws)]
        for w in ws:
            rname = f"{label(w['ref']['obj'])}.{w['ref']['col']}" if w.get("ref") else repr(w.get("value"))
            seen.append({"text": f"{label(obj)}.{w['col']} {w['op']} {rname}", "left": [r.get(w["col"]) for r in (good or rs)][:3],
                         "hit": bool(good), "nodata": not rs})
        ok = ok and bool(good)
    return {"hit": ok, "seen": seen}


def run_for(start: str, key_col: str, key_val: str, got: dict | None = None) -> list[dict]:
    """한 건(시작 개체의 한 줄)에 켜진 규칙을 모두 실행."""
    out = []
    routed = False
    for r in listing():
        c = r["cond"]
        if not r["on_"] or c.get("start") != start:
            continue
        if not r["check"]["ok"]:
            out.append({"id": r["id"], "kind": r["kind"], "name": r["name"], "hit": None, "why": r["check"]["why"]})
            continue
        g = got if got is not None else gather(start, key_col, key_val, targets=r["check"]["objs"])["got"]
        e = evaluate(c, g)
        res = {"id": r["id"], "kind": r["kind"], "name": r["name"], "hit": e["hit"], "then": c.get("then"), "seen": e["seen"]}
        if r["kind"] == "분류":
            if routed:
                res["hit"], res["skipped"] = False, True
            routed = routed or e["hit"]
        out.append(res)
    return out


def test(rid: int) -> dict:
    """규칙 시험 — 시작 개체의 모든 줄에 돌려 보고 걸린 건 목록."""
    r = next((x for x in listing() if x["id"] == rid), None)
    if not r or not r["check"]["ok"]:
        raise ValueError("실행할 수 없는 규칙입니다. (미연결 또는 열 없음)")
    st = r["cond"]["start"]
    key = next(o["key"] for o in objects() if o["name"] == st)
    from .db import ot
    hits, total = [], 0
    for row in rows(f"SELECT * FROM {ot(st)} LIMIT 500"):
        total += 1
        g = gather(st, key, row[key], targets=r["check"]["objs"])["got"]
        if evaluate(r["cond"], g)["hit"]:
            hits.append(row[key])
    return {"total": total, "hits": hits}


def run_all(start: str, by: str = "사람", limit: int = 2000) -> dict:
    """전체 판정 — 건마다 켜진 규칙을 모두 돌려 결과표를 저장(개체로 등록 · 시작 개체와 관계)."""
    from . import history, onto, sources
    rs = [r for r in listing() if r["on_"] and r["cond"].get("start") == start]
    if not rs:
        raise ValueError(f"{label(start)}에서 시작하는 사용 중인 규칙이 없습니다.")
    key = next(o["key"] for o in objects() if o["name"] == start)
    judge = [r for r in rs if r["kind"] == "판단"]
    data, cnt, route = [], {r["name"]: 0 for r in rs}, {}
    for row in rows(f"SELECT * FROM {ot(start)} LIMIT {int(limit)}"):
        res = run_for(start, key, str(row[key]))
        hit = {x["name"]: x for x in res}
        dest = next((x["then"] for x in res if x["kind"] == "분류" and x["hit"]), "")
        route[dest or "(분류 없음)"] = route.get(dest or "(분류 없음)", 0) + 1
        for x in res:
            cnt[x["name"]] += bool(x["hit"])
        data.append([row[key], dest, ", ".join(x["name"] for x in res if x["hit"])] +
                    ["해당" if hit.get(r["name"], {}).get("hit") else "실행 불가" if hit.get(r["name"], {}).get("hit") is None else "미해당" for r in judge])
    tname = clean_name(f"result_{start}")
    cols = ["key", "route", "hits"] + [clean_name(r["name"]) or f"rule_{r['id']}" for r in judge]
    seen = set()
    cols = [c if c not in seen and not seen.add(c) else f"{c}_{i}" for i, c in enumerate(cols)]
    sources.save_table(tname, cols, data, None)
    con = connect()
    if not one("SELECT 1 FROM obj WHERE name=?", (tname,)):
        con.execute("INSERT INTO obj (name, label, key, by, at, base, desc) VALUES (?,?,?,?,?,?,?)",
                    (tname, f"{label(start)} 판정 결과", "key", "규칙 실행", now(), tname, "전체 판정 실행으로 저장한 규칙 결과(사실)"))
        con.execute("INSERT INTO rel (name, a_tbl, a_col, b_tbl, b_col, by, at) VALUES (?,?,?,?,?,?,?)", ("판정", tname, "key", start, key, "규칙 실행", now()))
    labs = {"route": ("분류 결과", "분류 규칙 중 처음 해당한 결과"), "hits": ("해당 규칙", "해당한 규칙 이름")}
    labs.update({c: (r["name"], r["text"]) for c, r in zip(cols[3:], judge)})
    for c, (lb, ds) in labs.items():
        con.execute("INSERT OR REPLACE INTO prop (obj, col, label, type, desc, syn, hidden, sensitive, calc, ord) VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (tname, c, lb, "글자", ds, "", 0, 0, None, cols.index(c)))
    onto.rebuild(tname)
    history.record(f"전체 판정 · {label(start)} {len(data)}건", "규칙", by, {"규칙": len(rs), "건": len(data), **{k: f"{v}건" for k, v in cnt.items()}})
    return {"obj": tname, "total": len(data), "rules": [{"name": r["name"], "kind": r["kind"], "hits": cnt[r["name"]]} for r in rs],
            "route": route, "rows": [dict(zip(cols, d)) for d in data[:300]], "cols": cols, "labels": {c: labs.get(c, (c,))[0] for c in cols}}
