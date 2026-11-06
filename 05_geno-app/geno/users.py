"""사용자 · 역할 — 만드는 사람과 쓰는 사람을 나눔. 로그인 대신 화면 위에서 사용자를 고름(시험용).

역할
- 관리자: 모두 + 사용자 관리 · 처음 상태로
- 구축 담당(FD): 데이터 · 온톨로지 · 문서 · 규칙 · 지표 · 골든 질문을 만들고 고침, 변경 신청
- 검토자: 신청된 변경 승인 · 반려, 골든 질문 판정
- 현업: 질문만(민감 속성은 가려 보임)
사용자가 한 명도 없으면 설정 전 상태 — 모든 일을 할 수 있고, 화면이 첫 관리자를 만들라고 안내함.
"""
from contextvars import ContextVar

from .db import connect, now, one, rows

ROLES = {
    "관리자": "모든 기능과 사용자 관리",
    "구축 담당": "데이터 연결 · 온톨로지 · 문서 · 규칙 · 지표 · 골든 질문 만들기, 변경 신청",
    "검토자": "신청된 변경 승인 · 반려, 골든 질문 판정, 모든 화면 보기",
    "현업": "질문하기 · 내 질문 기록 · 데이터 탐색(민감 속성 가림)",
}
PERMS = {
    "관리자": {"view", "build", "review", "ask", "admin"},
    "구축 담당": {"view", "build", "ask"},
    "검토자": {"view", "review", "ask"},
    "현업": {"ask"},
}
ACTOR: ContextVar[dict | None] = ContextVar("actor", default=None)


def listing() -> list[dict]:
    return rows("SELECT * FROM usr ORDER BY id")


def get(uid) -> dict | None:
    try:
        return one("SELECT * FROM usr WHERE id=?", (int(uid),))
    except (TypeError, ValueError):
        return None


def setup_mode() -> bool:
    return not one("SELECT 1 FROM usr LIMIT 1")


def can(u: dict | None, perm: str) -> bool:
    if setup_mode():
        return True
    return bool(u) and perm in PERMS.get(u["role"], set())


def add(name: str, role: str) -> int:
    name = name.strip()
    if not name:
        raise ValueError("이름을 입력해 주세요.")
    if role not in ROLES:
        raise ValueError("역할을 선택해 주세요.")
    if setup_mode() and role != "관리자":
        raise ValueError("첫 사용자는 관리자여야 합니다.")
    if one("SELECT 1 FROM usr WHERE name=?", (name,)):
        raise ValueError("같은 이름의 사용자가 있습니다.")
    uid = connect().execute("INSERT INTO usr (name, role, at) VALUES (?,?,?)", (name, role, now())).lastrowid
    from . import history
    history.record(f"사용자 추가 · {name} ({role})", "사용자", "사람", {"이름": name, "역할": role})
    return uid


def _admins() -> int:
    return one("SELECT COUNT(*) n FROM usr WHERE role='관리자'")["n"]


def set_role(uid: int, role: str) -> None:
    u = get(uid)
    if not u or role not in ROLES:
        raise ValueError("사용자 또는 역할을 확인해 주세요.")
    if u["role"] == "관리자" and role != "관리자" and _admins() <= 1:
        raise ValueError("관리자가 한 명 이상 있어야 합니다.")
    connect().execute("UPDATE usr SET role=? WHERE id=?", (role, uid))
    from . import history
    history.record(f"역할 변경 · {u['name']} {u['role']} → {role}", "사용자", "사람", {"이름": u["name"], "역할": f"{u['role']} → {role}"})


def remove(uid: int) -> None:
    u = get(uid)
    if not u:
        return
    if u["role"] == "관리자" and _admins() <= 1:
        raise ValueError("마지막 관리자는 삭제할 수 없습니다.")
    connect().execute("DELETE FROM usr WHERE id=?", (uid,))
    from . import history
    history.record(f"사용자 삭제 · {u['name']}", "사용자", "사람", {"이름": u["name"]})
