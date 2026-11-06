"""보험 청구 시나리오 업로드 자료(비정형)를 만든다 (가상 자료).

시나리오마다 파일 2개를 만든다. 표나 항목 이름 없이, 실제 제출 서류처럼 문장과 자유 배치로 쓴다.
- UP-Sn-01_보험금청구서.docx : 청구인이 직접 쓴 자유 서술 청구서
- UP-Sn-02_입퇴원확인서.pdf  : 의료기관이 발급한 확인서 (텍스트 PDF, 스캔 아님)

시나리오 1(지금 구축): 피보험자 B의 두 번째 입원 → 지급
시나리오 2(발표 때 추가): 계약자 A 본인의 입원 → 피보험자가 아니므로 부지급

계약·고객은 B0의 PO-001과 가상 인물 A·B를 쓴다. 문서에는 청구인 번호(IP-…)나 보장 코드를 쓰지 않는다.
이름·계약번호·「하루 10만 원 입원 일당」으로 온톨로지가 기존 청구인·보장과 잇게 한다.
서류 해시는 문서 안에 없다. 구축 에이전트가 업로드 파일의 SHA-256을 계산한다(이 스크립트가 기대값을 출력).

사용: uv run --with python-docx --with reportlab python make_scenario_upload.py <출력 폴더>
"""
import hashlib
import sys
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.shared import Pt
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

OUT = Path(sys.argv[1])
DOCX_FONT = "Apple SD Gothic Neo"
pdfmetrics.registerFont(TTFont("KR", "/System/Library/Fonts/Supplemental/AppleGothic.ttf"))
NOTICE = "[가상 문서 — 실험용. 실제 인물·의료기관·보험 계약이 아닙니다]"

SCENARIOS = [
    {
        "no": 1,
        "letter": [
            "보험금을 청구합니다",
            "담당자님께,",
            "저는 가상 인물 B입니다. 계약번호 TEST-POLICY-001 보험에 피보험자로 들어 있습니다. "
            "이번에 입원을 하게 되어 입원 일당(하루 10만 원 보장)을 청구하려고 이 글을 씁니다.",
            "6월 2일 화요일 아침에 허리 통증이 심해져 가상 의료기관 H-002에 갔고, 그날 바로 입원했습니다. "
            "치료를 받고 6월 5일 금요일 오전에 퇴원했습니다.",
            "입원한 다음 날인 6월 3일에 콜센터에 전화해 사고 접수를 했고, 사고접수번호 ACC-0101을 안내받았습니다.",
            "올해 3월에도 같은 보험으로 입원 일당을 청구한 적이 있습니다. 이번 입원은 그때와 다른 별개의 입원입니다.",
            "병원에서 받은 입퇴원확인서를 함께 보냅니다(UP-S1-02_입퇴원확인서.pdf). 확인해 주시면 감사하겠습니다.",
            "2026년 6월 8일",
            "가상 인물 B 드림",
        ],
        "hospital": "H-002", "reg_no": "2026-0602-117", "patient": "가상 인물 B", "token": "TKN-B",
        "dept": "정형외과", "disease": "요추 염좌(가상)",
        "stay": "2026년 06월 02일 ~ 2026년 06월 05일 (3박 4일)", "issued": "2026. 06. 05.",
    },
    {
        "no": 2,
        "letter": [
            "입원비 청구드립니다",
            "안녕하세요.",
            "가상 인물 A입니다. 제가 계약자로 가입한 보험(계약번호 TEST-POLICY-001)으로 제 입원 일당을 청구하려고 합니다. "
            "하루 10만 원씩 나오는 입원 보장으로 알고 있습니다.",
            "7월 10일 금요일 저녁에 고열로 가상 의료기관 H-004 응급실에 갔다가 그대로 입원했고, "
            "7월 14일 화요일에 퇴원했습니다.",
            "주말인 7월 11일에 콜센터로 사고 접수를 했고, 사고접수번호는 ACC-0102라고 들었습니다.",
            "입퇴원확인서를 첨부합니다(UP-S2-02_입퇴원확인서.pdf).",
            "2026년 7월 16일",
            "가상 인물 A",
        ],
        "hospital": "H-004", "reg_no": "2026-0710-482", "patient": "가상 인물 A", "token": "TKN-A",
        "dept": "내과", "disease": "급성 장염(가상)",
        "stay": "2026년 07월 10일 ~ 2026년 07월 14일 (4박 5일)", "issued": "2026. 07. 14.",
    },
]


def make_letter(s: dict, path: Path):
    d = Document()
    st = d.styles["Normal"]
    st.font.name = DOCX_FONT
    st.element.rPr.rFonts.set(qn("w:eastAsia"), DOCX_FONT)
    st.font.size = Pt(11)
    d.add_paragraph(NOTICE).runs[0].font.size = Pt(8)
    title, *body = s["letter"]
    r = d.add_paragraph().add_run(title)
    r.bold, r.font.size = True, Pt(16)
    for line in body:
        d.add_paragraph(line)
    d.save(path)


def make_cert(s: dict, path: Path):
    c = canvas.Canvas(str(path), pagesize=A4)
    c.setTitle(f"입퇴원확인서 {s['reg_no']}")
    w, h = A4
    c.setFont("KR", 8)
    c.drawString(40, h - 30, NOTICE)
    c.setFont("KR", 12)
    c.drawString(40, h - 70, f"가상 의료기관 {s['hospital']}")
    c.setFont("KR", 8)
    c.drawString(40, h - 84, "(가상 주소) 가상시 가상구 실험로 1    원무과 000-0000-0000")
    c.setFont("KR", 24)
    c.drawCentredString(w / 2, h - 150, "입 퇴 원 확 인 서")
    c.setFont("KR", 10)
    c.drawRightString(w - 40, h - 180, f"등록번호 {s['reg_no']}")
    y = h - 230
    for text, size in [
        (f"성  명   {s['patient']}", 12),
        (f"(주민등록번호 대신 가상 식별 토큰 {s['token']})", 9),
        ("", 6),
        ("위 환자는 본원에서 아래와 같이 입원 치료를 받았음을 확인합니다.", 11),
        ("", 6),
        (f"입원 기간   {s['stay']}", 11),
        (f"진  료  과   {s['dept']}", 11),
        (f"병      명   {s['disease']}", 11),
        ("", 6),
        ("용도: 보험 청구용", 10),
    ]:
        c.setFont("KR", size)
        c.drawString(70, y, text)
        y -= size + 14
    c.setFont("KR", 11)
    c.drawCentredString(w / 2, 220, s["issued"])
    c.drawCentredString(w / 2, 190, f"가상 의료기관 {s['hospital']}   원무과장 (직인)")
    c.setFont("KR", 9)
    c.drawString(70, 140, f"요양기관기호 {s['hospital']}")
    c.circle(w / 2 + 120, 194, 18)
    c.setFont("KR", 8)
    c.drawCentredString(w / 2 + 120, 191, "직인")
    c.save()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


for s in SCENARIOS:
    folder = OUT / f"시나리오{s['no']}"
    folder.mkdir(parents=True, exist_ok=True)
    letter = folder / f"UP-S{s['no']}-01_보험금청구서.docx"
    cert = folder / f"UP-S{s['no']}-02_입퇴원확인서.pdf"
    make_letter(s, letter)
    make_cert(s, cert)
    for p in (letter, cert):
        print(p.relative_to(OUT), sha(p))
