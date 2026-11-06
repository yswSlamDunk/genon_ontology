"""보험 PoC 업무 시스템 공통 — DB 연결, 시스템 인증, /health, 조회 도우미, 쓰기 API 공통 규칙.

서버_설계서.md 2–3절, 7.1절을 따른다.
- 시스템마다 인증 방식이 다르다 (4절). 비밀 값은 환경변수에서만 읽는다.
- 조회 API는 읽기 전용 연결(db), 쓰기 API는 쓰기용 연결(db_write)만 쓴다.
- 응답 필드 이름은 DB 컬럼 이름 그대로다.
- 쓰기 API: Idempotency-Key 필수, 거절은 409 {"detail": {"code", "message"}}.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
from contextlib import contextmanager
from typing import Any, Iterator

import httpx
import psycopg
from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBasic, HTTPBasicCredentials, HTTPBearer
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

DSN = os.environ.get("INS_DSN", "")

LIMIT = Query(100, ge=1, le=500, description="최대 건수 (기본 100, 최대 500)")


# ── DB ───────────────────────────────────────────────────────────────────────

@contextmanager
def db() -> Iterator[psycopg.Connection]:
    """조회용. 요청 하나 = 읽기 전용 트랜잭션 하나."""
    with psycopg.connect(DSN, row_factory=dict_row, options="-c default_transaction_read_only=on",
                         connect_timeout=3) as conn:
        yield conn


@contextmanager
def db_write() -> Iterator[psycopg.Connection]:
    """쓰기 API용. 블록이 정상으로 끝나면 커밋, 예외면 롤백한다."""
    with psycopg.connect(DSN, row_factory=dict_row, connect_timeout=3) as conn:
        yield conn


def one(conn: psycopg.Connection, sql: str, params: tuple, what: str) -> dict:
    row = conn.execute(sql, params).fetchone()
    if not row:
        raise HTTPException(404, f"{what} 이(가) 없습니다")
    return row


def rows(conn: psycopg.Connection, sql: str, params: tuple = ()) -> list[dict]:
    return conn.execute(sql, params).fetchall()


def where(filters: dict[str, Any]) -> tuple[str, tuple]:
    """값이 있는 필터만 `col = %s` 로 잇는다. 키는 코드에 적힌 컬럼 이름만 온다 (사용자 입력 아님)."""
    used = [(k, v) for k, v in filters.items() if v is not None]
    if not used:
        return "", ()
    return " WHERE " + " AND ".join(f"{k} = %s" for k, _ in used), tuple(v for _, v in used)


def next_id(conn: psycopg.Connection, seq: str, prefix: str, width: int) -> str:
    n = conn.execute(f"SELECT nextval('{seq}') AS n").fetchone()["n"]
    return f"{prefix}{n:0{width}d}"


def plain(value: Any) -> Any:
    """DB 행·날짜를 JSON 값으로 (jsonb 저장, 해시 계산용)."""
    return jsonable_encoder(value)


def canonical_hash(value: Any) -> str:
    text = json.dumps(plain(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(text.encode()).hexdigest()


# ── 거절 ─────────────────────────────────────────────────────────────────────

class Reject(Exception):
    """업무 조건 위반. 업무 데이터는 바꾸지 않는다 (서버_설계서.md 7.1절)."""

    def __init__(self, code: str, message: str, status: int = 409):
        super().__init__(f"{code}: {message}")
        self.code, self.message, self.status = code, message, status


# ── 멱등성 (서버_설계서.md 7.1절, 명세 8.3절) ────────────────────────────────────

IdemKey = Header(..., alias="Idempotency-Key", description="요청 키. 같은 키·같은 입력이면 처음 결과를 돌려준다")


def idem_begin(conn: psycopg.Connection, schema: str, action_type: str, actor_id: str, key: str,
               payload: Any) -> Any | None:
    """처음이면 None. 같은 키·같은 입력의 완료 기록이 있으면 그 결과. 입력이 다르면 거절.

    INSERT 를 먼저 해서, 같은 키로 동시에 온 두 번째 요청은 첫 트랜잭션이 끝날 때까지 기다린다.
    """
    h = canonical_hash(payload)
    new = conn.execute(f"INSERT INTO {schema}.idempotency_record (action_type, actor_id, idem_key, request_hash) "
                       "VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING RETURNING 1",
                       (action_type, actor_id, key, h)).fetchone()
    if new:
        return None
    prev = conn.execute(f"SELECT request_hash, response FROM {schema}.idempotency_record "
                        "WHERE action_type = %s AND actor_id = %s AND idem_key = %s",
                        (action_type, actor_id, key)).fetchone()
    if prev["request_hash"] != h:
        raise Reject("IDEMPOTENCY_CONFLICT", f"요청 키 {key} 는 다른 입력으로 이미 쓰였습니다")
    return prev["response"]


def idem_finish(conn: psycopg.Connection, schema: str, action_type: str, actor_id: str, key: str, response: Any) -> Any:
    response = plain(response)
    conn.execute(f"UPDATE {schema}.idempotency_record SET response = %s "
                 "WHERE action_type = %s AND actor_id = %s AND idem_key = %s",
                 (Jsonb(response), action_type, actor_id, key))
    return response


# ── 인증 ──────────────────────────────────────────────────────────────────────

def _same(a: str, b: str) -> bool:
    return bool(a) and bool(b) and hmac.compare_digest(a.encode(), b.encode())


def api_key_auth(env: str, header: str = "X-API-Key"):
    scheme = APIKeyHeader(name=header, auto_error=False)

    def check(key: str | None = Depends(scheme)) -> str:
        if not _same(key or "", os.environ.get(env, "")):
            raise HTTPException(401, f"{header} 가 맞지 않습니다")
        return "api-key"
    return check


def basic_auth(env: str):
    """env 값은 `사용자:비밀번호`."""
    scheme = HTTPBasic(auto_error=False)

    def check(cred: HTTPBasicCredentials | None = Depends(scheme)) -> str:
        user, _, pw = os.environ.get(env, "").partition(":")
        if not cred or not (_same(cred.username, user) and _same(cred.password, pw)):
            raise HTTPException(401, "Basic 인증이 필요합니다", headers={"WWW-Authenticate": "Basic"})
        return cred.username
    return check


def bearer_auth(env: str):
    scheme = HTTPBearer(auto_error=False)

    def check(cred: HTTPAuthorizationCredentials | None = Depends(scheme)) -> str:
        if not cred or not _same(cred.credentials, os.environ.get(env, "")):
            raise HTTPException(401, "Bearer 토큰이 맞지 않습니다")
        return "bearer"
    return check


# ── 다른 시스템 호출 (서버_설계서.md 3절 원칙 1) ─────────────────────────────────

SYSTEMS = {
    "contract": "http://127.0.0.1:18101",
    "intake": "http://127.0.0.1:18102",
    "review": "http://127.0.0.1:18103",
    "payment": "http://127.0.0.1:18104",
}


def _auth_headers(system: str) -> dict:
    env = os.environ.get
    if system == "contract":
        return {"X-API-Key": env("INS_CONTRACT_API_KEY", "")}
    if system == "intake":
        return {"Authorization": "Basic " + base64.b64encode(env("INS_INTAKE_BASIC", "").encode()).decode()}
    if system == "review":
        return {"Authorization": "Bearer " + env("INS_REVIEW_TOKEN", "")}
    if system == "payment":
        return {"X-Payment-Key": env("INS_PAYMENT_API_KEY", "")}
    raise ValueError(system)


class DependencyError(Exception):
    """다른 시스템을 조회하지 못함 (연결 실패, 시간 초과, 5xx)."""

    def __init__(self, system: str, detail: str, timeout: bool = False):
        super().__init__(f"{system}: {detail}")
        self.system, self.detail, self.timeout = system, detail, timeout


def call(system: str, method: str, path: str, *, params: dict | None = None, json_body: Any = None,
         headers: dict | None = None, timeout: float = 3.0, raw: bytes | None = None) -> tuple[int, Any]:
    """다른 시스템 API 호출 → (상태 코드, JSON). 연결 실패·시간 초과·5xx 는 DependencyError.
    raw 를 주면 본문을 그 바이트 그대로 보낸다 (서명한 본문이 바뀌지 않게)."""
    try:
        r = httpx.request(method, SYSTEMS[system] + path, params={k: v for k, v in (params or {}).items() if v is not None},
                          json=json_body if raw is None else None, content=raw,
                          headers={**_auth_headers(system), **(headers or {})}, timeout=timeout)
    except httpx.TimeoutException as exc:
        raise DependencyError(system, f"시간 초과 {path}", timeout=True) from exc
    except httpx.HTTPError as exc:
        raise DependencyError(system, f"{type(exc).__name__} {path}") from exc
    if r.status_code >= 500:
        raise DependencyError(system, f"HTTP {r.status_code} {path}", timeout=r.status_code == 504)
    try:
        return r.status_code, r.json()
    except ValueError:
        return r.status_code, r.text


def get_or_none(system: str, path: str, **kw) -> Any | None:
    """GET — 404 면 None. 그 밖의 4xx 는 DependencyError (호출 계약 위반)."""
    status, data = call(system, "GET", path, **kw)
    if status == 404:
        return None
    if status >= 400:
        raise DependencyError(system, f"HTTP {status} {path}")
    return data


def sign(body: bytes) -> str:
    """지급 연계 콜백 서명 (서버_설계서.md 7.6절)."""
    return hmac.new(os.environ.get("INS_PAYMENT_CALLBACK_SECRET", "").encode(), body, hashlib.sha256).hexdigest()


def signature_ok(body: bytes, signature: str | None) -> bool:
    return bool(os.environ.get("INS_PAYMENT_CALLBACK_SECRET")) and _same(signature or "", sign(body))


# ── 앱 ───────────────────────────────────────────────────────────────────────

def make_app(*, title: str, description: str, schema: str) -> FastAPI:
    """공통 설정의 FastAPI 앱. /health 는 인증 없이, OpenAPI 문서에는 넣지 않는다 (설계서 2.2절)."""
    app = FastAPI(title=title, version="0.2.0", description=description)

    @app.exception_handler(Reject)
    async def _reject(_: Request, exc: Reject):
        return JSONResponse({"detail": {"code": exc.code, "message": exc.message}}, status_code=exc.status)

    @app.get("/health", operation_id="health", include_in_schema=False)
    def health():
        try:
            with db() as conn:
                conn.execute("SELECT 1 FROM pg_namespace WHERE nspname = %s", (schema,)).fetchone()
        except psycopg.Error as exc:
            return JSONResponse({"status": "down", "detail": f"DB 접속 실패: {type(exc).__name__}"}, status_code=503)
        return {"status": "ok", "schema": schema, "read_only_queries": True}

    return app
