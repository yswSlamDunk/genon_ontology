"""변경 이력 — 바꿀 때마다 버전(v번호)을 남김.

- 화면 버튼으로 직접 바꾼 것: 바로 적용 + 기록
- Copilot이 제안한 것 · 되돌리기: "승인 대기"로 들어가고, 승인해야 적용
버전마다 온톨로지 모습(개체 · 관계 · 읽을 칸 · 규칙 · 구축 의도)을 통째로 저장 → 되돌리기에 씀.
"""
import json
import time

from .db import connect, kv_get, kv_set, now, one, rows

LAYERS = ["데이터", "개체 · 관계", "읽을 칸", "규칙", "지표", "골든 질문", "구축 의도", "에이전트", "가정", "사용자"]


def snapshot() -> dict:
    return {
        "obj": rows("SELECT name, label, key, by, base, filter, title, desc FROM obj ORDER BY name"),
        "prop": rows("SELECT * FROM prop ORDER BY obj, ord"),
        "metric": rows("SELECT name, text, spec, by FROM metric ORDER BY id"),
        "rel": rows("SELECT id, name, a_tbl, a_col, b_tbl, b_col, by FROM rel ORDER BY id"),
        "field": rows("SELECT name, label, desc, ord FROM field ORDER BY ord"),
        "rule": rows("SELECT id, kind, name, text, cond, ord, on_ FROM rule ORDER BY id"),
        "intent": kv_get("intent", ""),
        "instr": kv_get("agent_instr", ""),
    }


def restore(s: dict) -> None:
    con = connect()
    for t in ["obj", "rel", "field", "rule"] + [t for t in ("prop", "metric") if t in s]:
        con.execute(f"DELETE FROM {t}")
    t0 = now()
    for o in s["obj"]:
        con.execute("INSERT INTO obj (name, label, key, by, at, base, filter, title, desc) VALUES (?,?,?,?,?,?,?,?,?)",
                    (o["name"], o["label"], o["key"], o["by"], t0, o.get("base") or o["name"], o.get("filter"), o.get("title"), o.get("desc")))
    for p in s.get("prop", []):
        con.execute("INSERT INTO prop (obj, col, label, type, desc, syn, hidden, sensitive, calc, ord) VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (p["obj"], p["col"], p["label"], p["type"], p["desc"], p["syn"], p["hidden"], p["sensitive"], p["calc"], p["ord"]))
    for m in s.get("metric", []):
        con.execute("INSERT INTO metric (name, text, spec, by, at) VALUES (?,?,?,?,?)", (m["name"], m["text"], m["spec"], m["by"], t0))
    for r in s["rel"]:
        con.execute("INSERT INTO rel VALUES (?,?,?,?,?,?,?,?)", (r["id"], r["name"], r["a_tbl"], r["a_col"], r["b_tbl"], r["b_col"], r["by"], t0))
    for f in s["field"]:
        con.execute("INSERT INTO field VALUES (?,?,?,?,?)", (f["name"], f["label"], f["desc"], f["ord"], t0))
    for r in s["rule"]:
        con.execute("INSERT INTO rule VALUES (?,?,?,?,?,?,?,?)", (r["id"], r["kind"], r["name"], r["text"], r["cond"], r["ord"], r["on_"], t0))
    kv_set("intent", s.get("intent", ""))
    if "instr" in s:
        kv_set("agent_instr", s["instr"])
    from . import onto
    onto.rebuild()


def _who(by: str) -> str:
    """'사람' · 'Copilot 제안'에 지금 사용자 이름을 붙임."""
    from .users import ACTOR
    u = ACTOR.get()
    if not u:
        return by
    if by == "사람":
        return u["name"]
    if by == "Copilot 제안":
        return f"Copilot 제안 · {u['name']}"
    return by


def record(title: str, layer: str, by: str, diff, status: str = "applied", op: dict | None = None) -> int:
    by = _who(by)
    snap = snapshot() if status == "applied" else None
    return connect().execute(
        "INSERT INTO change (title, layer, by, status, op, diff, snap, at, decided_at) VALUES (?,?,?,?,?,?,?,?,?)",
        (title, layer, by, status, json.dumps(op, ensure_ascii=False) if op else None, json.dumps(diff, ensure_ascii=False),
         json.dumps(snap, ensure_ascii=False) if snap else None, now(), now() if status == "applied" else None)).lastrowid


def propose(title: str, layer: str, op: dict, diff, by: str = "Copilot 제안") -> int:
    """승인이 필요한 변경 — 아직 적용 안 함."""
    return record(title, layer, by, diff, status="pending", op=op)


def approve(cid: int, who: dict | None = None) -> dict:
    c = one("SELECT * FROM change WHERE id=?", (cid,))
    if not c or c["status"] != "pending":
        raise ValueError("승인 대기 중인 변경이 아닙니다.")
    if who and who.get("role") != "관리자" and who.get("name") and who["name"] in (c["by"] or ""):
        raise PermissionError("내가 신청한 변경은 다른 검토자가 승인해야 합니다.")
    op = json.loads(c["op"])
    from . import onto
    onto.apply_op(op)
    connect().execute("UPDATE change SET status='applied', snap=?, decided_at=?, by=? WHERE id=?",
                      (json.dumps(snapshot(), ensure_ascii=False), now(), c["by"] + (f" → 승인 {who['name']}" if who else ""), cid))
    return {"id": cid, "title": c["title"]}


def reject(cid: int, reason: str = "", who: dict | None = None) -> None:
    c = one("SELECT diff FROM change WHERE id=?", (cid,))
    d = json.loads(c["diff"] or "{}") if c else {}
    if reason:
        d = {**(d if isinstance(d, dict) else {"diff": d}), "반려 사유": reason + (f" ({who['name']})" if who else "")}
    connect().execute("UPDATE change SET status='rejected', diff=?, decided_at=? WHERE id=? AND status='pending'",
                      (json.dumps(d, ensure_ascii=False), now(), cid))


def rollback_request(cid: int, by: str = "Copilot 제안") -> int:
    c = one("SELECT * FROM change WHERE id=? AND status='applied' AND snap IS NOT NULL", (cid,))
    if not c:
        raise ValueError("복원할 수 있는 버전이 아닙니다.")
    return propose(f"v{cid} 복원", "개체 · 관계", {"type": "restore", "snap": json.loads(c["snap"])},
                   {"to": f"v{cid}", "title": c["title"]}, by)


def current() -> int:
    r = one("SELECT MAX(id) v FROM change WHERE status='applied'")
    return r["v"] or 0


def listing() -> list[dict]:
    out = []
    for c in rows("SELECT id, title, layer, by, status, diff, at, decided_at FROM change ORDER BY id DESC LIMIT 200"):
        c["diff"] = json.loads(c["diff"] or "null")
        out.append(c)
    return out


def pending_count() -> int:
    return one("SELECT COUNT(*) n FROM change WHERE status='pending'")["n"]


def today() -> dict:
    t = time.localtime()
    start = time.mktime((t.tm_year, t.tm_mon, t.tm_mday, 0, 0, 0, 0, 0, -1))
    out = {k: [] for k in LAYERS}
    for c in rows("SELECT title, layer, status FROM change WHERE at>=? ORDER BY id", (start,)):
        out.setdefault(c["layer"], []).append(c["title"] + (" (승인 대기)" if c["status"] == "pending" else ""))
    return out
