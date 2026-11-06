"""데이터 소스 — CSV 올리기 · DB 연결(읽기만) · 문서 올리기.

가져온 표는 로컬 저장소에 "d:<표 이름>"으로 복사해 둠(다시 가져오기로 새로 고침).
DB 비밀번호는 data/secrets.json(본인만 읽기)에만 두고 화면 · 응답에 다시 내보내지 않음.
"""
import csv
import io
import json
import time
import os
import re
from pathlib import Path

from . import history
from .db import DATA, clean_name, connect, dt, now, one, q, rows

DB_KINDS = {"sqlite": "SQLite", "postgresql": "PostgreSQL", "mysql": "MySQL · MariaDB"}
DOC_EXT = {".jpg", ".jpeg", ".png", ".webp", ".pdf"}


# ── 표 저장 ──
def _type(vals: list[str]) -> str:
    v = [x for x in vals if x not in ("", None)]
    if not v:
        return "글자"
    if all(re.fullmatch(r"\d{4}-\d{2}-\d{2}", x) for x in v):
        return "날짜"
    if all(re.fullmatch(r"-?\d+(\.\d+)?", x) and not (len(x) > 1 and x.startswith("0") and "." not in x) for x in v):
        return "숫자"
    return "글자"


def save_table(name: str, cols: list[str], data: list[list], source_id: int) -> dict:
    cols = [c.strip() or f"col{i + 1}" for i, c in enumerate(cols)]
    if len(set(cols)) != len(cols):
        raise ValueError(f"{name}: 열 이름이 중복됩니다.")
    data = [["" if v is None else str(v) for v in r] for r in data]
    types = [_type([r[i] for r in data]) for i in range(len(cols))]
    con = connect()
    con.execute(f"DROP TABLE IF EXISTS {dt(name)}")
    con.execute(f"CREATE TABLE {dt(name)} ({', '.join(q(c) + ' TEXT' for c in cols)})")
    con.executemany(f"INSERT INTO {dt(name)} VALUES ({','.join('?' * len(cols))})", data)
    con.execute("INSERT OR REPLACE INTO tbl VALUES (?,?,?,?,?,?)", (name, source_id, json.dumps(cols, ensure_ascii=False),
                                                                 json.dumps(types, ensure_ascii=False), len(data), now()))
    return {"name": name, "cols": cols, "types": types, "nrows": len(data)}


def parse_csv(raw: bytes) -> tuple[list[str], list[list]]:
    for enc in ("utf-8-sig", "cp949"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError("파일 인코딩을 읽을 수 없습니다. UTF-8 또는 CP949 파일만 업로드할 수 있습니다.")
    r = list(csv.reader(io.StringIO(text)))
    r = [x for x in r if any(c.strip() for c in x)]
    if len(r) < 2:
        raise ValueError("머리글 행과 데이터 행이 1개 이상 있어야 합니다.")
    head = r[0]
    for i, line in enumerate(r[1:], start=2):
        if len(line) != len(head):
            raise ValueError(f"{i}번째 행의 열 개수({len(line)}개)가 머리글({len(head)}개)과 다릅니다.")
    return head, r[1:]


def add_files(name: str, files: list[tuple[str, bytes]], tnames: dict | None = None) -> dict:
    """CSV는 표로, 그림 · PDF는 문서로. 한 번 올린 묶음 = 소스 하나."""
    csvs = [(f, b) for f, b in files if f.lower().endswith(".csv")]
    docs = [(f, b) for f, b in files if Path(f).suffix.lower() in DOC_EXT]
    if not csvs and not docs:
        raise ValueError("CSV·JPG·PNG·WebP·PDF 파일만 업로드할 수 있습니다.")
    con = connect()
    out = {}
    stamp = time.strftime("%m/%d %H:%M")
    if csvs:
        sid = con.execute("INSERT INTO source (name, kind, conf, status, synced_at, at) VALUES (?,?,?,?,?,?)",
                          (name or f"업로드한 표 · {stamp}", "csv", "{}", "ok", now(), now())).lastrowid
        made = []
        for f, b in csvs:
            head, data = parse_csv(b)
            made.append(save_table(clean_name((tnames or {}).get(f) or Path(f).name), head, data, sid))
        out["tables"] = made
        history.record(f"파일 업로드 · 표 {len(made)}개", "데이터", "사람", {"tables": [m["name"] for m in made]})
    if docs:
        from . import docs as D
        sid = con.execute("INSERT INTO source (name, kind, conf, status, synced_at, at) VALUES (?,?,?,?,?,?)",
                          (name or f"업로드한 문서 · {stamp}", "doc", "{}", "ok", now(), now())).lastrowid
        out["docs"] = D.store(sid, docs)
        history.record(f"문서 업로드 · {len(out['docs'])}건", "데이터", "사람", {"docs": out["docs"]})
    return out


# ── DB 연결 ──
def _secret(sid: int, pw: str | None = None) -> str | None:
    p = DATA / "secrets.json"
    d = json.loads(p.read_text()) if p.exists() else {}
    if pw is None:
        return d.get(str(sid))
    d[str(sid)] = pw
    p.write_text(json.dumps(d))
    os.chmod(p, 0o600)
    return pw


def _open(conf: dict, pw: str | None):
    k = conf.get("kind")
    if k == "sqlite":
        path = Path(conf.get("path", "")).expanduser()
        if not path.exists():
            raise ValueError("SQLite 파일이 없습니다. 파일 경로를 확인해 주세요.")
        import sqlite3
        return sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    if k == "postgresql":
        import psycopg
        c = psycopg.connect(host=conf["host"], port=int(conf.get("port") or 5432), dbname=conf["dbname"],
                            user=conf["user"], password=pw or "", connect_timeout=8)
        c.read_only = True
        return c
    if k == "mysql":
        import pymysql
        return pymysql.connect(host=conf["host"], port=int(conf.get("port") or 3306), database=conf["dbname"],
                               user=conf["user"], password=pw or "", connect_timeout=8, read_timeout=30)
    raise ValueError("지원하지 않는 DB 유형입니다.")


def _list_tables(c, kind: str) -> list[dict]:
    cur = c.cursor()
    if kind == "sqlite":
        cur.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%' ORDER BY name")
    elif kind == "postgresql":
        cur.execute("SELECT table_schema || '.' || table_name FROM information_schema.tables "
                    "WHERE table_schema NOT IN ('pg_catalog','information_schema') ORDER BY 1")
    else:
        cur.execute("SHOW TABLES")
    names = [r[0] for r in cur.fetchall()]
    out = []
    for n in names[:200]:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {_qi(n, kind)}")
            cnt = cur.fetchone()[0]
        except Exception:
            cnt = None
        out.append({"name": n, "rows": cnt})
    return out


def _qi(name: str, kind: str) -> str:
    if kind == "mysql":
        return ".".join("`" + p.replace("`", "``") + "`" for p in name.split("."))
    return ".".join('"' + p.replace('"', '""') + '"' for p in name.split("."))


def db_test(conf: dict, pw: str | None) -> dict:
    c = _open(conf, pw)
    try:
        return {"ok": True, "tables": _list_tables(c, conf["kind"])}
    finally:
        c.close()


def db_add(name: str, conf: dict, pw: str | None, tables: list[str], limit: int = 50000) -> dict:
    conf = {k: conf.get(k) for k in ("kind", "host", "port", "dbname", "user", "path") if conf.get(k)}
    con = connect()
    sid = con.execute("INSERT INTO source (name, kind, conf, status, synced_at, at) VALUES (?,?,?,?,?,?)",
                      (name or DB_KINDS.get(conf["kind"], "DB"), "db", json.dumps({**conf, "tables": tables}, ensure_ascii=False),
                       "ok", None, now())).lastrowid
    if pw:
        _secret(sid, pw)
    res = db_sync(sid, limit)
    history.record(f"DB 연결 · {name} · 표 {len(tables)}개", "데이터", "사람", {"source": name, "tables": tables})
    return res


def db_sync(sid: int, limit: int = 50000) -> dict:
    s = one("SELECT * FROM source WHERE id=?", (sid,))
    conf = json.loads(s["conf"])
    c = _open(conf, _secret(sid))
    made = []
    try:
        cur = c.cursor()
        for t in conf.get("tables", []):
            cur.execute(f"SELECT * FROM {_qi(t, conf['kind'])} LIMIT {int(limit)}")
            cols = [d[0] for d in cur.description]
            made.append(save_table(clean_name(t.split(".")[-1]), cols, [list(r) for r in cur.fetchall()], sid))
    finally:
        c.close()
    connect().execute("UPDATE source SET synced_at=?, status='ok' WHERE id=?", (now(), sid))
    return {"tables": made}


# ── 목록 ──
def listing() -> list[dict]:
    out = []
    for s in rows("SELECT * FROM source ORDER BY id"):
        conf = json.loads(s["conf"] or "{}")
        ts = rows("SELECT name, cols, types, nrows FROM tbl WHERE source_id=? ORDER BY name", (s["id"],))
        for t in ts:
            t["cols"], t["types"] = json.loads(t["cols"]), json.loads(t["types"])
        nd = one("SELECT COUNT(*) n FROM doc WHERE source_id=?", (s["id"],))["n"]
        out.append({"id": s["id"], "name": s["name"], "kind": s["kind"], "kind_label": DB_KINDS.get(conf.get("kind"), ""),
                    "where": conf.get("host") or conf.get("path") or "", "status": s["status"], "synced_at": s["synced_at"] or s["at"],
                    "tables": ts, "docs": nd})
    return out


def rename(sid: int, name: str) -> None:
    if not name.strip():
        raise ValueError("이름을 입력해 주세요.")
    s = one("SELECT name FROM source WHERE id=?", (sid,))
    connect().execute("UPDATE source SET name=? WHERE id=?", (name.strip(), sid))
    history.record(f"데이터 소스 이름 변경 · {s['name']} → {name.strip()}", "데이터", "사람", {"이름": name.strip()})


def remove(sid: int) -> None:
    con = connect()
    s = one("SELECT * FROM source WHERE id=?", (sid,))
    if not s:
        return
    for t in rows("SELECT name FROM tbl WHERE source_id=?", (sid,)):
        con.execute(f"DROP TABLE IF EXISTS {dt(t['name'])}")
        con.execute("DELETE FROM tbl WHERE name=?", (t["name"],))
    from . import docs as D
    D.remove_source(sid)
    con.execute("DELETE FROM source WHERE id=?", (sid,))
    history.record(f"데이터 소스 삭제 · {s['name']}", "데이터", "사람", {"source": s["name"]})


def table_names() -> list[str]:
    return [r["name"] for r in rows("SELECT name FROM tbl ORDER BY name")]


def table(name: str) -> dict | None:
    t = one("SELECT * FROM tbl WHERE name=?", (name,))
    if t:
        t["cols"], t["types"] = json.loads(t["cols"]), json.loads(t["types"])
    return t


def sample(name: str, n: int = 5) -> list[dict]:
    return rows(f"SELECT * FROM {dt(name)} LIMIT {int(n)}")
