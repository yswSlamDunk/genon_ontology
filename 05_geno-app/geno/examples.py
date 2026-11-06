"""누르면 바로 해 볼 수 있는 예시 — 지금 DB에 있는 엔터티 형식 · 속성 · 실제 값 · 문서 본문으로 만듦(LLM 없음).

- agent: 데이터 에이전트 질문 유형별(집계 · 계산 속성 · 여러 단계 · 규칙 판정 · 문서 본문)
- search: 본문 검색(검색어 + 좁힐 대상) — 실제로 1건 이상 나오는 것만
- whatif: 값을 바꾸면 계산 속성 · 규칙 판정이 실제로 달라지는 것만(원본은 그대로, 복사본에서 확인)
- objects: 조건으로 떼어 낼 엔터티 형식(값 종류가 몇 개뿐인 글자 열)
- relations: 값이 겹치는데 아직 관계가 없는 열 짝
데이터가 없으면 빈 목록. 결과는 마지막 변경 버전이 같으면 다시 만들지 않음.
"""
import json
import re
from datetime import date, timedelta

from . import docs, graph, naming, onto, rules, sources, whatif
from .db import kv_get, kv_set, one, ot, q, rows

STOP = {"있습니다", "합니다", "위와", "같이", "하며", "위하여", "대한", "동의합니다", "본인은", "관계없음", "가상", "서류", "실제", "인물"}


def _j(w: str, a: str, b: str) -> str:
    """받침 따라 조사(a: 받침 있음, b: 없음). 숫자 · 영문 끝은 읽는 소리로(7=칠 → 받침, 2=이 → 없음)."""
    c = str(w)[-1:] if w else ""
    if c.isdigit():
        return a if c in "0136789" else b
    if c.isascii() and c.isalpha():
        return a if c.lower() in "lmnr" else b
    return a if c and "가" <= c <= "힣" and (ord(c) - 0xAC00) % 28 else b


def _objs() -> list[dict]:
    return [o for o in onto.objects() if not o["name"].startswith(("same_", "result_"))]


def _main(objs: list[dict]) -> list[dict]:
    rels = onto.relations()
    deg = lambda n: sum(1 for r in rels if n in (r["a_tbl"], r["b_tbl"]))
    num = lambda o: any(p["type"] == "숫자" and p["col"] != o["key"] and not p["calc"] for p in o["props"])
    date_ = lambda o: any(p["type"] == "날짜" for p in o["props"])
    return sorted(objs, key=lambda o: -(deg(o["name"]) + 3 * num(o) + 2 * date_(o) + min(o["nrows"], 50) / 50))


def _first_key(o: dict) -> str | None:
    r = one(f"SELECT {q(o['key'])} k FROM {ot(o['name'])} WHERE {q(o['key'])} IS NOT NULL AND {q(o['key'])}<>'' LIMIT 1")
    return str(r["k"]) if r else None


def _named(o: dict) -> list[dict]:
    """업무 이름을 붙인 속성 먼저(열 이름 그대로인 것은 뒤로)."""
    return sorted(o["props"], key=lambda p: not p.get("named"))


def _cat(o: dict) -> dict | None:
    for p in _named(o):
        if p["type"] != "글자" or p["hidden"] or p["calc"] or p["col"] in (o["key"], o.get("title")) or re.search(r"_id$|코드|번호", p["col"] + p["label"]):
            continue
        n = one(f"SELECT COUNT(DISTINCT {q(p['col'])}) d, COUNT(*) n FROM {ot(o['name'])} WHERE {q(p['col'])}<>''")
        if n and 1 < n["d"] <= min(12, max(2, n["n"] * 0.6)):
            return p
    return None


def _agent(objs: list[dict]) -> list[dict]:
    out = []
    main = _main(objs)
    # 집계
    for o in main[:3]:
        c = _cat(o)
        if c:
            out.append({"kind": "집계", "q": f"{c['label']}별 {o['label']} 건수는?"})
            break
    # 계산 속성
    for o in main:
        calcs = [p for p in o["props"] if p["calc"]]
        k = _first_key(o) if calcs else None
        if calcs and k:
            lab = calcs[-1]["label"]
            out.append({"kind": "계산 속성", "q": f"{o['label']} {k}의 {lab}{_j(lab, '은', '는')}?"})
            break
    # 여러 단계(관계 2단계)
    rels = onto.view()["relations"]
    byname = {o["name"]: o for o in objs}
    # 한 건에서 한 건으로만 이어지는 쪽(N:1 · 1:1)만 따라감 — 답이 하나로 정해지게
    nb = lambda n: [r["b_tbl"] for r in rels if r["a_tbl"] == n and r.get("card") in ("N:1", "1:1")] + [r["a_tbl"] for r in rels if r["b_tbl"] == n and r.get("card") in ("1:N", "1:1")]
    done = False
    # 출발: 계산 속성이 있고 한 건 → 한 건으로 나가는 관계가 많은 업무 엔터티(질문이 보통 여기서 시작)
    starts = sorted(main[:6], key=lambda o: (-any(p["calc"] for p in o["props"]), -len(nb(o["name"]))))
    for a in starts[:4]:
        k = _first_key(a)
        if not k or done:
            continue
        for b in nb(a["name"]):
            for c in nb(b):
                if c in (a["name"], b) or c not in byname or b not in byname:
                    continue
                co = byname[c]
                show = next((p for p in _named(co) if p["type"] in ("글자", "날짜") and not p["hidden"] and not p["calc"] and p["col"] != co["key"] and not p["sensitive"] and not re.search(r"_id$|^id$", p["col"])), None)
                if not show:
                    continue
                try:
                    got = graph.gather(a["name"], a["key"], k, targets=[c], depth=2)["got"]
                except Exception:
                    continue
                if got.get(c):
                    out.append({"kind": "여러 단계", "q": f"{a['label']} {k}의 {byname[b]['label']}{_j(byname[b]['label'], '을', '를')} 거쳐 이어진 {co['label']}의 {show['label']}{_j(show['label'], '은', '는')}?"})
                    done = True
                    break
            if done:
                break
    # 규칙 판정
    for r in rules.listing():
        if not (r["on_"] and r["check"]["ok"]):
            continue
        st = byname.get(r["cond"]["start"])
        if not st:
            continue
        try:
            hits = rules.test(r["id"])["hits"]
        except Exception:
            hits = []
        k = str(hits[0]) if hits else _first_key(st)
        then = str(r["cond"].get("then") or r["name"]).strip()
        if k:
            out.append({"kind": "규칙 판정", "q": f"{st['label']} {k}{_j(k, '은', '는')} {then} 대상인가요?"})
            break
    # 문서 본문
    s = _search(objs, 1)
    if s:
        did = one("SELECT c.doc_id, d.doc_type FROM chunk c JOIN doc d ON d.id=c.doc_id WHERE c.text LIKE ? AND d.doc_type<>'' LIMIT 1", (f"%{s[0]['q']}%",))
        if did:
            case = re.sub(r"-D\d+$", "", re.split(r"[_ ]", did["doc_id"])[0])  # CL-001-D1_보험금청구서 → CL-001
            out.append({"kind": "문서 본문", "q": f"{case} {did['doc_type']}에 적힌 {s[0]['q']}{_j(s[0]['q'], '은', '는')}?"})
    return out


def _phrases(doc_ids: list[str]) -> list[str]:
    """문서 본문에서 항목 이름(표 칸 머리)을 뽑음 — 여러 문서에 되풀이되는 짧은 말(값은 문서마다 달라서 빠짐)."""
    from collections import Counter
    seen: Counter = Counter()
    for did in doc_ids:
        cells = set()
        for c in docs.text_of(did):
            for cell in re.split(r"\||\n|:|：", c["text"]):
                w = re.sub(r"\s+", " ", cell).strip()
                if 2 <= len(w) <= 10 and re.fullmatch(r"[가-힣·\s]+", w) and w not in STOP and not re.fullmatch(r"(?:[가-힣] )+[가-힣]", w) and len(w.split()) <= 2:
                    cells.add(w)
        seen.update(cells)
    many = [w for w, n in seen.most_common() if n >= 2] or [w for w, _ in seen.most_common()]
    return many


def _search(objs: list[dict], n: int = 3) -> list[dict]:
    """본문 검색 예시 — 대상으로 좁혀 실제로 1건 이상 나오는 검색어."""
    if not one("SELECT 1 FROM chunk LIMIT 1"):
        return []
    out = []
    def docs_of(o, k, depth):
        try:
            got = graph.gather(o["name"], o["key"], k, depth=depth)["got"]
        except Exception:
            return []
        return sorted({str(r["doc_id"]) for rs in got.values() for r in rs if r.get("doc_id")})
    near = []
    for o in _main(objs)[:8]:
        if o["base"] == "doc_extract" or o["base"].startswith("claim_document") and False:
            continue
        k = _first_key(o)
        if k:
            near.append((next((d for d in (1, 2, 3) if docs_of(o, k, d)), 9), o, k))
    for _, o, k in sorted(near, key=lambda x: x[0])[:6]:
        ids = docs_of(o, k, 3)
        if not ids:
            continue
        for w in _phrases(ids)[:6]:
            if docs.search(w, ids, 1):
                out.append({"q": w, "obj": o["name"], "obj_label": o["label"], "value": k, "docs": len(ids)})
            if len(out) >= n:
                return out
        if out:
            break
    if len(out) < n:  # 좁히지 않는 검색어
        for w in _phrases([r["doc_id"] for r in rows("SELECT DISTINCT doc_id FROM chunk LIMIT 5")])[:8]:
            if all(w != x["q"] for x in out) and docs.search(w, None, 1):
                out.append({"q": w, "obj": "", "obj_label": "", "value": "", "docs": 0})
            if len(out) >= n:
                break
    return out


def _whatif(objs: list[dict]) -> list[dict]:
    """값 바꾸기 후보를 만들어 복사본에서 돌려 보고, 실제로 결과가 달라지는 것만 남김(규칙이 바뀌는 것 먼저)."""
    byname = {o["name"]: o for o in objs}
    cands = []
    for r in rules.listing():
        if not (r["on_"] and r["check"]["ok"]):
            continue
        st = byname.get(r["cond"]["start"])
        if not st:
            continue
        try:
            hits = set(map(str, rules.test(r["id"])["hits"]))
        except Exception:
            continue
        for w in r["cond"].get("when", []):
            if w.get("obj") != st["name"] or w.get("op") not in ("<", "<=", ">", ">=") or w.get("ref"):
                continue
            try:
                v = float(str(w["value"]).replace(",", ""))
            except (TypeError, ValueError):
                continue
            p = next((x for x in st["props"] if x["col"] == w["col"]), None)
            if not p:
                continue
            row = one(f"SELECT * FROM {ot(st['name'])} WHERE CAST({q(st['key'])} AS TEXT) NOT IN ({','.join('?' * len(hits)) or 'NULL'}) LIMIT 1", list(hits)) if hits else one(f"SELECT * FROM {ot(st['name'])} LIMIT 1")
            if not row:
                continue
            low = w["op"] in ("<", "<=")
            if not p["calc"]:  # 원본 숫자 칸 — 기준을 넘는 값으로
                cands.append({"obj": st["name"], "key": str(row[st["key"]]), "col": w["col"], "value": str(int(v - 1) if low else int(v + 1))})
                continue
            spec = p["calc"]
            m = re.fullmatch(r'\s*julianday\("(\w+)"\)\s*-\s*julianday\("(\w+)"\)\s*', str(spec.get("sql", ""))) if spec.get("kind") == "expr" else None
            if m and row.get(m.group(2)):  # 날짜 차이 계산 속성 — 앞 날짜를 기준 안쪽/바깥으로
                try:
                    b = date.fromisoformat(str(row[m.group(2)])[:10])
                except ValueError:
                    continue
                days = max(1, int(v) // 3) if low else int(v) * 2
                if m.group(1) in {x["col"] for x in st["props"] if not x["calc"]}:
                    cands.append({"obj": st["name"], "key": str(row[st["key"]]), "col": m.group(1), "value": (b + timedelta(days=days)).isoformat()})
    # 계산 속성 입력 값을 다른 줄의 값으로
    for o in _main(objs)[:4]:
        for p in o["props"]:
            spec = p["calc"] or {}
            if spec.get("kind") != "expr":
                continue
            used = [c for c in re.findall(r'"([^"]+)"', str(spec.get("sql", ""))) if c in {x["col"] for x in o["props"] if not x["calc"]}]
            if not used:
                continue
            rs = rows(f"SELECT {q(o['key'])} k, {q(used[0])} v FROM {ot(o['name'])} WHERE {q(used[0])}<>'' LIMIT 2")
            if len(rs) == 2 and rs[0]["v"] != rs[1]["v"]:
                cands.append({"obj": o["name"], "key": str(rs[0]["k"]), "col": used[0], "value": str(rs[1]["v"])})
    out, seen = [], set()
    for c in cands:
        sig = (c["obj"], c["key"], c["col"])
        if sig in seen:
            continue
        seen.add(sig)
        try:
            r = whatif.run([c])
        except Exception:
            continue
        nc = sum(x["changed"] for x in r["calcs"])
        nr = [x for x in r["rules"] if x.get("changed")]
        if not nc and not nr:
            continue
        ch = r["changes"][0]
        out.append({**c, "obj_label": ch["obj_label"], "label": ch["label"], "before": ch["before"],
                    "effect": f"계산 속성 {nc}개" + (f" · 규칙 '{nr[0]['name']}' {nr[0]['before']}건 → {nr[0]['after']}건" if nr else ""), "rule": bool(nr)})
        if len(out) >= 4:
            break
    out.sort(key=lambda x: not x["rule"])
    return out[:3]


def _objects() -> list[dict]:
    """조건으로 떼어 낼 엔터티 형식 — 값 종류가 몇 개뿐인 글자 열의 값 하나."""
    have = {(o["base"], json.dumps(o["filter"], ensure_ascii=False)) for o in onto.objects()}
    out = []
    for t in sources.table_names():
        tb = sources.table(t)
        if not tb or tb["nrows"] < 4:
            continue
        for c, ty in zip(tb["cols"], tb["types"]):
            if ty != "글자" or re.search(r"_id$|id$|name|이름|번호", c):
                continue
            vs = rows(f"SELECT {q(c)} v, COUNT(*) n FROM {q('d:' + t)} WHERE {q(c)}<>'' GROUP BY {q(c)} ORDER BY n DESC")
            if 2 <= len(vs) <= 8 and vs[0]["n"] >= 2:
                f = [{"col": c, "op": "=", "value": vs[0]["v"]}]
                if (t, json.dumps(f, ensure_ascii=False)) not in have:
                    v = str(vs[0]["v"])[:20]
                    lab = v if re.search(r"[가-힣]", v) else f"{naming.plain(c)} {v}"  # Q2 → 질문 번호 Q2
                    out.append({"label": lab, "base": t, "filter": f, "key": tb["cols"][0], "rows": vs[0]["n"]})
                break
        if len(out) >= 4:
            break
    return out


def _relations() -> list[dict]:
    """값이 겹치는데 아직 관계가 없는 열 짝(엔터티 형식이 있는 테이블끼리)."""
    objs = {o["base"]: o for o in onto.objects() if not o["filter"] and not o["name"].startswith(("same_", "result_"))}
    have = {(r["a_tbl"], r["a_col"], r["b_tbl"], r["b_col"]) for r in onto.relations()}
    have |= {(b, bc, a, ac) for a, ac, b, bc in have}
    out, seen = [], set()
    ty = lambda t, c: dict(zip(sources.table(t)["cols"], sources.table(t)["types"])).get(c)
    for c in onto.candidates([t for t in sources.table_names() if t in objs]):
        a, b = objs.get(c["a_tbl"]), objs.get(c["b_tbl"])
        pair = frozenset([(c["a_tbl"], c["a_col"]), (c["b_tbl"], c["b_col"])])
        if not a or not b or (a["name"], c["a_col"], b["name"], c["b_col"]) in have or pair in seen:
            continue
        if ty(c["a_tbl"], c["a_col"]) in ("날짜", "숫자") or ty(c["b_tbl"], c["b_col"]) in ("날짜", "숫자"):
            continue
        seen.add(pair)
        pl = lambda o, col: next((p["label"] for p in o["props"] if p["col"] == col), naming.plain(col))
        out.append({"a": a["name"], "a_label": a["label"], "a_col": c["a_col"], "a_col_label": pl(a, c["a_col"]), "b": b["name"], "b_label": b["label"], "b_col": c["b_col"], "b_col_label": pl(b, c["b_col"]), "hit": c["hit"], "of": c["a"]})
        if len(out) >= 4:
            break
    return out


def build(refresh: bool = False) -> dict:
    sig = f"{(one('SELECT MAX(id) m FROM change') or {}).get('m')}:{(one('SELECT COUNT(*) n FROM chunk') or {}).get('n')}"
    cache = kv_get("examples")
    if cache and cache.get("sig") == sig and not refresh:
        return cache["d"]
    objs = _objs()
    d = {"agent": [], "search": [], "whatif": [], "objects": [], "relations": []}
    if objs:
        for k, f in (("agent", lambda: _agent(objs)), ("search", lambda: _search(objs)), ("whatif", lambda: _whatif(objs)), ("relations", _relations)):
            try:
                d[k] = f()
            except Exception:
                d[k] = []
    if sources.table_names():
        try:
            d["objects"] = _objects()
        except Exception:
            d["objects"] = []
    kv_set("examples", {"sig": sig, "d": d})
    return d
