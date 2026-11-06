"""저장소(SQLite 파일 하나). 처음엔 아무 데이터도 없음 — 사람이 올리거나 연결한 것만 들어감.

- 메타 표: source · tbl · obj · prop · rel · field · doc · ext · chunk · rule · metric · golden · tpl · ask · change · usr · kv
- 실제 데이터: 올린 표마다 "d:<표 이름>" 표(모든 칸 글자로 저장)
- 개체: "o:<개체 이름>" 뷰 = 원본 표 + 조건(한 표에서 여러 개체) + 계산 속성. 화면 · 질문 · 규칙은 모두 이 뷰를 읽음
GENO_DB로 파일 위치를 바꿀 수 있음(테스트용).
"""
import json
import os
import re
import sqlite3
import time
from contextvars import ContextVar
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(os.environ.get("GENO_DATA", ROOT / "data"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v TEXT);
CREATE TABLE IF NOT EXISTS scenario (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, changes TEXT, result TEXT, by TEXT, at REAL);
CREATE TABLE IF NOT EXISTS source (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, kind TEXT, conf TEXT, status TEXT, synced_at REAL, at REAL);
CREATE TABLE IF NOT EXISTS tbl (name TEXT PRIMARY KEY, source_id INTEGER, cols TEXT, types TEXT, nrows INTEGER, at REAL);
CREATE TABLE IF NOT EXISTS obj (name TEXT PRIMARY KEY, label TEXT, key TEXT, by TEXT, at REAL, base TEXT, filter TEXT, title TEXT, desc TEXT);
CREATE TABLE IF NOT EXISTS prop (obj TEXT, col TEXT, label TEXT, type TEXT, desc TEXT, syn TEXT, hidden INTEGER DEFAULT 0, sensitive INTEGER DEFAULT 0,
  calc TEXT, ord INTEGER, PRIMARY KEY (obj, col));
CREATE TABLE IF NOT EXISTS chunk (id INTEGER PRIMARY KEY AUTOINCREMENT, doc_id TEXT, page INTEGER, idx INTEGER, text TEXT, emb TEXT);
CREATE TABLE IF NOT EXISTS metric (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, text TEXT, spec TEXT, by TEXT, at REAL);
CREATE TABLE IF NOT EXISTS usr (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, role TEXT, at REAL);
CREATE TABLE IF NOT EXISTS rel (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, a_tbl TEXT, a_col TEXT, b_tbl TEXT, b_col TEXT, by TEXT, at REAL);
CREATE TABLE IF NOT EXISTS field (name TEXT PRIMARY KEY, label TEXT, desc TEXT, ord INTEGER, at REAL);
CREATE TABLE IF NOT EXISTS doc (id TEXT PRIMARY KEY, file TEXT, source_id INTEGER, pages INTEGER, read_at REAL, doc_type TEXT, lying INTEGER, err TEXT);
CREATE TABLE IF NOT EXISTS ext (doc_id TEXT, field TEXT, value TEXT, conf REAL, by TEXT, at REAL, PRIMARY KEY (doc_id, field));
CREATE TABLE IF NOT EXISTS rule (id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT, name TEXT, text TEXT, cond TEXT, ord INTEGER, on_ INTEGER DEFAULT 1, at REAL);
CREATE TABLE IF NOT EXISTS golden (id INTEGER PRIMARY KEY AUTOINCREMENT, q TEXT, want TEXT, got TEXT, ok TEXT, vote TEXT, ask_id INTEGER, run_at REAL, at REAL);
CREATE TABLE IF NOT EXISTS tpl (name TEXT PRIMARY KEY, plan TEXT, params TEXT, at REAL);
CREATE TABLE IF NOT EXISTS ask (id INTEGER PRIMARY KEY AUTOINCREMENT, q TEXT, tpl TEXT, result TEXT, at REAL, who TEXT);
CREATE TABLE IF NOT EXISTS change (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, layer TEXT, by TEXT, status TEXT,
  op TEXT, diff TEXT, snap TEXT, at REAL, decided_at REAL);
"""


# 예전 파일에 새 칸 붙이기(칸이 없을 때만)
MIGRATE = {"obj": ["base TEXT", "filter TEXT", "title TEXT", "desc TEXT"], "ask": ["who TEXT"], "doc": ["rot INTEGER"]}
_ready = set()


# 가정 바꿔 보기(What-if)는 원본 대신 임시 복사본 DB로 계산 — 이 값이 있으면 그 파일을 씀
DB_OVERRIDE: ContextVar[str | None] = ContextVar("DB_OVERRIDE", default=None)


def connect() -> sqlite3.Connection:
    DATA.mkdir(parents=True, exist_ok=True)
    path = Path(DB_OVERRIDE.get()) if DB_OVERRIDE.get() else DATA / "geno.db"
    con = sqlite3.connect(path, timeout=15, isolation_level=None)
    con.row_factory = sqlite3.Row
    if str(path) not in _ready:
        con.executescript(SCHEMA)
        for t, cols in MIGRATE.items():
            have = {r[1] for r in con.execute(f"PRAGMA table_info({t})")}
            for c in cols:
                if c.split()[0] not in have:
                    con.execute(f"ALTER TABLE {t} ADD COLUMN {c}")
        _ready.add(str(path))
    return con


def now() -> float:
    return time.time()


def q(name: str) -> str:
    """SQL 이름 감싸기 — 사람이 올린 표 · 열 이름을 그대로 써도 안전하게."""
    return '"' + str(name).replace('"', '""') + '"'


def dt(name: str) -> str:
    return q("d:" + name)


def ot(name: str) -> str:
    """개체 뷰 이름."""
    return q("o:" + name)


def clean_name(s: str) -> str:
    s = re.sub(r"\.[A-Za-z0-9]+$", "", s.strip())
    s = re.sub(r"[^\w가-힣]+", "_", s).strip("_").lower()
    return s or "table"


def rows(sql: str, args=()) -> list[dict]:
    return [dict(r) for r in connect().execute(sql, args)]


def one(sql: str, args=()) -> dict | None:
    r = connect().execute(sql, args).fetchone()
    return dict(r) if r else None


def kv_get(k: str, default=None):
    r = one("SELECT v FROM kv WHERE k=?", (k,))
    return json.loads(r["v"]) if r else default


def kv_set(k: str, v) -> None:
    connect().execute("INSERT OR REPLACE INTO kv VALUES (?,?)", (k, json.dumps(v, ensure_ascii=False)))


def reset() -> None:
    """처음 상태로 — 메타 · 데이터 · 올린 파일 모두 지움."""
    con = connect()
    for (n,) in con.execute("SELECT name FROM sqlite_master WHERE type='view' AND name LIKE 'o:%'").fetchall():
        con.execute(f"DROP VIEW {q(n)}")
    for (n,) in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'd:%'").fetchall():
        con.execute(f"DROP TABLE {q(n)}")
    for t in ["kv", "scenario", "source", "tbl", "obj", "prop", "rel", "field", "doc", "ext", "chunk", "rule", "metric", "golden", "tpl", "ask", "change", "usr"]:
        con.execute(f"DELETE FROM {t}")
    con.execute("DELETE FROM sqlite_sequence")
    for sub in ["files", "pages"]:
        d = DATA / sub
        if d.exists():
            for f in d.iterdir():
                f.unlink()
    sec = DATA / "secrets.json"
    if sec.exists():
        sec.unlink()
