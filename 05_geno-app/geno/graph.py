"""관계를 따라 실제 값을 모으는 곳 — 질문 답하기 · 규칙 실행 · 데이터 탐색이 같이 씀.

한 걸음 = 관계 하나를 따라 SQL 한 번. 걸음마다 보낸 SQL과 받은 줄 수를 남김(탄 경로).
"""
from collections import deque

from .db import ot, q, rows
from .onto import label, objects, relations


def adj() -> dict:
    g = {}
    for r in relations():
        g.setdefault(r["a_tbl"], []).append((r["b_tbl"], r["a_col"], r["b_col"], r))
        g.setdefault(r["b_tbl"], []).append((r["a_tbl"], r["b_col"], r["a_col"], r))
    return g


def path(a: str, b: str) -> list | None:
    """a에서 b까지 관계로 가는 가장 짧은 길(관계 목록). 길이 없으면 None."""
    if a == b:
        return []
    g, seen, dq = adj(), {a}, deque([(a, [])])
    while dq:
        n, p = dq.popleft()
        for m, ac, bc, r in g.get(n, []):
            if m in seen:
                continue
            np = p + [(n, m, ac, bc, r)]
            if m == b:
                return np
            seen.add(m)
            dq.append((m, np))
    return None


def start_rows(tbl: str, col: str, val: str) -> tuple[list[dict], str]:
    sql = f"SELECT * FROM {ot(tbl)} WHERE {q(col)} = ?"
    return rows(sql, (val,)), sql.replace("?", repr(val))


def hop(rows_from: list[dict], frm: str, to: str, fcol: str, tcol: str, limit: int = 200) -> tuple[list[dict], str]:
    vals = sorted({r.get(fcol) for r in rows_from if r.get(fcol) not in (None, "")})
    if not vals:
        return [], f"-- {label(frm)}.{fcol} 값이 없어 따라갈 수 없음"
    marks = ",".join("?" * len(vals))
    sql = f"SELECT * FROM {ot(to)} WHERE {q(tcol)} IN ({marks}) LIMIT {limit}"
    shown = sql.replace(marks, ", ".join(repr(v) for v in vals[:5]) + (" …" if len(vals) > 5 else ""))
    return rows(sql, vals), shown


def gather(tbl: str, col: str, val: str, targets: list[str] | None = None, depth: int = 4) -> dict:
    """시작 값에서 출발해 관계를 따라감. targets가 있으면 그쪽으로 가는 길만, 없으면 depth까지 넓게."""
    found, sql0 = start_rows(tbl, col, val)
    got = {tbl: found}
    steps = [{"title": f"시작 · {label(tbl)}", "sql": sql0, "n": len(found), "from": None, "to": tbl, "rel": None}]
    used, missing = [], []
    if not found:
        return {"got": got, "steps": steps, "used": used, "missing": missing}
    plan = []
    if targets:
        for t in targets:
            if t == tbl or t in [p[1] for p in plan]:
                continue
            p = path(tbl, t)
            if p is None:
                missing.append([tbl, t])
                continue
            for e in p:
                if e[1] not in [x[1] for x in plan] and e[1] != tbl:
                    plan.append(e)
    else:
        g, seen, dq = adj(), {tbl}, deque([(tbl, 0)])
        while dq:
            n, d = dq.popleft()
            if d >= depth:
                continue
            for m, ac, bc, r in g.get(n, []):
                if m not in seen:
                    seen.add(m)
                    plan.append((n, m, ac, bc, r))
                    dq.append((m, d + 1))
    for frm, to, fcol, tcol, r in plan:
        if frm not in got:
            continue
        res, sql = hop(got[frm], frm, to, fcol, tcol)
        got.setdefault(to, [])
        have = {tuple(sorted(x.items())) for x in got[to]}
        got[to] += [x for x in res if tuple(sorted(x.items())) not in have]
        used.append(r["id"])
        steps.append({"title": f"{label(frm)} → {label(to)}", "sql": sql, "n": len(res), "from": frm, "to": to, "rel": r["id"]})
    return {"got": got, "steps": steps, "used": used, "missing": missing}


def follow(tbl: str, col: str, val: str, hops: list[list[str]]) -> dict:
    """정해진 길(hops: [가, 나] 목록)을 그대로 따라감. 가 → 나 사이 관계가 없으면 그 걸음은 '미연결'로 남기고 건너뜀."""
    found, sql0 = start_rows(tbl, col, val)
    got = {tbl: found}
    steps = [{"title": f"시작 · {label(tbl)}", "sql": sql0, "n": len(found), "from": None, "to": tbl, "rel": None}]
    used, missing = [], []
    rels = relations()
    for a, b in hops:
        r = next((x for x in rels if {x["a_tbl"], x["b_tbl"]} == {a, b}), None)
        if r is None:
            missing.append([a, b])
            continue
        if a not in got:
            continue
        fcol, tcol = (r["a_col"], r["b_col"]) if r["a_tbl"] == a else (r["b_col"], r["a_col"])
        res, sql = hop(got[a], a, b, fcol, tcol)
        got[b] = res  # 같은 개체를 다시 지나면 더 좁힌 값으로 바꿈(예: 질병군으로 고른 담보)
        used.append(r["id"])
        steps.append({"title": f"{label(a)} → {label(b)}", "sql": sql, "n": len(res), "from": a, "to": b, "rel": r["id"]})
    return {"got": got, "steps": steps, "used": used, "missing": missing}


def explore(tbl: str, col: str, val: str) -> dict:
    """데이터 탐색 — 실제 값 그래프(2단계까지)."""
    g = gather(tbl, col, val, depth=2)
    objs = {o["name"]: o for o in objects()}
    nodes, seen = [], set()
    for t, rs in g["got"].items():
        o = objs.get(t, {})
        for r in rs[:6]:
            sig = (t, tuple(sorted((k, str(v)) for k, v in r.items())))
            if sig in seen:  # 똑같은 줄만 합침 — 키가 겹쳐도 다른 줄은 다른 점
                continue
            seen.add(sig)
            show = r.get(o.get("title") or o.get("key", ""), "")
            nodes.append({"id": f"{t}:{len(nodes)}", "tbl": t, "key": str(r.get(o.get("key", ""), "")), "label": label(t), "value": str(show)[:40], "row": r})
    edges = []
    for s in g["steps"][1:]:
        rel = next((x for x in relations() if x["id"] == s["rel"]), None)
        if not rel:
            continue
        a, b = (rel["a_tbl"], rel["a_col"]), (rel["b_tbl"], rel["b_col"])
        for na in [n for n in nodes if n["tbl"] == a[0]]:
            for nb in [n for n in nodes if n["tbl"] == b[0]]:
                if na["row"].get(a[1]) not in (None, "") and na["row"].get(a[1]) == nb["row"].get(b[1]):
                    edges.append([na["id"], nb["id"], rel["name"]])
    return {"nodes": nodes, "edges": edges, "steps": g["steps"]}
