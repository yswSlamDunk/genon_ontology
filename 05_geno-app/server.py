"""GenTology 로컬 서버 — 빈 상태에서 시작. 화면은 /web(제논 어드민 디자인 시스템 토큰).

실행: uv run uvicorn server:app --port 8795
"""
import json
from pathlib import Path

from fastapi import Body, Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from geno import chat, db, docs, examples, graph, history, llm, onto, qa, rules, sources, users, whatif

WEB = Path(__file__).parent / "web"

# 현업이 볼 수 있는 화면 데이터(나머지 GET은 view 권한)
ASK_GET = ("/api/state", "/api/me", "/api/users", "/api/onto", "/api/objects/", "/api/asks", "/api/explore", "/api/golden", "/api/docs/", "/api/dev/", "/api/search", "/api/examples")


def _need(method: str, path: str) -> str | None:
    if not path.startswith("/api/"):
        return None
    if method == "GET":
        return None if path.startswith(ASK_GET) else "view"
    if path in ("/api/ask", "/api/chat", "/api/users/first"):
        return "ask" if path != "/api/users/first" else None
    if path.startswith("/api/users") or path == "/api/reset":
        return "admin"
    if path.startswith("/api/changes/") and path.endswith(("/approve", "/reject")):
        return "review"
    if path.startswith("/api/golden/") and path.endswith("/vote"):
        return "review"
    # 읽기만 하는 실행(저장 없음)은 보기 권한으로 — 검토자도 확인할 수 있게
    if path in ("/api/onto/overlap", "/api/onto/er/run", "/api/whatif/run") or (path.startswith(("/api/metrics/", "/api/rules/")) and path.endswith(("/run", "/test"))):
        return "view"
    return "build"


async def actor(request: Request):
    """요청마다 지금 사용자(화면 위에서 고른 사람)를 정하고 권한을 봄. 변경 이력의 '누가'에 쓰임."""
    u = users.get(request.headers.get("x-geno-user"))
    users.ACTOR.set(u)
    need = _need(request.method, request.url.path)
    if need and not users.can(u, need):
        if need == "review" and u and users.can(u, "build") and request.url.path.endswith("/vote"):
            return
        who = {"build": "구축 담당·관리자만", "review": "검토자·관리자만", "admin": "관리자만", "view": "현업을 뺀 역할만", "ask": "등록된 사용자만"}.get(need, "")
        raise HTTPException(403, f"{who} 할 수 있습니다." + (f" (지금 역할: {u['role']})" if u else " 화면 위에서 사용자를 선택해 주세요."))


app = FastAPI(title="GenTology", dependencies=[Depends(actor)])


@app.middleware("http")
async def no_cache(request: Request, call_next):
    """화면 파일은 늘 새로 받게 — 고친 뒤 옛 파일이 남지 않도록."""
    r = await call_next(request)
    if request.url.path.startswith("/web"):
        r.headers["Cache-Control"] = "no-cache"
    return r
me = users.ACTOR.get


@app.exception_handler(ValueError)
async def _val(_, e: ValueError):
    return JSONResponse({"detail": str(e)}, status_code=400)


@app.exception_handler(RuntimeError)
async def _rt(_, e: RuntimeError):
    return JSONResponse({"detail": str(e)}, status_code=502)


@app.exception_handler(PermissionError)
async def _perm(_, e: PermissionError):
    return JSONResponse({"detail": str(e)}, status_code=403)


@app.get("/")
def home():
    return RedirectResponse("/web/")


@app.get("/api/state")
def state():
    v = onto.view()
    gs = qa.golden()
    return {"llm": llm.info(), "version": history.current(), "pending": history.pending_count(),
            "sources": len(sources.listing()), "tables": len(sources.table_names()), "objects": len(v["objects"]),
            "relations": len(v["relations"]), "loose": len(v["loose_tables"]), "docs": db.one("SELECT COUNT(*) n FROM doc")["n"],
            "read": db.one("SELECT COUNT(*) n FROM doc WHERE read_at IS NOT NULL")["n"], "fields": len(docs.fields()),
            "review": len(docs.review_list()), "rules": len(rules.listing()), "golden": len(gs),
            "golden_pass": sum(g["ok"] == "맞음" for g in gs), "golden_run": any(g["run_at"] for g in gs),
            "asks": db.one("SELECT COUNT(*) n FROM ask")["n"], "intent": v["intent"], "metrics": len(qa.metrics()), "scenarios": db.one("SELECT COUNT(*) n FROM scenario")["n"],
            "chunks": db.one("SELECT COUNT(*) n FROM chunk")["n"], "users": len(users.listing()), "setup": users.setup_mode()}


# ── 사용자 · 역할 ──
@app.get("/api/me")
def who_am_i():
    u = me()
    return {"user": u, "setup": users.setup_mode(), "roles": users.ROLES, "perms": sorted(users.PERMS[u["role"]]) if u else []}


@app.get("/api/users")
def user_list():
    return {"users": users.listing(), "roles": users.ROLES}


@app.post("/api/users/first")
def user_first(body: dict = Body(...)):
    if not users.setup_mode():
        raise HTTPException(400, "이미 사용자가 있습니다.")
    return {"id": users.add(body.get("name", ""), "관리자")}


@app.post("/api/users")
def user_add(body: dict = Body(...)):
    return {"id": users.add(body.get("name", ""), body.get("role", ""))}


@app.post("/api/users/{uid}/role")
def user_role(uid: int, body: dict = Body(...)):
    users.set_role(uid, body.get("role", ""))
    return {"ok": True}


@app.delete("/api/users/{uid}")
def user_del(uid: int):
    users.remove(uid)
    return {"ok": True}


@app.post("/api/reset")
def reset():
    db.reset()
    return {"ok": True}


# ── 데이터 소스 ──
@app.get("/api/sources")
def src_list():
    return sources.listing()


@app.post("/api/sources/files")
async def src_files(name: str = Form(""), tables: str = Form(""), files: list[UploadFile] = File(...)):
    return sources.add_files(name, [(f.filename, await f.read()) for f in files], json.loads(tables) if tables else None)


@app.post("/api/sources/{sid}/name")
def src_rename(sid: int, body: dict = Body(...)):
    sources.rename(sid, body.get("name", ""))
    return {"ok": True}


@app.post("/api/sources/db/test")
def src_db_test(body: dict = Body(...)):
    try:
        return sources.db_test(body["conf"], body.get("password"))
    except (ValueError, KeyError):
        raise
    except Exception as e:
        raise HTTPException(400, f"DB 연결에 실패했습니다. {str(e)[:200]}")


@app.post("/api/sources/db")
def src_db_add(body: dict = Body(...)):
    if not body.get("tables"):
        raise HTTPException(400, "가져올 표를 1개 이상 선택해 주세요.")
    try:
        return sources.db_add(body.get("name", ""), body["conf"], body.get("password"), body["tables"])
    except ValueError:
        raise
    except Exception as e:
        raise HTTPException(400, f"데이터 가져오기에 실패했습니다. {str(e)[:200]}")


@app.post("/api/sources/{sid}/sync")
def src_sync(sid: int):
    try:
        return sources.db_sync(sid)
    except Exception as e:
        raise HTTPException(400, f"데이터 가져오기에 실패했습니다. {str(e)[:200]}")


@app.delete("/api/sources/{sid}")
def src_del(sid: int):
    sources.remove(sid)
    return {"ok": True}


@app.get("/api/tables/{name}")
def tbl(name: str, n: int = 20):
    t = sources.table(name)
    if not t:
        raise HTTPException(404, "표가 없습니다.")
    return {**t, "rows": sources.sample(name, n)}


@app.get("/api/objects/{name}/explain")
def obj_explain(name: str, key: str, cols: str = ""):
    """개체 한 건의 계산 속성 풀이(식 · 들어간 값 · 출처 · 예상)."""
    return whatif.mask_items(whatif.explain(name, key, [c for c in cols.split(",") if c] or None), me())


@app.post("/api/whatif/run")
def whatif_run(body: dict = Body(...)):
    return whatif.run(body.get("changes", []), bool(body.get("golden")))


@app.get("/api/examples")
def examples_get(refresh: int = 0):
    """누르면 바로 해 볼 예시(질문 유형 · 본문 검색 · What-if · 엔터티 · 관계) — 지금 데이터로 만듦."""
    return examples.build(bool(refresh))


@app.get("/api/whatif")
def whatif_list():
    return whatif.listing()


@app.post("/api/whatif")
def whatif_save(body: dict = Body(...)):
    return {"id": whatif.save(body.get("name", ""), body.get("changes", []), body.get("result", {}))}


@app.delete("/api/whatif/{sid}")
def whatif_del(sid: int):
    whatif.remove(sid)
    return {"ok": True}


@app.get("/api/objects/{name}/rows")
def obj_rows(name: str, q: str = "", n: int = 50):
    """개체 줄 목록(인스턴스) — 검색어가 있으면 보이는 속성 어디에든 들어 있는 줄."""
    o = next((x for x in onto.objects() if x["name"] == name), None)
    if not o:
        raise HTTPException(404, "개체가 없습니다.")
    cols = [p["col"] for p in o["props"] if not p["hidden"]]
    where, args = "", ()
    if q.strip():
        where = " WHERE " + " OR ".join(f"{db.q(c)} LIKE ?" for c in cols)
        args = tuple(f"%{q.strip()}%" for _ in cols)
    rs = db.rows(f"SELECT * FROM {db.ot(name)}{where} LIMIT {int(n)}", args)
    total = db.one(f"SELECT COUNT(*) n FROM {db.ot(name)}{where}", args)["n"]
    return {"cols": cols, "labels": {p["col"]: p["label"] for p in o["props"]}, "rows": qa.mask(name, rs, me()), "total": total, "key": o["key"], "title": o.get("title")}


# ── 온톨로지 ──
@app.get("/api/onto")
def onto_view():
    return onto.view()


@app.post("/api/onto/draft")
def onto_draft(body: dict = Body({})):
    return onto.draft(body.get("instruction", ""), body.get("tables"))


@app.post("/api/onto/relation")
def onto_rel(body: dict = Body(...)):
    return onto.add_relation(body["a_tbl"], body["a_col"], body["b_tbl"], body["b_col"], body.get("name", ""))


@app.delete("/api/onto/relation/{rid}")
def onto_rel_del(rid: int):
    onto.remove_relation(rid)
    return {"ok": True}


@app.post("/api/onto/overlap")
def onto_ov(body: dict = Body(...)):
    return onto.overlap(body["a_tbl"], body["a_col"], body["b_tbl"], body["b_col"])


@app.post("/api/onto/label")
def onto_label(body: dict = Body(...)):
    onto.set_label(body["name"], body["label"])
    return {"ok": True}


@app.post("/api/onto/object")
def onto_obj_add(body: dict = Body(...)):
    return onto.add_object(body.get("label", ""), body.get("base", ""), body.get("filter", []), body.get("key", ""))


@app.delete("/api/onto/object/{name}")
def onto_obj_del(name: str):
    onto.remove_object(name)
    return {"ok": True}


@app.post("/api/onto/object/{name}/def")
def onto_obj_def(name: str, body: dict = Body(...)):
    onto.save_def(name, body)
    return {"ok": True}


@app.get("/api/onto/object/{name}/key")
def onto_key(name: str, col: str):
    return onto.key_check(name, col)


@app.post("/api/onto/object/{name}/compound_key")
def onto_compound_key(name: str, body: dict = Body(...)):
    return {"key": onto.compound_key(name, body.get("cols", []))}


@app.post("/api/onto/calc/compile")
def onto_calc_compile(body: dict = Body(...)):
    return onto.calc_compile(body["obj"], body.get("text", ""))


@app.post("/api/onto/calc")
def onto_calc_add(body: dict = Body(...)):
    onto.add_calc(body["obj"], body["col"], body.get("label") or body["col"], body["calc"])
    return {"ok": True}


@app.delete("/api/onto/calc/{obj}/{col}")
def onto_calc_del(obj: str, col: str):
    onto.remove_calc(obj, col)
    return {"ok": True}


@app.post("/api/onto/er/run")
def onto_er_run(body: dict = Body(...)):
    return onto.er_run(body["a"], body["b"], body.get("pairs", []), body.get("how", "loose"))


@app.post("/api/onto/er/apply")
def onto_er_apply(body: dict = Body(...)):
    return onto.er_apply(body["a"], body["b"], body.get("matches", []), body.get("pairs", []), body.get("how", "loose"))


@app.post("/api/onto/intent")
def onto_intent(body: dict = Body(...)):
    onto.set_intent(body["text"])
    return {"ok": True}


@app.post("/api/onto/intent/draft")
def onto_intent_draft():
    return {"text": onto.draft_intent()}


# ── 문서 읽기 ──
@app.get("/api/docs")
def docs_list():
    return docs.listing()


@app.get("/api/docs/{did}/image")
def doc_img(did: str, page: int = 1):
    u = me()
    if u and u["role"] == "현업":
        raise HTTPException(403, "원본 그림에는 민감 정보가 있을 수 있어 현업에게는 보여 주지 않습니다.")
    p = docs.image_path(did, page)
    if not p or not p.exists():
        raise HTTPException(404, "이미지가 없습니다.")
    return FileResponse(p)


@app.get("/api/docs/{did}/values")
def doc_vals(did: str):
    vs = docs.values(did)
    u = me()
    if u and u["role"] == "현업":
        sens = {r["col"] for r in db.rows("SELECT col FROM prop WHERE obj='doc_extract' AND sensitive=1")}
        vs = [{**v, "value": "●●●" if v["field"] in sens and v["value"] else v["value"]} for v in vs]
    return vs


@app.get("/api/docs/{did}/text")
def doc_text(did: str):
    return [{**t, "text": qa.mask_text(t["text"], me())} for t in docs.text_of(did)]


@app.get("/api/search")
def search(q: str, obj: str = "", value: str = "", k: int = 8):
    """본문 검색. 개체 · 값을 주면 그 값에 관계로 이어진 문서 안에서만(그래프로 거르고 벡터로 고름)."""
    ids, via = None, None
    if obj and value:
        o = next((x for x in onto.objects() if x["name"] == obj), None)
        if not o:
            raise HTTPException(404, "개체가 없습니다.")
        g = graph.gather(obj, o["key"], value, depth=3)
        ids = sorted({str(r["doc_id"]) for rs in g["got"].values() for r in rs if r.get("doc_id")})
        via = {"obj": o["label"], "value": value, "docs": ids}
    hits = [{**h, "text": qa.mask_text(h["text"], me())} for h in docs.search(q, ids, k)]
    return {"hits": hits, "via": via, "mode": docs.search_mode()}


@app.post("/api/fields")
def field_add(body: dict = Body(...)):
    docs.add_field(body.get("name", ""), body.get("label", ""), body.get("desc", ""))
    return {"ok": True}


@app.get("/api/fields/suggest")
def field_suggest(refresh: int = 0):
    return docs.suggest_fields(bool(refresh))


@app.post("/api/fields/bulk")
def field_bulk(body: dict = Body(...)):
    return {"added": docs.add_fields(body.get("items", []))}


@app.delete("/api/fields/{name}")
def field_del(name: str):
    docs.remove_field(name)
    return {"ok": True}


@app.post("/api/read")
def read(body: dict = Body({})):
    return docs.read_all(body.get("only"))


@app.get("/api/review")
def review():
    return docs.review_list()


@app.post("/api/review/fix")
def review_fix(body: dict = Body(...)):
    docs.fix(body["doc_id"], body["field"], body["value"])
    return {"ok": True}


# ── 규칙 ──
@app.get("/api/rules")
def rule_list():
    return rules.listing()


@app.post("/api/rules/compile")
def rule_compile(body: dict = Body(...)):
    return rules.compile_text(body["text"], body.get("kind", "판단"))


@app.post("/api/rules")
def rule_add(body: dict = Body(...)):
    return {"id": rules.add(body)}


@app.delete("/api/rules/{rid}")
def rule_del(rid: int):
    rules.remove(rid)
    return {"ok": True}


@app.post("/api/rules/{rid}/toggle")
def rule_toggle(rid: int, body: dict = Body(...)):
    rules.toggle(rid, bool(body.get("on")))
    return {"ok": True}


@app.post("/api/rules/{rid}/test")
def rule_test(rid: int):
    r = rules.test(rid)
    # 시작 개체의 계산 속성을 쓰는 규칙이면 걸린 건 앞 3건의 계산 과정도 같이
    ru = next((x for x in rules.listing() if x["id"] == rid), None)
    st = ru["cond"]["start"] if ru else None
    cc = set(whatif.calc_cols(st)) if st else set()
    used = sorted({w["col"] for w in ru["cond"].get("when", []) if w.get("obj") == st and w.get("col") in cc}) if ru else []
    if used:
        r["calc"] = [{"key": k, "items": whatif.mask_items(whatif.explain(st, k, used), me())} for k in r["hits"][:3]]
    return r


@app.post("/api/rules/run_all")
def rule_run_all(body: dict = Body(...)):
    return rules.run_all(body["start"])


# ── 지표 ──
@app.get("/api/metrics")
def metric_list():
    return qa.metrics()


@app.post("/api/metrics/compile")
def metric_compile(body: dict = Body(...)):
    return qa.metric_compile(body.get("text", ""))


@app.post("/api/metrics")
def metric_add(body: dict = Body(...)):
    return {"id": qa.metric_add({k: body.get(k) for k in ("name", "text", "spec")})}


@app.delete("/api/metrics/{mid}")
def metric_del(mid: int):
    qa.metric_remove(mid)
    return {"ok": True}


@app.post("/api/metrics/{mid}/run")
def metric_run(mid: int):
    return qa.metric_run(mid, me())


# ── 질문 · 골든 질문 ──
@app.post("/api/ask")
def ask(body: dict = Body(...)):
    return qa.ask(body["q"], me())


@app.get("/api/asks")
def asks():
    u = me()
    return qa.asks(who=u["name"] if u and u["role"] == "현업" else None)


@app.get("/api/asks/{aid}")
def ask_one(aid: int):
    r = qa.ask_detail(aid)
    if not r:
        raise HTTPException(404, "질문 기록이 없습니다.")
    return r


@app.get("/api/agent")
def agent_get():
    return qa.agent()


@app.post("/api/agent/instr")
def agent_instr(body: dict = Body(...)):
    qa.set_instr(body.get("text", ""))
    return {"ok": True}


@app.delete("/api/agent/templates/{name}")
def agent_tpl_del(name: str):
    qa.tpl_remove(name)
    return {"ok": True}


@app.get("/api/golden")
def golden():
    return qa.golden()


@app.post("/api/golden")
def golden_add(body: dict = Body(...)):
    return {"id": qa.golden_add(body.get("q", ""), body.get("want", ""))}


@app.delete("/api/golden/{gid}")
def golden_del(gid: int):
    qa.golden_remove(gid)
    return {"ok": True}


@app.post("/api/golden/{gid}/vote")
def golden_vote(gid: int, body: dict = Body(...)):
    qa.golden_vote(gid, body.get("vote"))
    return {"ok": True}


@app.post("/api/golden/run")
def golden_run():
    return qa.golden_run()


# ── 데이터 탐색 ──
@app.get("/api/explore")
def explore(obj: str, value: str):
    o = next((x for x in onto.objects() if x["name"] == obj), None)
    if not o:
        raise HTTPException(404, "개체가 없습니다.")
    r = graph.explore(obj, o["key"], value)
    for n in r["nodes"]:
        n["row"] = qa.mask(n["tbl"], [n["row"]], me())[0]
    return r


# ── 변경 이력 ──
@app.get("/api/changes")
def changes():
    return {"items": history.listing(), "today": history.today(), "current": history.current()}


@app.post("/api/changes/{cid}/approve")
def ch_approve(cid: int):
    return history.approve(cid, me())


@app.post("/api/changes/{cid}/reject")
def ch_reject(cid: int, body: dict = Body({})):
    history.reject(cid, body.get("reason", ""), me())
    return {"ok": True}


@app.post("/api/changes/{cid}/rollback")
def ch_rollback(cid: int):
    return {"id": history.rollback_request(cid)}


# ── Copilot ──
@app.post("/api/chat")
def chat_(body: dict = Body(...)):
    return chat.reply(body.get("text", ""), body.get("page", ""), me())


@app.post("/api/chat/propose")
def chat_propose(body: dict = Body(...)):
    return {"id": chat.propose(body["title"], body["layer"], body["op"], body.get("lines", []))}


# ── 개발용: 자동 새로 고침 · 목업 ──
MOCK = Path.home() / "Project" / "20261104_GenO_목업.html"


@app.get("/api/dev/stamp")
def dev_stamp():
    fs = list(WEB.rglob("*")) + ([MOCK] if MOCK.exists() else [])
    return {"stamp": max((f.stat().st_mtime for f in fs if f.is_file()), default=0)}


@app.get("/mock")
def mock():
    """목업 HTML 한 장을 그대로 보여 줌(+ 자동 새로 고침). 파일 자체는 서버 없이도 열림."""
    if not MOCK.exists():
        raise HTTPException(404, "목업 파일이 없습니다.")
    # 목업은 fetch를 가짜 서버로 바꿔 쓰므로, 새로 고침 확인은 XHR로 진짜 서버에 물음
    live = ("<script>(()=>{let s=null;setInterval(()=>{const x=new XMLHttpRequest();x.open('GET','/api/dev/stamp');"
            "x.onload=()=>{try{const t=JSON.parse(x.responseText).stamp;if(s&&t!==s)location.reload();s=t}catch(e){}};x.send()},1500)})()</script>")
    from fastapi.responses import HTMLResponse
    return HTMLResponse(MOCK.read_text(encoding="utf-8").replace("</body>", live + "</body>"))


app.mount("/web", StaticFiles(directory=WEB, html=True), name="web")
