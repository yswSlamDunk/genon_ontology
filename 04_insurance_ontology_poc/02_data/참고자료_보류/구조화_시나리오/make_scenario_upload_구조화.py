"""보험 청구 시나리오 업로드 자료 4개를 만든다 (가상 자료).

시나리오마다 docx 1개(청구 서류 묶음: 보험금 청구서 + 입퇴원확인서)와 xlsx 1개(접수 자료 표)를 만든다.
- 시나리오 1: 피보험자 B의 두 번째 입원 → 지급 (한도 반영)
- 시나리오 2: 계약자 A 본인의 입원 → 피보험자가 아니므로 부지급

계약·고객은 B0의 PO-001과 가상 인물 A·B를 쓴다(계약 시스템에는 계약을 만드는 API가 없다).
입퇴원확인서 본문의 SHA-256이 xlsx 「제출서류」 시트의 content_hash다.

사용: uv run --with python-docx --with openpyxl python make_scenario_upload.py <출력 폴더>
"""
import hashlib
import sys
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.shared import Pt
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
FONT = "Apple SD Gothic Neo"

SCENARIOS = [
    {
        "no": 1, "title": "피보험자 B의 두 번째 입원 (지급)",
        "story": ("피보험자 가상 인물 B가 2026년 6월 2일 가상 의료기관 H-002에 입원해 6월 5일 퇴원했다. "
                  "B는 같은 계약으로 3월에도 입원해 청구(CL-001)한 적이 있다. B가 직접 보험금을 청구한다."),
        "request_key": "REQ-S1-0001", "submitted_on": "2026-06-08",
        "submitter": ("IP-0002", "가상 인물 B", "TKN-B"), "patient": ("IP-0002", "가상 인물 B", "TKN-B"),
        "relation": "본인 (피보험자)", "accident_no": "ACC-0101", "provider": "H-002",
        "admission": "2026-06-02", "discharge": "2026-06-05", "issued": "2026-06-05",
        "form_id": "UP-S1-01", "cert_id": "UP-S1-02",
    },
    {
        "no": 2, "title": "계약자 A 본인의 입원 (부지급)",
        "story": ("계약자 가상 인물 A가 2026년 7월 10일 가상 의료기관 H-004에 입원해 7월 14일 퇴원했다. "
                  "A는 이 계약의 계약자이지만 피보험자는 아니다. A가 자기 입원에 대해 보험금을 청구한다."),
        "request_key": "REQ-S2-0001", "submitted_on": "2026-07-16",
        "submitter": ("IP-0001", "가상 인물 A", "TKN-A"), "patient": ("IP-0001", "가상 인물 A", "TKN-A"),
        "relation": "본인 (계약자)", "accident_no": "ACC-0102", "provider": "H-004",
        "admission": "2026-07-10", "discharge": "2026-07-14", "issued": "2026-07-14",
        "form_id": "UP-S2-01", "cert_id": "UP-S2-02",
    },
]
POLICY, COVERAGE = "TEST-POLICY-001", "INPATIENT-DAILY-A"


def cert_text(s: dict) -> str:
    """입퇴원확인서 본문. 이 문자열의 SHA-256을 서류 해시로 쓴다."""
    return "\n".join([
        "[가상 문서 — 실험용]",
        "입퇴원확인서",
        f"문서 번호: {s['cert_id']}",
        f"환자: {s['patient'][1]} (식별 토큰 {s['patient'][2]})",
        f"의료기관 코드: {s['provider']} (가상 의료기관)",
        f"입원일: {s['admission']}",
        f"퇴원일: {s['discharge']}",
        "진료 구분: 입원",
        "위 사실을 확인합니다.",
        f"{s['issued']}  가상 의료기관 {s['provider']}",
    ])


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def new_doc() -> Document:
    d = Document()
    for name in ("Normal", "Title", "Heading 1", "Heading 2"):
        st = d.styles[name]
        st.font.name = FONT
        st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    d.styles["Normal"].font.size = Pt(10.5)
    return d


def kv_table(d: Document, rows: list[tuple[str, str]]):
    t = d.add_table(rows=0, cols=2)
    t.style = "Table Grid"
    for k, v in rows:
        c = t.add_row().cells
        c[0].text, c[1].text = k, v
        for r in c[0].paragraphs[0].runs:
            r.bold = True
    d.add_paragraph()


def make_docx(s: dict):
    d = new_doc()
    d.add_paragraph("[가상 서류 묶음 — 실험용. 실제 인물·의료기관·보험 계약이 아닙니다]")
    d.add_heading(f"시나리오 {s['no']} 청구 서류: {s['title']}", 0)
    d.add_paragraph("이 묶음에는 보험금 청구서 1부와 입퇴원확인서 1부가 들어 있습니다. 아직 업무 시스템에 접수되지 않은 제출 원본입니다.")

    d.add_heading("1. 보험금 청구서", 1)
    kv_table(d, [
        ("업로드 문서 번호", s["form_id"]),
        ("서류 종류", "보험금 청구서 (CLAIM_FORM)"),
        ("청구 요청 키", s["request_key"]),
        ("제출일", s["submitted_on"]),
        ("계약 번호", POLICY),
        ("보장 코드", COVERAGE + " (테스트 입원일당 A)"),
        ("청구인", f"{s['submitter'][1]} (청구인 번호 {s['submitter'][0]})"),
        ("입원한 사람", f"{s['patient'][1]} (청구인 번호 {s['patient'][0]})"),
        ("청구인과 입원한 사람의 관계", s["relation"]),
        ("사고 번호", s["accident_no"]),
        ("의료기관 코드", s["provider"]),
        ("입원일", s["admission"]),
        ("퇴원일", s["discharge"]),
        ("첨부 서류", f"입퇴원확인서 1부 ({s['cert_id']})"),
        ("접수 담당자", "intake-01"),
    ])
    d.add_heading("입원 경위", 2)
    d.add_paragraph(s["story"])
    d.add_paragraph("위 내용이 사실임을 확인하고 보험금을 청구합니다.")
    d.add_paragraph(f"{s['submitted_on']}  청구인 {s['submitter'][1]}")

    d.add_heading("2. 입퇴원확인서", 1)
    d.add_paragraph(f"업로드 문서 번호: {s['cert_id']}  /  서류 종류: 입퇴원확인서 (HOSPITALIZATION_CERTIFICATE)")
    d.add_paragraph("아래 본문이 원문입니다. 본문의 SHA-256 해시는 접수 자료(xlsx)의 「제출서류」 시트에 있습니다.")
    for line in cert_text(s).split("\n"):
        d.add_paragraph(line)
    name = f"시나리오{s['no']}_청구서류.docx"
    d.save(OUT / name)
    return name


def header(ws, n):
    for c in range(1, n + 1):
        cell = ws.cell(row=1, column=c)
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="DDEBF7")
        cell.alignment = Alignment(vertical="center", wrap_text=True)


def make_xlsx(s: dict, docx_name: str):
    wb = Workbook()
    ws = wb.active
    ws.title = "청구접수"
    head = ["request_key", "submitted_on", "policy_number", "coverage_code", "submitter_no", "patient_no",
            "accident_no", "provider_code", "admission_date", "discharge_date", "intake_actor_id", "claim_form_doc"]
    ws.append(head)
    ws.append([s["request_key"], s["submitted_on"], POLICY, COVERAGE, s["submitter"][0], s["patient"][0],
               s["accident_no"], s["provider"], s["admission"], s["discharge"], "intake-01", s["form_id"]])
    header(ws, len(head))
    for i, w in enumerate([14, 13, 17, 19, 13, 12, 12, 13, 14, 14, 15, 15], 1):
        ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = w

    docs = wb.create_sheet("제출서류")
    head2 = ["upload_doc_id", "document_type", "storage_ref", "content_hash",
             "extracted_insured", "extracted_insured_confidence", "extracted_provider_code",
             "extracted_provider_code_confidence", "extracted_admission_date", "extracted_admission_date_confidence",
             "extracted_discharge_date", "extracted_discharge_date_confidence", "request_key"]
    docs.append(head2)
    text = cert_text(s)
    docs.append([s["cert_id"], "HOSPITALIZATION_CERTIFICATE", f"upload/{docx_name}#{s['cert_id']}", sha(text),
                 s["patient"][2], 0.97, s["provider"], 0.99, s["admission"], 0.96, s["discharge"], 0.96,
                 s["request_key"]])
    header(docs, len(head2))
    for i, w in enumerate([13, 28, 44, 66, 12, 10, 12, 10, 14, 10, 14, 10, 14], 1):
        docs.column_dimensions[docs.cell(row=1, column=i).column_letter].width = w

    info = wb.create_sheet("설명")
    info.append(["항목", "설명"])
    for r in [
        ["자료", f"[가상 자료 — 실험용] 시나리오 {s['no']}: {s['title']}. 아직 업무 시스템에 접수되지 않은 제출 자료입니다."],
        ["청구접수", "보험금 청구서의 내용을 접수 시스템 입력 항목 이름으로 옮긴 행. 청구 접수(A01)의 입력값"],
        ["제출서류", "첨부된 입퇴원확인서. storage_ref·content_hash는 서류 등록(registerDocument)의 입력값"],
        ["extracted_*", "서류에서 자동으로 읽은 값(추출값)과 신뢰도. 담당자가 확인(A03)하기 전에는 확인값이 아닙니다"],
        ["extracted_insured", "환자의 식별 토큰(TKN-…). 청구인 번호가 아니라 토큰으로 적힌 값입니다"],
        ["claim_form_doc", f"같은 내용의 보험금 청구서 문서 번호 ({docx_name} 안의 {s['form_id']})"],
    ]:
        info.append(r)
    header(info, 2)
    info.column_dimensions["A"].width = 18
    info.column_dimensions["B"].width = 100
    name = f"시나리오{s['no']}_접수자료.xlsx"
    wb.save(OUT / name)
    return name, sha(text)


for s in SCENARIOS:
    dn = make_docx(s)
    xn, h = make_xlsx(s, dn)
    print(dn, "|", xn, "| cert hash", h[:16])
