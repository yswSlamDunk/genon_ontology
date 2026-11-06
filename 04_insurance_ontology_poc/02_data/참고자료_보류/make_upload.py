"""보험 청구 심사 온톨로지 추가 인제스천용 업로드 자료 4개를 만든다 (가상 자료).

DOCX 2: 약관(TEST-TERMS-A-1.0), 심사 업무 지침
XLSX 2: 의료기관 목록, 심사 사유 코드표
값은 명세(2.3·5.4·7·8·9절)와 평가 엔진(evaluation.py), B0 데이터에 맞춘다.
"""
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


def new_doc() -> Document:
    d = Document()
    for name in ("Normal", "Title", "Heading 1", "Heading 2", "Heading 3"):
        st = d.styles[name]
        st.font.name = FONT
        st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    d.styles["Normal"].font.size = Pt(10.5)
    return d


def table(d: Document, header: list[str], rows: list[list[str]]):
    t = d.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    for i, h in enumerate(header):
        t.rows[0].cells[i].text = h
        for r in t.rows[0].cells[i].paragraphs[0].runs:
            r.bold = True
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = v
    d.add_paragraph()


# ───────────────────────── 1. 약관 ─────────────────────────
def terms():
    d = new_doc()
    d.add_paragraph("[가상 약관 — 실험용. 실제 보험 상품이 아닙니다]")
    d.add_heading("테스트 입원일당 A 보통약관", 0)
    table(d, ["항목", "내용"], [
        ["약관 코드", "TEST-TERMS-A-1.0"],
        ["상품", "테스트 입원일당 A (보장 코드 INPATIENT-DAILY-A)"],
        ["적용 심사 기준", "INPATIENT-DAILY 1.0 (규칙 버전 RV-001)"],
        ["시행일", "2026-01-01"],
    ])

    arts = [
        ("제1장 총칙", [
            ("제1조", "목적", None,
             ["이 약관은 피보험자가 보장 기간 중 입원한 경우 입원 일수에 따라 정해진 금액(입원일당)을 지급하는 데 필요한 사항을 정합니다."]),
            ("제2조", "용어의 정의", None,
             ["① 계약자: 회사와 계약을 맺고 보험료를 내는 사람",
              "② 피보험자: 입원하면 보험금 지급 대상이 되는 사람",
              "③ 수익자: 보험금을 받는 사람. 이 상품의 수익자는 피보험자로 고정합니다.",
              "④ 보장 기간: 보장이 유효한 기간. 시작일을 포함하고 종료일을 포함하지 않습니다.",
              "⑤ 입원: 의료기관에 입원하여 진료를 받는 것. 입원일과 퇴원일은 입퇴원확인서로 확인합니다.",
              "⑥ 날짜는 서울(Asia/Seoul) 달력 날짜를 기준으로 합니다."]),
        ]),
        ("제2장 보험금의 지급", [
            ("제3조", "보험금의 지급 사유", None,
             ["회사는 피보험자가 보장 기간 중 입원한 경우, 제7조의 입원 일수에 1일 지급액 100,000원을 곱한 금액을 제8조의 한도 안에서 지급합니다."]),
            ("제4조", "피보험자의 확인", "R01 IDENTITY_MATCH",
             ["① 입원한 사람이 입원일 기준으로 이 계약의 피보험자여야 합니다.",
              "② 입원한 사람이 피보험자가 아니면 보험금을 지급하지 않습니다(사유 IDENTITY_MISMATCH).",
              "③ 피보험자 역할을 확인할 수 없으면 판단을 보류하고 담당자가 확인합니다(사유 UNCONFIRMED_FACT)."]),
            ("제5조", "보장 기간", "R02 COVERAGE_PERIOD",
             ["① 입원일이 보장 기간 안에 있고 퇴원일이 보장 종료일 이전(종료일 포함)이어야 합니다.",
              "② 입원일이 보장 기간 밖이면 지급하지 않습니다(사유 OUTSIDE_COVERAGE).",
              "③ 입원이 보장 종료일을 넘어 이어지면 자동 계산하지 않고 담당자가 검토합니다(사유 PERIOD_CROSSING)."]),
            ("제6조", "대기 기간", "R03 WAITING_PERIOD",
             ["① 보장 시작일로부터 30일이 지난 날 이후의 입원에 대해 지급합니다. 입원일이 보장 시작일 + 30일 이상이어야 합니다.",
              "② 예: 보장 시작일이 2026-01-01이면 대기 기간은 2026-01-31에 끝납니다. 2026-01-30 입원은 지급하지 않고, 2026-01-31 입원은 지급합니다.",
              "③ 대기 기간 중 입원은 지급하지 않습니다(사유 WAITING_NOT_MET)."]),
            ("제7조", "입원 일수의 계산", "R05 POSITIVE_STAY",
             ["① 입원 일수는 퇴원일에서 입원일을 뺀 날수입니다. 입원일은 포함하고 퇴원일은 포함하지 않습니다.",
              "② 같은 날 입원하고 퇴원하면 0일이며 지급하지 않습니다(사유 ZERO_STAY).",
              "③ 퇴원일이 입원일보다 앞서면 자료 오류로 보고 담당자가 바로잡습니다(사유 INVALID_DATES)."]),
            ("제8조", "지급 한도", "R07 LIMIT_AVAILABLE",
             ["① 한 보장 기간에 피보험자별로 최대 5일까지 지급합니다.",
              "② 남은 일수는 5일에서 이미 지급한 일수와 다른 청구로 지급하기로 예약한 일수를 뺀 값입니다.",
              "③ 남은 일수가 없으면 지급하지 않습니다(사유 LIMIT_EXHAUSTED).",
              "④ 한도는 지급을 결정하는 시점에 다시 확인합니다."]),
            ("제9조", "중복 지급의 제한", "R06 DUPLICATE_CLEAR",
             ["① 같은 피보험자의 같은 보장, 같은 입원 사건에 대해 이미 승인되거나 지급된 다른 청구가 있으면 중복 여부를 담당자가 검토합니다(사유 DUPLICATE_REVIEW).",
              "② 비슷한 입원 기록이라는 이유만으로 같은 사건이라고 확정하지 않습니다."]),
        ]),
        ("제3장 보험금의 청구", [
            ("제10조", "청구할 수 있는 사람", None,
             ["계약자 또는 피보험자가 청구할 수 있습니다. 대리인 청구는 이 상품에서 받지 않습니다."]),
            ("제11조", "청구 서류", "R04 EVIDENCE_COMPLETE",
             ["① 입퇴원확인서 1부 이상을 내야 하며, 담당자가 확인을 마쳐야 합니다.",
              "② 담당자는 입퇴원확인서에서 피보험자, 의료기관 코드, 입원일, 퇴원일 네 항목을 확인합니다.",
              "③ 서류가 없거나 확인되지 않았으면 보완을 요청합니다(사유 MISSING_DOCUMENT).",
              "④ 서류의 확인값이 입원 사건과 다르면 담당자가 사실을 다시 확인합니다(사유 FACT_CONFLICT).",
              "⑤ 서류에서 자동으로 읽은 값(추출값)은 담당자가 확인한 값과 같은 것으로 보지 않습니다."]),
            ("제12조", "보험금을 받는 사람", None,
             ["보험금은 수익자(피보험자)에게 지급합니다."]),
        ]),
        ("제4장 심사와 지급", [
            ("제13조", "심사와 결정", None,
             ["① 회사의 심사 시스템은 제4조부터 제11조까지를 확인해 지급 후보, 부지급 후보, 서류 보완, 담당자 검토 중 하나의 의견을 냅니다.",
              "② 지급과 부지급의 최종 결정은 담당 심사자가 합니다.",
              "③ 확인되지 않은 사실을 임의로 채워 판단하지 않습니다."]),
            ("제14조", "지급 결과의 확인", None,
             ["① 지급 요청의 결과를 알 수 없으면 새로 지급하지 않고, 지급 내역을 조회해 결과를 확정합니다.",
              "② 지급 요청을 다시 할 때는 처음과 같은 지급 키를 씁니다."]),
        ]),
    ]
    for chapter, items in arts:
        d.add_heading(chapter, 1)
        for no, title, rule, paras in items:
            d.add_heading(f"{no} ({title})", 2)
            for p in paras:
                d.add_paragraph(p)
            if rule:
                d.add_paragraph(f"관련 심사 규칙: {rule}")
    d.add_heading("부칙", 1)
    d.add_paragraph("이 약관은 2026-01-01부터 시행합니다.")
    d.save(OUT / "TEST-TERMS-A-1.0_입원일당A_약관.docx")


# ───────────────────────── 2. 심사 업무 지침 ─────────────────────────
def guideline():
    d = new_doc()
    d.add_paragraph("[가상 업무 지침 — 실험용]")
    d.add_heading("입원일당 청구 심사 업무 지침 v1.0", 0)
    table(d, ["항목", "내용"], [
        ["문서 번호", "GUIDE-INPATIENT-1.0"],
        ["적용 상품·약관", "테스트 입원일당 A / TEST-TERMS-A-1.0"],
        ["적용 심사 기준", "INPATIENT-DAILY 1.0 (RV-001)"],
        ["시행일", "2026-01-01"],
    ])

    d.add_heading("1. 목적", 1)
    d.add_paragraph("입원일당 청구를 접수부터 지급까지 같은 기준으로 처리하기 위해, 청구 상태와 평가 결과에 따라 담당자가 할 일을 정합니다.")

    d.add_heading("2. 담당자와 할 수 있는 업무", 1)
    table(d, ["담당자", "담당자 ID 예", "할 수 있는 업무 (액션)"], [
        ["접수 담당자", "intake-01", "청구 접수(A01), 서류 연결·교체(A02)"],
        ["담당 심사자", "reviewer-01", "서류 확인(A03), 평가(A04), 보완 요청(A05), 심사 업무 해결(A06), 지급 승인(A07), 부지급 결정(A08)"],
        ["지급 담당자", "payment-01", "지급 요청(A09), 지급 결과 대사(A11)"],
    ])
    d.add_paragraph("지급 승인·부지급·지급 요청은 실행 전에 사람의 승인을 받고, 실행한 뒤에는 되돌리지 않습니다.")

    d.add_heading("3. 청구 상태별 처리", 1)
    steps = [
        ("RECEIVED (접수됨)", "청구를 평가합니다(A04). 서류가 없으면 평가 결과에 따라 보완을 요청합니다."),
        ("NEED_INFO (서류 보완 필요)", "보완 요청(A05)을 보내고, 서류가 오면 연결(A02)하고 확인(A03)한 뒤, 보완 업무를 해결(A06)하고 다시 평가(A04)합니다."),
        ("UNDER_REVIEW (심사 중)", "열린 심사 업무를 확인하고 근거를 남겨 해결(A06)한 뒤 다시 평가(A04)합니다."),
        ("READY_FOR_DECISION (결정 대기)", "4절의 승인 전 확인을 마치고, 평가 결과가 지급 후보면 지급 승인(A07), 부지급 후보면 부지급 결정(A08)을 합니다."),
        ("APPROVED (지급 승인됨)", "지급 담당자가 지급 요청(A09)을 합니다. 결과를 알 수 없으면 지급 결과 대사(A11)로 확정합니다."),
        ("PAID (지급 완료) / REJECTED (부지급)", "종결입니다. 추가 업무가 없습니다."),
    ]
    for i, (state, todo) in enumerate(steps, 1):
        d.add_heading(f"3.{i} {state}", 2)
        d.add_paragraph(todo)

    d.add_heading("4. 평가 결과별 조치", 1)
    table(d, ["평가 결과", "뜻", "담당자 조치"], [
        ["PAYABLE_CANDIDATE", "지급 후보. 모든 규칙을 충족", "승인 전 확인(5절) 후 지급 승인(A07)"],
        ["NOT_PAYABLE_CANDIDATE", "부지급 후보. 확인된 조건 미충족", "사유 코드와 약관 조항을 확인하고 부지급 결정(A08)"],
        ["NEED_INFO", "서류 보완 필요", "보완 요청(A05) → 서류 연결(A02)·확인(A03) → 업무 해결(A06) → 재평가(A04)"],
        ["MANUAL_REVIEW", "담당자 검토 필요", "생성된 심사 업무를 근거와 함께 해결(A06)하고 재평가(A04)"],
    ])

    d.add_heading("5. 지급 승인 전 확인", 1)
    for p in ["① 결정의 근거가 되는 평가가 그 청구의 현재 평가인지 확인합니다.",
              "② 열린 심사 업무가 0건인지 확인합니다.",
              "③ 보험금을 받을 사람이 수익자(피보험자)인지 확인합니다.",
              "④ 남은 한도는 승인할 때 시스템이 다시 확인합니다. 평가 이후 서류나 사건이 바뀌었으면 승인이 거절되며(STALE_ASSESSMENT), 다시 평가해야 합니다."]:
        d.add_paragraph(p)

    d.add_heading("6. 유의 사항", 1)
    for p in ["① 확인되지 않은 사실을 임의로 채우지 않습니다. 모르는 값은 모른다고 기록합니다.",
              "② 서류에서 자동으로 읽은 값(추출값)은 확인값이 아닙니다. 서류 확인(A03)을 거친 값만 씁니다.",
              "③ 이미 승인 근거로 쓰인 서류의 확인값은 고치지 않습니다.",
              "④ 지급 결과를 알 수 없을 때 새 지급 지시를 만들지 않습니다. 대사(A11)로 확인합니다.",
              "⑤ 비슷한 입원 기록만으로 중복 청구라고 단정하지 않습니다. 중복 검토 업무로 처리합니다."]:
        d.add_paragraph(p)
    d.save(OUT / "입원일당_청구심사_업무지침_v1.0.docx")


# ───────────────────────── 3. 의료기관 목록 ─────────────────────────
def style_header(ws, ncol):
    for c in range(1, ncol + 1):
        cell = ws.cell(row=1, column=c)
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="DDEBF7")
        cell.alignment = Alignment(vertical="center", wrap_text=True)


def providers():
    wb = Workbook()
    ws = wb.active
    ws.title = "의료기관"
    head = ["provider_code", "기관명", "종별", "시도", "시군구", "병상 수", "입원 진료", "주요 진료과", "개설일", "정보 기준일"]
    rows = [
        ["H-001", "가상한빛병원", "병원", "서울특별시", "가상구", 120, "Y", "내과, 정형외과", "2015-04-01", "2026-01-01"],
        ["H-002", "가상온누리의원", "의원", "경기도", "가상시", 20, "Y", "외과", "2018-09-15", "2026-01-01"],
        ["H-003", "가상새솔종합병원", "종합병원", "부산광역시", "가상구", 450, "Y", "내과, 외과, 신경과", "2009-03-02", "2026-01-01"],
        ["H-004", "가상푸른요양병원", "요양병원", "대전광역시", "가상구", 200, "Y", "재활의학과", "2012-11-20", "2026-01-01"],
        ["H-005", "가상밝은의원", "의원", "서울특별시", "가상구", 0, "N", "가정의학과", "2020-06-01", "2026-01-01"],
    ]
    ws.append(head)
    for r in rows:
        ws.append(r)
    style_header(ws, len(head))
    for col, w in zip("ABCDEFGHIJ", [14, 18, 10, 12, 10, 9, 9, 20, 12, 12]):
        ws.column_dimensions[col].width = w

    info = wb.create_sheet("설명")
    info.append(["항목", "설명"])
    for r in [
        ["자료", "[가상 자료 — 실험용] 입원일당 심사에서 참고하는 의료기관 기준 정보. 실제 의료기관이 아닙니다."],
        ["provider_code", "의료기관 코드. 접수 시스템의 청구 접수(provider_code), 심사 시스템의 입원 사건(provider_code), 입퇴원확인서의 의료기관 코드와 같은 값"],
        ["종별", "종합병원, 병원, 요양병원, 의원"],
        ["입원 진료", "Y = 입원 진료를 하는 기관, N = 외래만 하는 기관"],
        ["정보 기준일", "이 목록의 값이 유효한 기준 날짜"],
        ["주의", "이 목록은 심사 참고 정보입니다. 보험금 지급 여부는 약관과 심사 기준(RV-001)으로만 판단합니다."],
    ]:
        info.append(r)
    style_header(info, 2)
    info.column_dimensions["A"].width = 14
    info.column_dimensions["B"].width = 90
    wb.save(OUT / "의료기관_목록.xlsx")


# ───────────────────────── 4. 심사 사유 코드표 ─────────────────────────
def reason_codes():
    wb = Workbook()
    ws = wb.active
    ws.title = "사유코드"
    head = ["reason_code", "사유", "관련 규칙", "규칙 판정", "평가 결과에 주는 영향", "생성되는 심사 업무", "약관 조항", "담당자 안내", "다음 업무(액션)"]
    rows = [
        ["MISSING_DOCUMENT", "필수 서류 누락·미확인", "R04", "UNKNOWN", "NEED_INFO", "EVIDENCE_REQUEST", "제11조",
         "입퇴원확인서가 없거나 확인되지 않았습니다.", "보완 요청(A05) → 서류 연결(A02) → 서류 확인(A03) → 업무 해결(A06) → 재평가(A04)"],
        ["FACT_CONFLICT", "서류와 사건 사실 불일치", "R04", "UNKNOWN", "MANUAL_REVIEW", "FACT_REVIEW", "제11조",
         "서류 확인값이 입원 사건과 다릅니다. 원본을 다시 대조하세요.", "서류 확인(A03) 또는 업무 해결(A06, 사건 정정) → 재평가(A04)"],
        ["UNCONFIRMED_FACT", "핵심 사실 미확인", "R01, R04", "UNKNOWN", "MANUAL_REVIEW (서류 보완으로 해소되면 NEED_INFO)", "FACT_REVIEW", "제4조, 제11조",
         "피보험자 역할이나 입원 사실이 확인되지 않았습니다.", "서류 확인(A03) 또는 업무 해결(A06) → 재평가(A04)"],
        ["INVALID_DATES", "입퇴원일 역전", "R05", "UNKNOWN", "MANUAL_REVIEW", "DATA_REPAIR", "제7조",
         "퇴원일이 입원일보다 앞섭니다. 자료를 바로잡으세요.", "업무 해결(A06) → 재평가(A04)"],
        ["PERIOD_CROSSING", "보장 종료 경계를 넘는 입원", "R02", "UNKNOWN", "MANUAL_REVIEW", "PERIOD_REVIEW", "제5조",
         "입원이 보장 종료일을 넘습니다. 자동 계산하지 않습니다.", "업무 해결(A06) → 재평가(A04)"],
        ["DUPLICATE_REVIEW", "중복 청구 검토", "R06", "UNKNOWN", "MANUAL_REVIEW", "DUPLICATE_REVIEW", "제9조",
         "같은 사건·보장에 승인되거나 지급된 다른 청구가 있습니다.", "업무 해결(A06, 별개 사건이면 사건 정정) → 재평가(A04)"],
        ["DEPENDENCY_UNAVAILABLE", "필수 정보 조회 실패", "전체", "UNKNOWN", "MANUAL_REVIEW", "DATA_REPAIR", "제13조",
         "규칙·한도 등 필요한 정보를 조회하지 못했습니다.", "원인 해소 후 업무 해결(A06) → 재평가(A04)"],
        ["IDENTITY_MISMATCH", "피보험자 불일치", "R01", "FAIL", "NOT_PAYABLE_CANDIDATE", "없음", "제4조",
         "입원한 사람이 이 계약의 피보험자가 아닙니다.", "부지급 결정(A08)"],
        ["OUTSIDE_COVERAGE", "보장 기간 밖 입원", "R02", "FAIL", "NOT_PAYABLE_CANDIDATE", "없음", "제5조",
         "입원일이 보장 기간 밖입니다.", "부지급 결정(A08)"],
        ["WAITING_NOT_MET", "대기 기간 중 입원", "R03", "FAIL", "NOT_PAYABLE_CANDIDATE", "없음", "제6조",
         "보장 시작 후 30일이 지나기 전에 입원했습니다.", "부지급 결정(A08)"],
        ["ZERO_STAY", "입원 일수 0일", "R05", "FAIL", "NOT_PAYABLE_CANDIDATE", "없음", "제7조",
         "같은 날 입원하고 퇴원했습니다.", "부지급 결정(A08)"],
        ["LIMIT_EXHAUSTED", "지급 한도 소진", "R07", "FAIL", "NOT_PAYABLE_CANDIDATE", "없음", "제8조",
         "보장 기간 한도 5일을 모두 썼습니다.", "부지급 결정(A08)"],
    ]
    ws.append(head)
    for r in rows:
        ws.append(r)
    style_header(ws, len(head))
    for col, w in zip("ABCDEFGHI", [24, 22, 10, 10, 30, 20, 12, 44, 60]):
        ws.column_dimensions[col].width = w

    tt = wb.create_sheet("심사업무유형")
    tt.append(["task_type", "업무", "생기는 사유 코드", "해결 방법", "해결 액션"])
    for r in [
        ["EVIDENCE_REQUEST", "서류 보완", "MISSING_DOCUMENT", "보완 서류를 받아 연결·확인한 뒤 해결 근거를 남깁니다", "A06 심사 업무 해결"],
        ["FACT_REVIEW", "사실 확인", "FACT_CONFLICT, UNCONFIRMED_FACT", "원본 대조로 사실을 확정하고, 필요하면 확인된 사건으로 청구를 다시 연결합니다", "A06 심사 업무 해결"],
        ["DATA_REPAIR", "자료 보정", "INVALID_DATES, DEPENDENCY_UNAVAILABLE", "잘못된 자료나 조회 실패 원인을 바로잡습니다", "A06 심사 업무 해결"],
        ["PERIOD_REVIEW", "보장 기간 검토", "PERIOD_CROSSING", "보장 종료 경계를 넘는 입원을 담당자가 판단합니다", "A06 심사 업무 해결"],
        ["DUPLICATE_REVIEW", "중복 검토", "DUPLICATE_REVIEW", "같은 사건인지 확인하고, 별개 사건이면 근거를 남겨 사건 연결을 정정합니다", "A06 심사 업무 해결"],
    ]:
        tt.append(r)
    style_header(tt, 5)
    for col, w in zip("ABCDE", [20, 14, 34, 60, 20]):
        tt.column_dimensions[col].width = w

    info = wb.create_sheet("설명")
    info.append(["항목", "설명"])
    for r in [
        ["자료", "[가상 자료 — 실험용] 심사 평가(Assessment)의 사유 코드(reason_codes)와 심사 업무(ReviewTask)의 업무 유형(task_type)을 담당자 말로 풀어 쓴 표"],
        ["규칙 판정", "UNKNOWN = 판단 보류(확인 필요), FAIL = 확인된 조건 미충족"],
        ["약관 조항", "TEST-TERMS-A-1.0 테스트 입원일당 A 보통약관의 조항"],
    ]:
        info.append(r)
    style_header(info, 2)
    info.column_dimensions["A"].width = 14
    info.column_dimensions["B"].width = 100
    wb.save(OUT / "심사_사유코드표.xlsx")


terms()
guideline()
providers()
reason_codes()
for p in sorted(OUT.iterdir()):
    print(p.name, p.stat().st_size)
