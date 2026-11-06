"""LLM 없이 도는 부분 시험 — 시험용 데이터는 tests 안에서 만들고 지움(저장소는 임시 폴더)."""
import importlib
import sqlite3

import pytest


@pytest.fixture()
def app(tmp_path, monkeypatch):
    monkeypatch.setenv("GENO_DATA", str(tmp_path / "data"))
    monkeypatch.setenv("GENO_LLM_OFF", "1")
    import geno.db
    importlib.reload(geno.db)
    import geno.history, geno.sources, geno.onto, geno.docs, geno.graph, geno.rules, geno.qa, geno.whatif, geno.examples
    for m in (geno.history, geno.sources, geno.onto, geno.docs, geno.graph, geno.rules, geno.qa, geno.whatif, geno.examples):
        importlib.reload(m)
    return geno, tmp_path


CUST = b"customer_id,name\nC1,Kim\nC2,Lee\n"
ORD = b"order_id,customer_id,amount,ordered_on\nO1,C1,100,2026-01-02\nO2,C1,250,2026-02-03\nO3,C2,90,2026-03-04\n"


def test_empty_start(app):
    g, _ = app
    assert g.sources.listing() == [] and g.onto.view()["objects"] == [] and g.docs.fields() == []


def test_csv_db_draft_rules_history(app):
    g, tmp = app
    g.sources.add_files("판매", [("customer.csv", CUST), ("orders.csv", ORD)])
    # SQLite DB 연결(읽기만)
    p = tmp / "shop.db"
    c = sqlite3.connect(p)
    c.execute("CREATE TABLE refund (refund_id TEXT, order_id TEXT, reason TEXT)")
    c.execute("INSERT INTO refund VALUES ('R1','O2','파손')")
    c.commit(); c.close()
    t = g.sources.db_test({"kind": "sqlite", "path": str(p)}, None)
    assert t["tables"][0]["name"] == "refund" and t["tables"][0]["rows"] == 1
    g.sources.db_add("환불 DB", {"kind": "sqlite", "path": str(p)}, None, ["refund"])
    assert set(g.sources.table_names()) == {"customer", "orders", "refund"}
    # 설계(규칙 기반 초안): orders.customer_id → customer, refund.order_id → orders
    d = g.onto.draft()
    assert d["relations"] == 2
    v = g.onto.view()
    assert all(r["ov"]["hit"] == r["ov"]["a"] for r in v["relations"])
    # 길 따라가기
    got = g.graph.gather("refund", "refund_id", "R1", targets=["customer"])
    assert got["got"]["customer"][0]["name"] == "Kim" and not got["missing"]
    # 규칙: 환불 사유가 파손이고 주문 금액 > 200 이면 확인
    rid = g.rules.add({"kind": "판단", "name": "큰 파손 환불", "text": "파손 환불이 200 넘으면 확인", "start": "refund",
                       "when": [{"obj": "refund", "col": "reason", "op": "=", "value": "파손"},
                                {"obj": "orders", "col": "amount", "op": ">", "value": "200"}], "then": "확인 필요"})
    assert g.rules.test(rid)["hits"] == ["R1"]
    # 관계 지우면 규칙은 길 끊김
    rel = next(r for r in g.onto.relations() if r["a_tbl"] == "refund")
    v_before = g.history.current()
    g.onto.remove_relation(rel["id"])
    assert not g.rules.listing()[0]["check"]["ok"]
    # Copilot 제안 → 승인해야 적용
    cid = g.history.propose("관계 추가", "개체 · 관계", {"type": "add_rel", "rel": {"a_tbl": "refund", "a_col": "order_id", "b_tbl": "orders", "b_col": "order_id"}}, {})
    assert g.history.pending_count() == 1 and g.rules.listing()[0]["check"]["ok"] is False
    g.history.approve(cid)
    assert g.rules.listing()[0]["check"]["ok"]
    # 되돌리기도 승인 거침
    rb = g.history.rollback_request(v_before)
    g.history.approve(rb)
    assert len(g.onto.relations()) == 2
    # 데이터 탐색
    e = g.graph.explore("customer", "customer_id", "C1")
    assert any(n["tbl"] == "orders" for n in e["nodes"]) and e["edges"]


def test_doc_review_links(app):
    g, _ = app
    g.sources.add_files("병원", [("hospital.csv", "hospital_name\n누리병원\n한별병원\n".encode())])
    g.sources.add_files("문서", [("D1.png", b"\x89PNG fake")])
    g.docs.add_field("hospital_name", "병원 이름", "병원 이름 그대로")
    con = g.db.connect()
    con.execute("UPDATE doc SET read_at=1, doc_type='영수증', lying=0")
    con.execute("INSERT INTO ext VALUES ('D1','hospital_name','누리병언',0.97,'AI',1)")
    g.docs._rebuild_table()
    g.onto.draft()
    g.onto.add_relation("doc_extract", "hospital_name", "hospital", "hospital_name")
    rv = g.docs.review_list()
    assert rv and "hospital.hospital_name에 없는 값" in rv[0]["why"] and rv[0]["fix"] == "누리병원"
    g.docs.fix("D1", "hospital_name", "누리병원")
    assert g.docs.review_list() == []


def test_reset(app):
    g, _ = app
    g.sources.add_files("x", [("a.csv", CUST)])
    g.db.reset()
    assert g.sources.listing() == [] and g.history.listing() == []


def test_object_layer_set_metric_rules(app):
    """개체 정의 층(조건 개체 · 계산 속성 · 키 점검) + 여러 건 계산 + 지표 + 전체 판정."""
    g, _ = app
    g.sources.add_files("판매", [("customer.csv", CUST + b"C3,Kim\n"), ("orders.csv", ORD)])
    g.onto.draft()
    # 한 표에서 조건으로 개체 하나 더(큰 주문)
    r = g.onto.add_object("큰 주문", "orders", [{"col": "amount", "op": ">", "value": "200"}], "order_id")
    assert r["nrows"] == 1
    # 계산 속성: 고객의 주문 건수(이어진 줄 집계) → 같은 줄 계산
    g.onto.add_calc("customer", "order_count", "주문 건수", {"kind": "agg", "obj": "orders", "fn": "count", "col": "", "where": []})
    g.onto.add_calc("customer", "is_regular", "단골", {"kind": "expr", "sql": 'CASE WHEN "order_count" >= 2 THEN \'예\' ELSE \'아니오\' END'})
    rows = {x["customer_id"]: x for x in g.onto.sample("customer", 5)}
    assert rows["C1"]["order_count"] == 2 and rows["C1"]["is_regular"] == "예" and rows["C2"]["order_count"] == 1
    # 키 점검 — 이름은 겹침(Kim 2명)
    assert g.onto.key_check("customer", "customer_id")["ok"] and not g.onto.key_check("customer", "name")["ok"]
    # 관계 짝 수
    rel = next(x for x in g.onto.view()["relations"] if x["a_tbl"] == "orders")
    assert rel["card"] == "N:1"
    # 여러 건 계산 — 고객 이름별 주문 금액 합계: 동명이인(Kim C1 · C3)은 따로
    res = g.qa.run_set({"target": "orders", "group": {"obj": "customer", "col": "name"}, "measure": {"fn": "sum", "obj": "orders", "col": "amount"}})
    assert {x["grp"]: x["val"] for x in res["rows"]} == {"Kim": 350, "Lee": 90}
    res = g.qa.run_set({"target": "orders", "filters": [{"obj": "customer", "col": "name", "op": "=", "value": "Kim"}], "measure": {"fn": "count"}})
    assert res["rows"][0]["val"] == 2
    # 지표 저장 · 실행
    mid = g.qa.metric_add({"name": "고객별 주문 금액", "text": "고객별 주문 금액 합계", "spec": {"target": "orders", "group": {"obj": "customer", "col": "customer_id"}, "measure": {"fn": "sum", "obj": "orders", "col": "amount"}}})
    assert g.qa.metric_run(mid)["rows"][0] == {"grp": "C1", "val": 350}
    # 규칙이 계산 속성을 씀 → 전체 판정 결과가 개체로 저장
    g.rules.add({"kind": "판단", "name": "단골", "text": "주문 2건 이상이면 단골", "start": "customer",
                 "when": [{"obj": "customer", "col": "order_count", "op": ">=", "value": "2"}], "then": "단골 혜택"})
    ra = g.rules.run_all("customer")
    assert ra["total"] == 3 and ra["rules"][0]["hits"] == 1
    assert "result_customer" in {o["name"] for o in g.onto.objects()}
    # 되돌리기 스냅숏에 속성 · 지표가 들어감
    snap = g.history.snapshot()
    assert any(p["col"] == "order_count" for p in snap["prop"]) and snap["metric"]


def test_entity_resolution_and_mask(app):
    g, _ = app
    g.sources.add_files("고객", [("crm.csv", b"cid,name,birth\nA1,Kim Min,1990-01-01\nA2,Lee,1985-02-02\n"),
                                 ("shop.csv", b"sid,full_name,dob\nS1,kim-min,1990-01-01\nS2,Park,1970-03-03\n")])
    g.onto.draft()
    r = g.onto.er_run("crm", "shop", [["name", "full_name"], ["birth", "dob"]], "loose")
    assert [(p["a_key"], p["b_key"]) for p in r["pairs"]] == [("A1", "S1")]
    assert g.onto.er_run("crm", "shop", [["name", "full_name"]], "exact")["total"] == 0
    g.onto.er_apply("crm", "shop", r["pairs"], [["name", "full_name"], ["birth", "dob"]], "loose")
    got = g.graph.gather("crm", "cid", "A1", targets=["shop"])
    assert got["got"]["shop"][0]["sid"] == "S1" and not got["missing"]
    # 민감 속성은 현업에게 가림
    g.onto.save_def("crm", {"label": "CRM 고객", "key": "cid", "props": [{"col": "birth", "label": "생일", "sensitive": True}]})
    rs = g.onto.sample("crm", 1)
    assert g.qa.mask("crm", rs, {"role": "현업"})[0]["birth"] == "●●●" and g.qa.mask("crm", rs, {"role": "구축 담당"})[0]["birth"] == "1990-01-01"
    assert "●" in g.qa.mask_text("주민번호 900101-1234567", {"role": "현업"})


def test_users_permissions(app, monkeypatch):
    g, _ = app
    import geno.users
    importlib.reload(geno.users)
    import server
    importlib.reload(server)
    from fastapi.testclient import TestClient
    c = TestClient(server.app)
    assert c.get("/api/me").json()["setup"] is True
    admin = c.post("/api/users", json={"name": "관리", "role": "관리자"}).json()["id"]
    h = lambda uid: {"X-GenO-User": str(uid)}  # noqa: E731
    fd = c.post("/api/users", json={"name": "구축", "role": "구축 담당"}, headers=h(admin)).json()["id"]
    biz = c.post("/api/users", json={"name": "현업", "role": "현업"}, headers=h(admin)).json()["id"]
    assert c.post("/api/onto/intent", json={"text": "x"}, headers=h(biz)).status_code == 403
    assert c.get("/api/sources", headers=h(biz)).status_code == 403
    assert c.post("/api/onto/intent", json={"text": "판매 분석"}, headers=h(fd)).status_code == 200
    assert c.get("/api/changes", headers=h(admin)).json()["items"][0]["by"] == "구축"  # 누가 바꿨는지 남음
    assert c.post("/api/users", json={"name": "x", "role": "현업"}, headers=h(fd)).status_code == 403


def test_calc_explain_and_whatif(app):
    """계산 과정 펼쳐 보기(식 · 들어간 값 · 출처 · 예상) + 가정 바꿔 보기(원본은 그대로)."""
    g, _ = app
    g.sources.add_files("판매", [("customer.csv", CUST), ("orders.csv", ORD + b"O4,C2,,2026-03-05\n")])
    g.onto.draft()
    g.onto.add_calc("customer", "order_sum", "주문 금액 합계", {"kind": "agg", "obj": "orders", "fn": "sum", "col": "amount", "where": [], "text": "고객의 주문 금액 합계"})
    g.onto.add_calc("orders", "vat", "부가세", {"kind": "expr", "sql": 'CAST("amount" AS REAL) * 0.1'})
    ex = {x["col"]: x for x in g.whatif.explain("customer", "C1")}
    s = ex["order_sum"]
    assert s["result"] == 350 and len(s["inputs"]) == 2 and all(i["state"] == "확정" for i in s["inputs"]) and not s["estimated"]
    assert s["inputs"][0]["src"].startswith("orders")
    # 빈 값이 들어가면 "예상"
    v = {x["col"]: x for x in g.whatif.explain("orders", "O4")}["vat"]
    assert v["estimated"] and v["inputs"][0]["state"] == "빈 값"
    assert "값 넣기" in v["steps"][0]
    # 규칙: 주문 금액 합계 300 이상
    g.rules.add({"kind": "판단", "name": "큰 고객", "text": "주문 금액 합계 300 이상", "start": "customer",
                 "when": [{"obj": "customer", "col": "order_sum", "op": ">=", "value": "300"}], "then": "확인"})
    # 가정: O3(C2) 금액 90 → 400 이면 C2 합계 90 → 400, 규칙에 C2가 새로 걸림
    r = g.whatif.run([{"obj": "orders", "key": "O3", "col": "amount", "value": "400"}])
    c2 = next(c for c in r["calcs"] if c["obj"] == "customer" and c["key"] == "C2" and c["col"] == "order_sum")
    assert c2["before"] == 90 and c2["after"] == 400 and c2["changed"]
    rule = r["rules"][0]
    assert rule["before"] == 1 and rule["after"] == 2 and rule["added"] == ["C2"]
    # 원본은 그대로
    assert {x["customer_id"]: x for x in g.onto.sample("customer", 5)}["C2"]["order_sum"] == 90
    # 계산 속성은 직접 바꿀 수 없음 · 없는 대상은 오류
    with pytest.raises(ValueError):
        g.whatif.run([{"obj": "customer", "key": "C1", "col": "order_sum", "value": "1"}])
    with pytest.raises(ValueError):
        g.whatif.run([{"obj": "orders", "key": "X9", "col": "amount", "value": "1"}])
    # 저장 · 목록 · 삭제
    sid = g.whatif.save("O3 금액을 400으로", r["changes"], r)
    assert g.whatif.listing()[0]["name"] == "O3 금액을 400으로"
    g.whatif.remove(sid)
    assert g.whatif.listing() == []


def test_examples_from_data(app):
    """누르면 해 보는 예시 — 지금 데이터로 만들고, What-if 예시는 실제로 결과가 달라지는 것만."""
    g, _ = app
    assert g.examples.build(True)["agent"] == []  # 데이터가 없으면 빈 목록(칩 숨김)
    g.sources.add_files("판매", [("customer.csv", CUST + b"C3,Park\n"), ("orders.csv", b"order_id,customer_id,amount,channel,ordered_on\nO1,C1,100,web,2026-01-02\nO2,C1,250,shop,2026-02-03\nO3,C2,90,web,2026-03-04\nO4,C3,40,web,2026-03-05\n")])
    g.onto.draft()
    g.onto.add_calc("orders", "vat", "부가세", {"kind": "expr", "sql": 'CAST("amount" AS REAL) * 0.1'})
    g.rules.add({"kind": "판단", "name": "큰 주문", "text": "금액 200 이상", "start": "orders",
                 "when": [{"obj": "orders", "col": "amount", "op": ">=", "value": "200"}], "then": "확인"})
    d = g.examples.build(True)
    kinds = {x["kind"] for x in d["agent"]}
    assert {"집계", "계산 속성", "규칙 판정"} <= kinds
    assert d["whatif"] and all("계산 속성" in x["effect"] for x in d["whatif"])
    r = g.whatif.run([{k: d["whatif"][0][k] for k in ("obj", "key", "col", "value")}])
    assert any(c["changed"] for c in r["calcs"]) or any(x.get("changed") for x in r["rules"])


def test_examples_no_english_names(app):
    """예시 문장 · 속성 이름에 영어 칸 이름(소문자 3자 이상)이 보이지 않음 — 업무 이름이 없어도 한글 임시 이름으로."""
    import re
    g, _ = app
    g.sources.add_files("판매", [("customer.csv", CUST + b"C3,Park\n"), ("orders.csv", b"order_id,customer_id,amount,sales_channel,ordered_on\nO1,C1,100,web,2026-01-02\nO2,C1,250,shop,2026-02-03\nO3,C2,90,web,2026-03-04\nO4,C3,40,web,2026-03-05\n")])
    g.onto.draft()
    g.onto.add_calc("orders", "vat", "부가세", {"kind": "expr", "sql": 'CAST("amount" AS REAL) * 0.1'})
    g.rules.add({"kind": "판단", "name": "큰 주문", "text": "금액 200 이상", "start": "orders",
                 "when": [{"obj": "orders", "col": "amount", "op": ">=", "value": "200"}], "then": "확인"})
    labs = {p["col"]: p["label"] for p in next(o for o in g.onto.objects() if o["name"] == "orders")["props"]}
    assert labs["ordered_on"] == "주문일" and labs["sales_channel"] == "채널" or labs["sales_channel"].endswith("채널")
    d = g.examples.build(True)
    texts = [x["q"] for x in d["agent"]] + [x["label"] for x in d["objects"]] + [f"{x['obj_label']} {x['label']}" for x in d["whatif"]]
    # 영어 낱말(소문자 3자 이상) 중 칸 이름 · 테이블 이름인 것이 없어야 함(데이터 값 web 같은 것은 그대로 둠)
    names = {c for t in g.sources.table_names() for c in g.sources.table(t)["cols"]} | set(g.sources.table_names())
    leaked = [w for t in texts for w in re.findall(r"[a-z_]{3,}", t) if w in names]
    assert texts and not leaked, (leaked, texts)
