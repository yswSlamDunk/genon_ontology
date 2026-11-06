"""문서 읽기 — 올린 스캔본 · PDF(모든 쪽, 최대 10쪽)에서 사람이 정한 칸을 LLM(그림 읽기)으로 뽑음.
본문도 쪽마다 글자로 남겨 조각(chunk)으로 나누고 임베딩 → "그래프로 거르고(이어진 문서만) 벡터로 고르기" 검색에 씀.

읽을 칸은 처음에 하나도 없음 — 사람이 정함(무엇을 읽을지 알려 줘야 AI가 잘 뽑음).
읽은 값은 "doc_extract" 표(개체 이름 "읽은 값")로 저장 → 다른 표와 관계를 이을 수 있음(doc_key = 파일 이름 첫 "_" 앞).
검수 목록 = AI 확신도 0.8 미만 · 옆으로 누운 문서 · 이어 둔 표에 없는 값(AI 확신도는 틀린 값에도 높게 나와서).
"""
import difflib
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import history, llm, sources
from .db import clean_name, DATA, connect, dt, now, one, ot, q, rows

EXTRACT = "doc_extract"
MAX_PAGES = 10


def _dirs():
    for d in ("files", "pages"):
        (DATA / d).mkdir(parents=True, exist_ok=True)
    return DATA / "files", DATA / "pages"


def store(sid: int, files: list[tuple[str, bytes]]) -> list[str]:
    fdir, pdir = _dirs()
    ids = []
    con = connect()
    for fname, b in files:
        stem = Path(fname).stem
        did, i = stem, 2
        while one("SELECT 1 FROM doc WHERE id=?", (did,)):
            did, i = f"{stem}-{i}", i + 1
        ext = Path(fname).suffix.lower()
        (fdir / f"{did}{ext}").write_bytes(b)
        pages = 1
        if ext == ".pdf":
            import pypdfium2 as pdfium
            pdf = pdfium.PdfDocument(b)
            pages = len(pdf)
            for i in range(min(pages, MAX_PAGES)):
                out = pdir / (f"{did}.png" if i == 0 else f"{did}-p{i + 1}.png")
                pdf[i].render(scale=2).to_pil().save(out) if _has_pil() else _render_raw(pdf, out, i)
                txt = pdf[i].get_textpage().get_text_range().strip()
                if txt:  # 글자가 들어 있는 PDF면 쪽 글자를 그대로 씀(그림 읽기 없이)
                    (pdir / f"{did}-p{i + 1}.txt").write_text(txt, encoding="utf-8")
        con.execute("INSERT INTO doc (id, file, source_id, pages) VALUES (?,?,?,?)", (did, f"{did}{ext}", sid, pages))
        ids.append(did)
    return ids


def _has_pil() -> bool:
    try:
        import PIL  # noqa: F401
        return True
    except ImportError:
        return False


def _render_raw(pdf, out: Path, i: int = 0) -> None:
    """PIL 없이 PDF 한 쪽을 PNG로 — pypdfium2 비트맵을 직접 PNG로 씀."""
    import struct
    import zlib
    bm = pdf[i].render(scale=2, rev_byteorder=True)
    w, h, stride = bm.width, bm.height, bm.stride
    buf = bytes(bm.buffer)
    n = bm.n_channels
    raw = b"".join(b"\x00" + buf[y * stride:y * stride + w * n] for y in range(h))
    ctype = {3: 2, 4: 6, 1: 0}[n]

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    out.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, ctype, 0, 0, 0))
                    + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b""))


def image_path(did: str, page: int = 1) -> Path | None:
    d = one("SELECT * FROM doc WHERE id=?", (did,))
    if not d:
        return None
    fdir, pdir = _dirs()
    if not d["file"].lower().endswith(".pdf"):
        r = pdir / f"{did}.png"  # 돌려 놓은 그림이 있으면 그것을 씀(원본 파일은 그대로)
        return r if d["rot"] and r.exists() else fdir / d["file"]
    return pdir / (f"{did}.png" if page == 1 else f"{did}-p{page}.png")


def page_images(did: str) -> list[Path]:
    d = one("SELECT pages FROM doc WHERE id=?", (did,))
    n = min(d["pages"] or 1, MAX_PAGES) if d else 1
    return [p for p in (image_path(did, i + 1) for i in range(n)) if p and p.exists()]


def remove_source(sid: int) -> None:
    con = connect()
    for d in rows("SELECT id FROM doc WHERE source_id=?", (sid,)):
        for p in page_images(d["id"]) + [DATA / "files" / one("SELECT file FROM doc WHERE id=?", (d["id"],))["file"]] + list((DATA / "pages").glob(f"{d['id']}-p*.txt")):
            if p and p.exists():
                p.unlink()
        con.execute("DELETE FROM ext WHERE doc_id=?", (d["id"],))
        con.execute("DELETE FROM chunk WHERE doc_id=?", (d["id"],))
        con.execute("DELETE FROM doc WHERE id=?", (d["id"],))
    _rebuild_table()


# ── 읽을 칸 ──
def fields() -> list[dict]:
    return rows("SELECT name, label, desc FROM field ORDER BY ord, name")


def insert_field(f: dict) -> None:
    n = one("SELECT COALESCE(MAX(ord),0)+1 n FROM field")["n"]
    connect().execute("INSERT OR REPLACE INTO field VALUES (?,?,?,?,?)", (f["name"], f.get("label") or f["name"], f.get("desc", ""), n, now()))


def add_field(name: str, label: str, desc: str) -> None:
    name = name.strip()
    if not name:
        raise ValueError("칸 이름을 입력해 주세요.")
    insert_field({"name": name, "label": label, "desc": desc})
    history.record(f"읽을 칸 추가 · {label or name}", "읽을 칸", "사람", {"add": name, "desc": desc})


def suggest_fields(refresh: bool = False) -> dict:
    """읽을 칸 추천 — 이미 읽은 본문(문서 종류마다 2건)을 보고 AI가 칸 후보를 냄. 사람이 눌러서 추가(Fabric ai.infer_schema처럼).
    다른 테이블과 이을 수 있는 칸은 그 테이블의 열 이름을 그대로 씀. 결과는 문서 수가 같으면 다시 묻지 않음."""
    from . import sources
    from .db import kv_get, kv_set
    ds = rows("SELECT id, doc_type FROM doc WHERE read_at IS NOT NULL ORDER BY id")
    have = {f["name"] for f in fields()}
    if not ds:
        return {"items": [], "why": "문서를 한 번 읽으면(읽을 칸 없이도) 본문을 보고 칸을 추천합니다."}
    sig = f"{len(ds)}:{','.join(sorted({d['doc_type'] or '' for d in ds}))}"
    cache = kv_get("field_suggest")
    if cache and cache.get("sig") == sig and not refresh:
        return {"items": [x for x in cache["items"] if x["name"] not in have], "why": ""}
    if not llm.available():
        return {"items": [], "why": "LLM이 연결되지 않아 추천할 수 없습니다."}
    by_type: dict[str, list[str]] = {}
    for d in ds:
        by_type.setdefault(d["doc_type"] or "기타", []).append(d["id"])
    samples = []
    for t, ids in list(by_type.items())[:8]:
        for did in ids[:2]:
            txt = "\n".join(c["text"] for c in text_of(did))[:1500]
            if txt:
                samples.append(f"[{t} · {did}]\n{txt}")
    if not samples:
        return {"items": [], "why": "읽은 본문이 없습니다. 문서 탭에서 읽기를 실행해 주세요."}
    cols = sorted({c for t in sources.table_names() if t != EXTRACT for c in (sources.table(t) or {}).get("cols", [])})
    d = llm.chat_json(
        "문서 본문들을 보고, 문서에서 뽑아 표로 만들 칸 후보를 낸다(최대 12개). 업무에 쓸 값만(날짜 · 금액 · 코드 · 번호 · 이름 · 진단명 등), 작성자 전화 · 서식 번호 같은 잡다한 칸은 뺀다. "
        "다른 테이블에 뜻이 똑같은 열이 있을 때만 그 열 이름을 name에 그대로 쓴다(예: 진단서의 질병분류기호 = disease_code). 이름만 비슷하고 뜻이 다르면(예: 고지 답변일 ≠ 진단일, answer ≠ 청구 사유) 새 이름을 짓는다. desc에는 뜻과 형식을 적는다(예: '실제 진단일. 발급일 아님. YYYY-MM-DD'). "
        '형식: {"items":[{"name":"영문 소문자_밑줄","label":"한국어 이름","desc":"뜻 · 형식","types":["이 칸이 있는 문서 종류"],"example":"본문에서 본 값 하나","link":"이을 수 있는 열 이름 또는 빈 글자"}]}',
        f"이미 있는 테이블 열 이름: {', '.join(cols[:200])}\n이미 정한 칸: {', '.join(sorted(have)) or '(없음)'}\n\n" + "\n\n".join(samples))
    items = []
    for x in d.get("items") or []:
        n = clean_name(str(x.get("name") or ""))
        if not n or n in have or any(i["name"] == n for i in items):
            continue
        items.append({"name": n, "label": str(x.get("label") or n)[:30], "desc": str(x.get("desc") or "")[:200],
                      "types": [str(t) for t in (x.get("types") or [])][:5], "example": str(x.get("example") or "")[:60],
                      "link": ", ".join(t for t in sources.table_names() if t != EXTRACT and n in (sources.table(t) or {}).get("cols", []))[:80]})
    kv_set("field_suggest", {"sig": sig, "items": items})
    return {"items": items, "why": ""}


def add_fields(items: list[dict]) -> int:
    n = 0
    for x in items:
        if x.get("name") and x["name"] not in {f["name"] for f in fields()}:
            insert_field({"name": x["name"], "label": x.get("label", ""), "desc": x.get("desc", "")})
            n += 1
    if n:
        history.record(f"읽을 칸 {n}개 추가 · AI 추천", "읽을 칸", "사람", {"add": ", ".join(x.get("label", "") for x in items)[:300]})
    return n


def remove_field(name: str) -> None:
    connect().execute("DELETE FROM field WHERE name=?", (name,))
    history.record(f"읽을 칸 삭제 · {name}", "읽을 칸", "사람", {"remove": name})


# ── 읽기 ──
def _read_one(d: dict, fl: list[dict]) -> dict:
    spec = "\n".join(f"- {f['name']}: {f['label']} — {f['desc']}" for f in fl)
    imgs = page_images(d["id"])
    sysm = (f"문서 그림 {len(imgs)}쪽에서 정해진 칸을 읽는다(여러 쪽이면 모든 쪽을 보고). 없는 칸은 빈 글자. 날짜는 YYYY-MM-DD, 금액은 숫자만. conf는 0~1 사이 너의 확신도. "
            "글자가 옆으로(90도) 눕거나 거꾸로(180도) 뒤집혔을 때만 lying=true(몇 도 기울어진 정도는 false), rotate에는 바로 세우려면 시계 방향으로 몇 도 돌려야 하는지(90 · 180 · 270, 바르면 0). pages에는 쪽마다 본문 글자를 줄바꿈 그대로 적는다(쪽마다 최대 2500자, 표는 칸을 ' | '로). "
            '형식: {"doc_type":"","lying":false,"rotate":0,"fields":{"칸 이름":{"value":"","conf":0.0}},"pages":["1쪽 글자"]}')
    try:
        r = llm.chat_json(sysm, f"읽을 칸:\n{spec}", image=imgs, timeout=240)
        return {"id": d["id"], "ok": True, "r": r}
    except Exception as e:
        return {"id": d["id"], "ok": False, "err": str(e)[:200]}


def _rot(r: dict) -> int:
    try:
        v = int(r.get("rotate") or 0) % 360
    except (TypeError, ValueError):
        return 0
    return v if v in (90, 180, 270) else 0


def _orient(did: str, order: tuple = (0, 90, 180, 270)) -> int | None:
    """방향 고르기 — 첫 쪽을 0 · 90 · 180 · 270도 돌린 4장을 한 번에 보여 주고 글자가 바로 읽히는 그림을 고르게 함.
    "누웠나?"를 따로 물으면 AI가 양쪽으로 틀려서(바로 선 것을 누웠다, 누운 것을 바르다) 비교로 정함. 돌려야 할 각도(시계 방향) 또는 None."""
    import tempfile
    from PIL import Image
    imgs = page_images(did)
    if not imgs:
        return None
    im = Image.open(imgs[0]).convert("RGB")
    im.thumbnail((700, 700))
    tmp = Path(tempfile.mkdtemp(prefix="geno_orient_"))
    paths = []
    for i, deg in enumerate(order):
        pth = tmp / f"{i + 1}.jpg"
        im.rotate(-deg, expand=True).save(pth, quality=70)
        paths.append(pth)
    try:
        d = llm.chat_json('같은 문서 그림을 네 방향으로 돌린 1~4번 그림이다. 글자가 똑바로(위에서 아래로, 왼쪽에서 오른쪽으로) 읽히는 그림 번호 하나를 고른다. 형식: {"pick":1}',
                          "1번 · 2번 · 3번 · 4번 순서로 붙였다.", image=paths, timeout=90)
        k = int(d.get("pick") or 0)
    except Exception:
        k = 0
    finally:
        for pth in paths:
            pth.unlink(missing_ok=True)
        tmp.rmdir()
    return order[k - 1] if 1 <= k <= 4 else None


def orient(did: str) -> int | None:
    """돌릴 각도 — 순서를 바꿔 두 번 물어 같을 때만 믿고, 세로 서류를 가로로 눕히는 답(90 · 270)은 받지 않음. 못 정하면 None."""
    from PIL import Image
    a, b = _orient(did), _orient(did, (180, 270, 0, 90))
    if a is None or a != b:
        return None
    try:
        w, h = Image.open(page_images(did)[0]).size
    except Exception:
        return None
    if a in (90, 270) and h > w * 1.1:  # 지금 세로 → 90° 돌리면 가로가 됨. 서류는 대개 세로라 믿지 않음
        return None
    return a


def _turn(did: str, deg: int) -> None:
    """쪽 그림을 시계 방향으로 deg도 돌려 저장. 그림 파일은 pages 폴더에(원본은 그대로)."""
    from PIL import Image
    fdir, pdir = _dirs()
    d = one("SELECT * FROM doc WHERE id=?", (did,))
    for i, src in enumerate(page_images(did)):
        out = pdir / (f"{did}.png" if i == 0 else f"{did}-p{i + 1}.png")
        Image.open(src).rotate(-deg, expand=True).save(out)
    connect().execute("UPDATE doc SET rot=? WHERE id=?", ((((d["rot"] or 0) + deg) % 360) or None, did))


def read_all(only: list[str] | None = None) -> dict:
    fl = fields() or [{"name": "_none", "label": "(칸 없음 · 본문만)", "desc": "읽지 않음"}]
    if not llm.available():
        raise ValueError("LLM 키가 없어 문서를 읽을 수 없습니다.")
    ds = rows("SELECT * FROM doc ORDER BY id")
    if only:
        ds = [d for d in ds if d["id"] in only]
    if not ds:
        raise ValueError("업로드한 문서가 없습니다.")
    t0 = time.time()
    with ThreadPoolExecutor(6) as ex:
        res = list(ex.map(lambda d: _read_one(d, fl), ds))
    # 누운 문서는 그림을 돌려 바로 세운 뒤 한 번 더 읽음(사람 검수 전에 스스로 고침)
    # 방향 확인 대상: AI가 누웠다고 본 문서 + 가로로 긴 쪽(서류는 대개 세로) → 네 방향 비교로 각도를 정함
    def wide(did):
        try:
            from PIL import Image
            w, h = Image.open(page_images(did)[0]).size
            return w > h * 1.1
        except Exception:
            return False
    turned = []
    if _has_pil():
        cand = [(i, x) for i, x in enumerate(res) if x["ok"] and (x["r"].get("lying") or wide(x["id"]))]
        with ThreadPoolExecutor(6) as ex:
            degs = list(ex.map(lambda ix: orient(ix[1]["id"]), cand))
        for (i, x), deg in zip(cand, degs):
            if deg:  # 돌려야 함
                x["r"]["rotate"] = deg
                turned.append((i, x))
            elif deg == 0:  # 이미 바름 — 누웠다는 판단은 틀린 것
                x["r"]["lying"] = False
    if turned:
        for _, x in turned:
            _turn(x["id"], _rot(x["r"]))
        with ThreadPoolExecutor(6) as ex:
            again = list(ex.map(lambda ix: _read_one(next(d for d in ds if d["id"] == ix[1]["id"]), fl), turned))
        # 돌린 그림을 다시 읽어 "바로 섰다"고 나오고 확신도가 떨어지지 않을 때만 받아들임. 아니면 그림을 원래대로 되돌림
        #  (AI가 바로 선 문서를 누웠다고 잘못 볼 때가 있어서 — 확인 없이 돌리면 오히려 눕힘)
        def conf(r):
            cs = [v.get("conf") for v in (r.get("fields") or {}).values() if isinstance(v, dict) and isinstance(v.get("conf"), (int, float))]
            return sum(cs) / len(cs) if cs else 1.0
        for (i, x), y in zip(turned, again):
            if y["ok"] and not y["r"].get("lying") and conf(y["r"]) >= conf(x["r"]) - 0.05:
                res[i] = y
            else:
                _turn(x["id"], 360 - _rot(x["r"]))
    con = connect()
    names = {f["name"] for f in fl}
    fail = 0
    for x in res:
        if not x["ok"]:
            fail += 1
            con.execute("UPDATE doc SET err=? WHERE id=?", (x["err"], x["id"]))
            continue
        r = x["r"]
        con.execute("UPDATE doc SET doc_type=?, lying=?, err=NULL, read_at=? WHERE id=?", (r.get("doc_type", ""), int(bool(r.get("lying"))), now(), x["id"]))
        for k, v in (r.get("fields") or {}).items():
            if k not in names or k == "_none":
                continue
            if one("SELECT 1 FROM ext WHERE doc_id=? AND field=? AND by='사람'", (x["id"], k)):
                continue
            v = v if isinstance(v, dict) else {"value": v, "conf": None}
            con.execute("INSERT OR REPLACE INTO ext VALUES (?,?,?,?,?,?)", (x["id"], k, str(v.get("value") or ""), v.get("conf"), "AI", now()))
        _save_text(x["id"], r.get("pages") or [])
    _rebuild_table()
    _embed_missing()
    secs = round(time.time() - t0, 1)
    history.record(f"문서 {len(ds)}건 읽기 · {secs}초", "데이터", "AI", {"docs": len(ds), "failed": fail, "secs": secs, "model": llm.info()["model"]})
    return {"docs": len(ds), "failed": fail, "secs": secs}


def _rebuild_table() -> None:
    fl = [f["name"] for f in fields()]
    ds = rows("SELECT id, file, doc_type, source_id FROM doc WHERE read_at IS NOT NULL ORDER BY id")
    if not ds:
        connect().execute(f"DROP TABLE IF EXISTS {dt(EXTRACT)}")
        connect().execute("DELETE FROM tbl WHERE name=?", (EXTRACT,))
        connect().execute("DELETE FROM obj WHERE name=?", (EXTRACT,))
        return
    vals = {(e["doc_id"], e["field"]): e["value"] for e in rows("SELECT doc_id, field, value FROM ext")}
    # doc_key = 파일 이름에서 첫 "_" 앞(예: CL-004-D2_진단서.jpg → CL-004-D2) — 회사 표의 문서 번호와 잇기 쉽게
    data = [[d["id"], re.split(r"[_ ]", d["id"])[0], d["file"], d["doc_type"] or ""] + [vals.get((d["id"], f), "") for f in fl] for d in ds]
    sources.save_table(EXTRACT, ["doc_id", "doc_key", "file_name", "doc_type"] + fl, data, ds[0]["source_id"])
    if not one("SELECT 1 FROM obj WHERE name=?", (EXTRACT,)):
        connect().execute("INSERT INTO obj (name, label, key, by, at, base) VALUES (?,?,?,?,?,?)", (EXTRACT, "읽은 값", "doc_id", "시스템", now(), EXTRACT))
    from . import onto
    onto.rebuild(EXTRACT)


# ── 결과 · 검수 ──
def _links() -> dict:
    """읽은 값 칸 → 이어 둔 (표, 열)."""
    out = {}
    for r in rows("SELECT * FROM rel WHERE a_tbl=? OR b_tbl=?", (EXTRACT, EXTRACT)):
        mine, other = ((r["a_col"], (r["b_tbl"], r["b_col"])) if r["a_tbl"] == EXTRACT else (r["b_col"], (r["a_tbl"], r["a_col"])))
        out.setdefault(mine, []).append(other)
    return out


def review_list() -> list[dict]:
    links, lab = _links(), {f["name"]: f["label"] for f in fields()}
    cache = {}
    out = []
    lying = {d["id"] for d in rows("SELECT id FROM doc WHERE lying=1")}
    for e in rows("SELECT * FROM ext WHERE by<>'사람' ORDER BY doc_id, field"):
        why, fix = [], None
        if e["conf"] is not None and e["conf"] < 0.8 and e["value"]:
            why.append(f"AI 확신도 낮음 ({e['conf']:.2f})")
        if e["doc_id"] in lying and e["value"]:
            why.append("옆으로 누운 문서")
        for t, c in links.get(e["field"], []):
            if not e["value"]:
                continue
            key = (t, c)
            if key not in cache:
                try:
                    cache[key] = [r["v"] for r in rows(f"SELECT DISTINCT {q(c)} v FROM {ot(t)}")]
                except Exception:
                    cache[key] = []
            if e["value"] not in cache[key]:
                why.append(f"{t}.{c}에 없는 값")
                m = difflib.get_close_matches(e["value"], cache[key], n=1, cutoff=0.6)
                fix = fix or (m[0] if m else None)
        if why:
            out.append({**e, "label": lab.get(e["field"], e["field"]), "why": why, "fix": fix})
    return out


def fix(doc_id: str, field: str, value: str) -> None:
    connect().execute("INSERT OR REPLACE INTO ext VALUES (?,?,?,?,?,?)", (doc_id, field, value, 1.0, "사람", now()))
    _rebuild_table()


def listing() -> dict:
    ds = rows("SELECT * FROM doc ORDER BY id")
    cnt = {r["doc_id"]: r["n"] for r in rows("SELECT doc_id, COUNT(*) n FROM ext WHERE value<>'' GROUP BY doc_id")}
    rv = {}
    for r in review_list():
        rv[r["doc_id"]] = rv.get(r["doc_id"], 0) + 1
    ch = {r["doc_id"]: r["n"] for r in rows("SELECT doc_id, COUNT(*) n FROM chunk GROUP BY doc_id")}
    for d in ds:
        d["filled"], d["review"], d["chunks"] = cnt.get(d["id"], 0), rv.get(d["id"], 0), ch.get(d["id"], 0)
    return {"docs": ds, "fields": fields(), "chunks": sum(ch.values()), "search_mode": search_mode()}


def values(doc_id: str) -> list[dict]:
    return rows("SELECT * FROM ext WHERE doc_id=? ORDER BY field", (doc_id,))


# ── 본문 · 검색 ──
def _split(text: str, size: int = 400) -> list[str]:
    out, cur = [], ""
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if cur and len(cur) + len(line) > size:
            out.append(cur)
            cur = cur[-80:] + "\n" + line  # 앞 조각 끝을 조금 겹침
        else:
            cur = (cur + "\n" + line) if cur else line
    if cur:
        out.append(cur)
    return out


def _save_text(did: str, pages: list) -> None:
    """쪽 글자 → 조각. 글자가 든 PDF는 PDF 글자를, 아니면 그림 읽기 결과를 씀."""
    con = connect()
    con.execute("DELETE FROM chunk WHERE doc_id=?", (did,))
    n = max(len(pages), len(page_images(did)))
    for i in range(n):
        f = DATA / "pages" / f"{did}-p{i + 1}.txt"
        text = f.read_text(encoding="utf-8") if f.exists() else (str(pages[i]) if i < len(pages) else "")
        for j, c in enumerate(_split(text)):
            con.execute("INSERT INTO chunk (doc_id, page, idx, text) VALUES (?,?,?,?)", (did, i + 1, j, c))


def _local_vec(t: str, dim: int = 256) -> list[float]:
    """임베딩이 안 될 때 쓰는 글자 2개씩 묶음 벡터(뜻이 아니라 글자 겹침)."""
    import hashlib
    v = [0.0] * dim
    t = re.sub(r"\s+", "", t.lower())
    for i in range(len(t) - 1):
        v[int(hashlib.md5(t[i:i + 2].encode()).hexdigest(), 16) % dim] += 1
    n = sum(x * x for x in v) ** 0.5 or 1
    return [round(x / n, 4) for x in v]


def _vecs(texts: list[str]) -> tuple[list[list[float]], str]:
    from .db import kv_get, kv_set
    mode = kv_get("embed_mode")
    if mode != "local" and llm.available():
        try:
            vs = llm.embed(texts)
            kv_set("embed_mode", "embed")
            return [[round(x, 5) for x in v] for v in vs], "embed"
        except Exception:
            if mode == "embed":
                raise
            kv_set("embed_mode", "local")
    return [_local_vec(t) for t in texts], "local"


def _embed_missing() -> None:
    cs = rows("SELECT id, text FROM chunk WHERE emb IS NULL")
    if not cs:
        return
    vs, _ = _vecs([c["text"] for c in cs])
    con = connect()
    for c, v in zip(cs, vs):
        con.execute("UPDATE chunk SET emb=? WHERE id=?", (json.dumps(v), c["id"]))


def search_mode() -> str:
    from .db import kv_get
    return {"embed": "의미 검색 · 단어가 달라도 뜻이 비슷하면 찾음", "local": "글자 검색 · 같은 단어가 있어야 찾음(임베딩 미연결)"}.get(kv_get("embed_mode"), "검색 전")


def search(text: str, doc_ids: list[str] | None = None, k: int = 5) -> list[dict]:
    """본문 조각 검색. doc_ids가 있으면 그 문서 안에서만(그래프로 거른 뒤 벡터로 고름)."""
    if not text.strip():
        return []
    cs = rows("SELECT id, doc_id, page, text, emb FROM chunk WHERE emb IS NOT NULL")
    if doc_ids is not None:  # 문서 번호(CL-001-D1)로 와도 파일 이름 붙은 문서(CL-001-D1_보험금청구서)를 찾음
        keep = set(doc_ids)
        cs = [c for c in cs if c["doc_id"] in keep or re.split(r"[_ ]", c["doc_id"])[0] in keep]
    if not cs:
        return []
    qv = _vecs([text])[0][0]
    out = []
    for c in cs:
        v = json.loads(c["emb"])
        if len(v) != len(qv):
            continue
        out.append({"doc_id": c["doc_id"], "page": c["page"], "text": c["text"], "score": round(sum(a * b for a, b in zip(qv, v)), 3)})
    out.sort(key=lambda x: -x["score"])
    return out[:k]


def text_of(did: str) -> list[dict]:
    return rows("SELECT page, idx, text FROM chunk WHERE doc_id=? ORDER BY page, idx", (did,))
