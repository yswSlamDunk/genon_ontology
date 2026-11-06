"""업무 이름이 없는 칸의 한글 이름 — LLM 없이(영어 칸 이름을 화면에 그대로 내지 않으려고).

순서: 사람이 붙인 업무 이름 → 동의어 첫 말 → 설명(뜻)의 앞부분 → 영어 낱말을 사전으로 옮긴 짧은 이름(visit_type → 진료 유형, filed_date → 청구일).
"""
import re

WORDS = {
    "id": "번호", "no": "번호", "num": "번호", "number": "번호", "seq": "순번", "idx": "순번", "index": "순번", "key": "키",
    "code": "코드", "name": "이름", "title": "제목", "label": "이름", "type": "유형", "kind": "종류", "category": "분류", "class": "분류",
    "status": "상태", "state": "상태", "flag": "여부", "yn": "여부", "level": "등급", "grade": "등급", "rank": "순위", "score": "점수",
    "amount": "금액", "amt": "금액", "price": "가격", "cost": "비용", "fee": "수수료", "premium": "보험료", "benefit": "보험금", "limit": "한도",
    "count": "건수", "cnt": "건수", "qty": "수량", "quantity": "수량", "total": "합계", "sum": "합계", "avg": "평균", "mean": "평균",
    "median": "중앙값", "max": "최대", "min": "최소", "rate": "비율", "ratio": "비율", "pct": "비율", "percent": "비율", "std": "표준편차",
    "days": "일수", "year": "연도", "month": "월", "week": "주", "hour": "시간", "age": "나이",
    "start": "시작", "begin": "시작", "end": "종료", "from": "시작", "to": "종료", "effective": "효력", "expire": "만기", "expiry": "만기",
    "created": "생성", "updated": "수정", "deleted": "삭제", "renewal": "갱신", "cancel": "해지", "approved": "승인", "approve": "승인",
    "reject": "반려", "request": "요청", "process": "처리", "step": "단계", "issue": "발행", "issued": "발행",
    "filed": "청구", "claim": "청구", "policy": "계약", "contract": "계약", "insured": "피보험자", "insurer": "보험사", "customer": "고객",
    "user": "사용자", "member": "회원", "patient": "환자", "doctor": "의사", "hospital": "병원", "clinic": "의원", "disease": "질병",
    "group": "군", "diag": "진단", "diagnosis": "진단", "onset": "발병", "visit": "진료", "treatment": "진료", "drug": "약", "prescription": "처방",
    "receipt": "영수증", "doc": "문서", "document": "서류", "file": "파일", "page": "쪽", "text": "본문", "product": "상품", "coverage": "보장",
    "paid": "지급", "pay": "지급", "payment": "지급", "history": "이력", "result": "결과", "rule": "규칙", "review": "심사", "stat": "통계",
    "question": "질문", "answer": "답변", "answered": "답변", "target": "대상", "notice": "주의", "exclusion": "면책", "reason": "사유",
    "desc": "설명", "description": "설명", "note": "메모", "memo": "메모", "comment": "의견", "address": "주소", "addr": "주소",
    "phone": "전화번호", "tel": "전화번호", "mobile": "휴대전화", "email": "이메일", "gender": "성별", "sex": "성별", "region": "지역",
    "city": "도시", "branch": "지점", "dept": "부서", "department": "부서", "channel": "채널", "order": "주문", "item": "품목", "unit": "단위",
    "value": "값", "main": "주", "sub": "하위", "parent": "상위", "bank": "은행", "account": "계좌", "rrn": "주민등록번호", "ssn": "주민등록번호",
    "zip": "우편번호", "lat": "위도", "lng": "경도", "lon": "경도", "url": "주소", "ticker": "종목코드", "corp": "법인", "company": "회사",
    "stock": "주식", "holder": "주주", "share": "지분", "employee": "직원", "dividend": "배당", "financial": "재무", "event": "행사",
    "check": "점검", "condition": "조건", "finding": "소견", "metric": "지표", "p25": "하위 25%", "p75": "상위 25%", "p50": "중앙값",
    "period": "기간", "reduce": "감액", "months": "개월", "route": "분류", "sample": "표본", "n": "수", "source": "출처", "uses": "사용",
    "cancer": "암", "similar": "유사", "decided": "결정", "exempt": "면책", "deduct": "공제", "self": "본인", "outlier": "이상치",
    "medical": "의료", "waiting": "대기", "plain": "쉬운", "decision": "결정", "outcome": "결과", "count_n": "건수",
    "is": "", "has": "", "the": "", "of": "", "and": "", "in": "",
}
DAY = {"date": "일", "dt": "일", "on": "일", "day": "일"}
AT = {"at": "일시", "time": "시각", "datetime": "일시", "ts": "일시"}
NUM = {"id", "no", "num", "number"}


def from_words(col: str) -> str:
    """영어 칸 이름 → 짧은 한글. 모르는 낱말은 빼고, 남는 게 없으면 빈 글자."""
    toks = [t.lower() for t in re.split(r"[_\-\s]+|(?<=[a-z])(?=[A-Z])", str(col)) if t]
    if not toks or not all(re.fullmatch(r"[a-z0-9]+", t) for t in toks):
        return ""
    if toks[:2] == ["birth", "date"] or toks == ["birth"]:
        return "생년월일"
    tail = ""
    if toks[-1] in DAY:
        tail, toks = "일", toks[:-1]
    elif toks[-1] in AT:
        tail, toks = AT[toks[-1]], toks[:-1]
    words = [WORDS.get(t) or (WORDS.get(t[:-1]) if t.endswith("s") else "") for t in toks]  # orders → order
    words = [w for w in words if w]
    if not words:
        return tail if tail and len(toks) == 0 else ""
    out = ""
    for w in words:  # 군 · 별처럼 붙여 쓰는 말은 붙임(질병군)
        out += w if out and w in ("군", "별") else (" " + w if out else w)
    if tail == "일":
        out += "일"
    elif tail:
        out += " " + tail
    if toks and toks[-1] == "flag" or (toks and toks[0] in ("is", "has")):
        out = out if out.endswith("여부") else out + " 여부"
    return out


def plain(col: str, label: str = "", desc: str = "", syn: str = "") -> str:
    if label and label != col and not re.fullmatch(r"[a-z0-9_]+", label):
        return label
    if syn:
        s = re.split(r"[,·/]", syn)[0].strip()
        if s and not re.search(r"[a-z]{3,}", s):
            return s[:16]
    if desc:
        d = re.split(r"[.(\n:—\-]|\s{2}", desc)[0].strip()
        if 1 < len(d) <= 12 and not re.search(r"[a-z]{3,}", d):
            return d
    w = from_words(col)
    if w:
        return w
    return "이름 없는 속성" if re.search(r"[A-Za-z]", str(col)) else str(col)
