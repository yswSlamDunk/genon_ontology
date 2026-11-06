"""보험 청구 심사 온톨로지 PoC 보고서 PPT 빌드.

양식: 온톨로지_솔루션_오픈소스_조사_v2.pptx (표지 슬라이드·마스터·레이아웃 재사용, 본문은 같은 스타일 규칙으로 생성)
사용: uv run --with python-pptx python build_poc_deck.py <template.pptx> <arch.png> <out.pptx>
"""
import re
import sys

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt, Emu
from lxml import etree

TPL, ARCH, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
FONT = "Pretendard"
NAVY, BLUE, TEXT, MUTED, BLACK = "002060", "1F4E79", "262626", "595959", "000000"
PANEL, SIDE, WHITE, LINE = "DDEBF7", "F2F6FB", "FFFFFF", "9DC3E6"
TABLE_STYLE = "{5940675A-B579-460E-94D1-54222C63F5DA}"

prs = Presentation(TPL)
BLANK = [l for l in prs.slide_layouts if l.name == "빈 화면"][0]

# 표지만 남기고 지움
ids = prs.slides._sldIdLst
for sld in list(ids)[1:]:
    prs.part.drop_rel(sld.get(qn("r:id")))
    ids.remove(sld)


def rgb(h):
    return RGBColor.from_string(h)


def set_font(run, size, bold=False, color=TEXT, italic=False):
    f = run.font
    f.size, f.bold, f.italic = Pt(size), bold, italic
    f.color.rgb = rgb(color)
    rpr = run._r.get_or_add_rPr()
    for tag in ("a:latin", "a:ea", "a:cs"):
        el = rpr.find(qn(tag))
        if el is None:
            el = etree.SubElement(rpr, qn(tag))
        el.set("typeface", FONT)


def add_runs(p, text, size, bold, color, italic=False):
    """**굵게** 표기를 run으로 나눔."""
    parts = re.split(r"(\*\*[^*]+\*\*)", text)
    for part in parts:
        if not part:
            continue
        b = part.startswith("**") and part.endswith("**")
        r = p.add_run()
        r.text = part[2:-2] if b else part
        set_font(r, size, bold or b, BLUE if (b and not bold and color == TEXT) else color, italic)


def bullet_ppr(p, level=0):
    ppr = p._p.get_or_add_pPr()
    ppr.set("marL", str(201168 + level * 228600))
    ppr.set("indent", "-164592")
    bu = etree.SubElement(ppr, qn("a:buChar"))
    bu.set("char", "•" if level == 0 else "–")


def spacing(p, after_pt):
    ppr = p._p.get_or_add_pPr()
    sa = etree.SubElement(ppr, qn("a:spcAft"))
    etree.SubElement(sa, qn("a:spcPts")).set("val", str(int(after_pt * 100)))


def textbox(slide, x, y, w, h, items, anchor="t", align=PP_ALIGN.LEFT, autofit=False):
    """items: list of (kind, text) — kind: h(heading) b(bullet) s(sub-bullet) t(plain) or dict."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    bp = tf._txBody.find(qn("a:bodyPr"))
    for k, v in (("lIns", "45720"), ("tIns", "27432"), ("rIns", "45720"), ("bIns", "27432")):
        bp.set(k, v)
    tf.vertical_anchor = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}[anchor]
    first = True
    for it in items:
        kind, text = it[0], it[1]
        opt = it[2] if len(it) > 2 else {}
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = opt.get("align", align)
        size = opt.get("size")
        if kind == "h":
            add_runs(p, text, size or 16, True, opt.get("color", BLUE))
            spacing(p, opt.get("after", 6))
        elif kind == "b":
            bullet_ppr(p)
            add_runs(p, text, size or 14, opt.get("bold", False), opt.get("color", TEXT))
            spacing(p, opt.get("after", 4))
        elif kind == "s":
            bullet_ppr(p, 1)
            add_runs(p, text, size or 12, False, opt.get("color", TEXT))
            spacing(p, opt.get("after", 3))
        else:
            add_runs(p, text, size or 14, opt.get("bold", False), opt.get("color", TEXT), opt.get("italic", False))
            spacing(p, opt.get("after", 4))
    return tb


def box(slide, x, y, w, h, fill=PANEL, line=None, dash=False, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.04):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = radius
    if fill:
        s.fill.solid()
        s.fill.fore_color.rgb = rgb(fill)
    else:
        s.fill.background()
    if line:
        s.line.color.rgb = rgb(line)
        s.line.width = Pt(1.25)
        if dash:
            ln = s.line._get_or_add_ln()
            etree.SubElement(ln, qn("a:prstDash")).set("val", "dash")
    else:
        s.line.fill.background()
    s.shadow.inherit = False
    return s


def panel(slide, x, y, w, h, items, fill=PANEL, pad=0.15):
    box(slide, x, y, w, h, fill)
    return textbox(slide, x + pad, y + 0.12, w - 2 * pad, h - 0.2, items)


def table(slide, x, y, w, rows, widths, size=12, first_col=True, row_h=0.36, header=True):
    nr, nc = len(rows), len(rows[0])
    gs = slide.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(w), Inches(row_h * nr))
    tbl = gs.table
    tblPr = tbl._tbl.tblPr
    for a in ("firstRow", "bandRow", "firstCol", "lastRow", "lastCol", "bandCol"):
        if tblPr.get(a) is not None:
            del tblPr.attrib[a]
    sid = tblPr.find(qn("a:tableStyleId"))
    if sid is None:
        sid = etree.SubElement(tblPr, qn("a:tableStyleId"))
    sid.text = TABLE_STYLE
    tot = sum(widths)
    for i, cw in enumerate(widths):
        tbl.columns[i].width = Emu(int(Inches(w) * cw / tot))
    for r in range(nr):
        tbl.rows[r].height = Inches(row_h)
        for c in range(nc):
            cell = tbl.cell(r, c)
            hdr = header and r == 0
            fc = first_col and c == 0 and not hdr
            cell.fill.solid()
            cell.fill.fore_color.rgb = rgb(NAVY if hdr else PANEL if fc else WHITE)
            cell.margin_left = cell.margin_right = Emu(73152)
            cell.margin_top = cell.margin_bottom = Emu(36576)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = cell.text_frame
            tf.word_wrap = True
            lines = str(rows[r][c]).split("\n")
            for li, line in enumerate(lines):
                p = tf.paragraphs[0] if li == 0 else tf.add_paragraph()
                p.alignment = PP_ALIGN.LEFT
                if hdr:
                    add_runs(p, line, size, True, WHITE)
                elif fc:
                    add_runs(p, line, size, True, BLUE)
                else:
                    add_runs(p, line, size, False, TEXT)
    return gs


PAGE = [1]


def slide_(title, sub, step=None):
    s = prs.slides.add_slide(BLANK)
    PAGE[0] += 1
    textbox(s, 0.45, 0.24, 12.40 if not step else 9.0, 0.54, [("t", title, {"size": 20, "bold": True, "color": BLACK})])
    textbox(s, 0.40, 0.74, 12.50, 0.50, [("t", sub, {"size": 14})])
    textbox(s, 12.20, 7.05, 0.70, 0.30, [("t", str(PAGE[0]), {"size": 10, "color": MUTED, "align": PP_ALIGN.RIGHT})])
    if step:
        textbox(s, 9.60, 0.28, 3.30, 0.40, [("t", step, {"size": 12, "bold": True, "color": BLUE, "align": PP_ALIGN.RIGHT})])
    return s


def caption(s, x, y, w, text):
    textbox(s, x, y, w, 0.30, [("t", text, {"size": 10, "color": MUTED, "align": PP_ALIGN.CENTER})])


def source(s, text):
    textbox(s, 0.40, 7.02, 11.6, 0.30, [("t", text, {"size": 10, "color": MUTED})])


def capture(s, x, y, w, h, text):
    box(s, x, y, w, h, fill="FAFAFA", line="BFBFBF", dash=True, radius=0.02)
    textbox(s, x, y, w, h, [("t", "화면 캡처 자리", {"size": 14, "bold": True, "color": "7F7F7F", "align": PP_ALIGN.CENTER}),
                            ("t", text, {"size": 12, "color": "7F7F7F", "align": PP_ALIGN.CENTER})], anchor="m")


def stat(s, x, y, w, h, num, label, sub=None):
    box(s, x, y, w, h, PANEL)
    items = [("t", num, {"size": 36, "bold": True, "color": BLUE, "align": PP_ALIGN.CENTER, "after": 0}),
             ("t", label, {"size": 14, "bold": True, "color": TEXT, "align": PP_ALIGN.CENTER, "after": 2})]
    if sub:
        items.append(("t", sub, {"size": 11, "color": MUTED, "align": PP_ALIGN.CENTER}))
    textbox(s, x + 0.1, y + 0.05, w - 0.2, h - 0.1, items, anchor="m")


def arrow(s, x, y, w=0.45, h=0.4):
    a = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x), Inches(y), Inches(w), Inches(h))
    a.fill.solid()
    a.fill.fore_color.rgb = rgb(LINE)
    a.line.fill.background()
    a.shadow.inherit = False


def code(s, x, y, w, h, text):
    box(s, x, y, w, h, fill="F2F2F2", radius=0.03)
    textbox(s, x + 0.15, y, w - 0.3, h, [("t", text, {"size": 13, "color": TEXT})], anchor="m")



IMG = "/Users/simpleisbest/Desktop/workplace/ontology/04_insurance_ontology_poc/images/"


def pic(s, path, x, y, w=None, h=None):
    kw = {}
    if w: kw["width"] = Inches(w)
    if h: kw["height"] = Inches(h)
    return s.shapes.add_picture(IMG + path, Inches(x), Inches(y), **kw)


def screen(title, sub, step, img, cap, side):
    s = slide_(title, sub, step)
    pic(s, img, 0.45, 1.42, h=5.09)
    caption(s, 0.45, 6.58, 8.14, cap)
    panel(s, 8.80, 1.30, 4.10, 5.65, side, fill=SIDE)
    return s


def node(s, x, y, w, h, title, sub=None, fill=WHITE, line=BLUE, dash=False, tsize=14, color=BLUE):
    box(s, x, y, w, h, fill, line=line, dash=dash, radius=0.08)
    items = [("t", title, {"size": tsize, "bold": True, "color": color, "align": PP_ALIGN.CENTER, "after": 2})]
    if sub:
        items.append(("t", sub, {"size": 12, "color": TEXT, "align": PP_ALIGN.CENTER}))
    textbox(s, x + 0.05, y, w - 0.1, h, items, anchor="m")


# ── 1. 표지 ─────────────────────────────────────────────
cover = prs.slides[0]
if cover.has_notes_slide:
    cover.notes_slide.notes_text_frame.text = ""
for sh in cover.shapes:
    if sh.has_text_frame and sh.text_frame.text.strip():
        runs = [r for p in sh.text_frame.paragraphs for r in p.runs]
        if sh.name == "TextBox 1":
            runs[0].text = "보험 청구 심사 온톨로지 PoC"
        elif sh.name == "TextBox 2":
            runs[0].text = "Ontological Studio로 구현한 입원 정액보험 청구 심사 — 업무 시스템 연결부터 비정형 서류 접수까지"
        for r in runs[1:]:
            r.text = ""


# ── 2. 개요 ─────────────────────────────────────────────
s = slide_("PoC 개요 — 목적과 결론",
           "앞선 조사에서 분석한 Ontological Studio를 실제 업무(입원 정액보험 청구 심사)에 적용해, 구축부터 활용까지 어디까지 되는지 확인함")
panel(s, 0.45, 1.40, 6.10, 2.05, [
    ("h", "① 확인할 것"),
    ("b", "읽기 — 시스템마다 흩어진 고객·계약·청구를 잇고 질문에 답하는가"),
    ("b", "쓰기 — 온톨로지에서 업무 시스템의 상태를 안전하게 바꾸는가"),
    ("b", "추가 인제스천 — 비정형 서류를 올려 업무에 반영하는가"),
])
panel(s, 6.75, 1.40, 6.10, 2.05, [
    ("h", "② 한 것"),
    ("b", "가상 업무 시스템 4개(API 44개)를 만들어 Studio에 등록"),
    ("b", "1차 구축: 클래스 17 · 관계 32 · 액션 10"),
    ("b", "서류 업로드 → 실제 청구 접수(RC-0002 · CL-002)"),
])
panel(s, 0.45, 3.65, 12.40, 3.25, [
    ("h", "③ 결론", {"size": 18, "after": 10}),
    ("b", "**온톨로지는 시스템마다 다른 번호를 관계로 잇는다** — 「입원한 사람이 이 계약의 피보험자인가」를 계약자와 구분해 답했다", {"size": 15, "after": 8}),
    ("b", "**액션은 여러 업무 API를 묶은 업무 단위다** — 되돌리기·중복 거르기·원자성은 업무 시스템 API가 맡으므로 **API 설계가 먼저**다", {"size": 15, "after": 8}),
    ("b", "**비정형 서류도 스키마 변경 없이 업무에 반영된다** — 구축(추가 인제스천)으로 그래프에 넣고, 질의·액션으로 업무 시스템에 접수", {"size": 15, "after": 8}),
    ("b", "**운영에 쓰려면 Studio 개선이 필요하다** — 액션 뒤 재적재(동기화 버튼), 질의 범위 선택, 스캔 문서 처리", {"size": 15, "after": 8}),
])

# ── 3. 과제 (핵심만) ───────────────────────────────────
s = slide_("1. 과제 — 입원 정액보험 청구 심사",
           "핵심은 하나다. 같은 사람이 시스템마다 다른 번호로 기록돼 있어, 「입원한 사람이 이 계약의 피보험자인가」를 담당자가 직접 대조해야 한다")
for i, (h, d) in enumerate([("상품", "입원 1일 10만 원\n1년에 최대 5일, 가입 후 30일 대기"),
                            ("사람", "A — 계약자 (보험료를 내는 사람)\nB — 피보험자·수익자 (보장받는 사람)"),
                            ("업무 흐름", "접수 → 서류 확인 → 평가 → 승인 → 지급")]):
    y = 1.45 + i * 1.40
    box(s, 0.45, y, 4.60, 1.25, PANEL, radius=0.06)
    textbox(s, 0.60, y + 0.08, 4.30, 1.10, [("t", h, {"size": 15, "bold": True, "color": BLUE, "after": 4}), ("t", d, {"size": 13})])
table(s, 5.30, 1.45, 7.55, [
    ["대상", "계약 시스템", "접수 시스템", "잇는 키"],
    ["계약자 A", "C-10001", "IP-0001", "동일인 토큰 TKN-A"],
    ["피보험자 B", "C-10002", "IP-0002", "동일인 토큰 TKN-B"],
    ["계약", "PO-001", "TEST-POLICY-001", "대외 계약 번호"],
    ["청구", "–", "RC-0001 (심사: CL-001)", "접수 번호"],
], [1.5, 1.6, 2.3, 2.15], row_h=0.62)
panel(s, 5.30, 4.75, 7.55, 2.15, [
    ("h", "온톨로지가 하는 일", {"size": 14}),
    ("b", "담당자가 하던 번호 대조를 **관계**로 만들어 둔다", {"size": 13}),
    ("b", "사람과 계약 사이에 **계약 역할**(계약자 / 피보험자, 유효 기간)을 둬서 둘을 섞지 않는다", {"size": 13}),
    ("b", "예: A가 낸 청구라도 입원한 사람이 B이면 지급 대상, A 본인이 입원하면 부지급", {"size": 13}),
], fill=SIDE)
# ── 4. 전체 구성 ────────────────────────────────────────
s = slide_("2. 전체 구성 — Studio, 업무 시스템 서버, 업무 DB",
           "읽기는 조회 API와 데이터소스로, 쓰기는 오직 액션 → 업무 시스템 API로. Studio는 DB를 직접 고치지 않는다")
s.shapes.add_picture(ARCH, Inches(0.45), Inches(1.40), width=Inches(12.40))
caption(s, 0.45, 5.88, 12.40, "Studio는 데스크톱 v0.1.1, 업무 시스템 서버는 FastAPI로 직접 만듦")
panel(s, 0.45, 6.25, 6.10, 0.70, [("t", "**읽기** — 구축 에이전트가 조회 API로 읽어 그래프에 적재. 데이터소스는 읽기 전용 계정", {"size": 13})])
panel(s, 6.75, 6.25, 6.10, 0.70, [("t", "**쓰기** — 액션 실행기가 인증·멱등성 키를 붙여 API 호출. DB는 업무 서버만 씀", {"size": 13})])

# ── 7. 역할 분담 ────────────────────────────────────────
s = slide_("3. 역할 분담 — Studio는 조율, 업무 규칙은 업무 시스템",
           "언제·어떤 순서로·누구 승인으로 API를 부를지는 Studio가, 무엇을 바꾸고 무엇을 막을지는 업무 시스템이 맡는다",
           "단계 ⑧ 실행 (Action)")
table(s, 0.45, 1.40, 12.40, [
    ["기능", "Studio가 하는 일", "업무 시스템이 하는 일"],
    ["보상 (되돌리기)", "단계가 실패하면 성공한 단계를 **역순으로 자동 보상**. 사용자 「취소」도 같은 방식", "되돌리는 API 제공, 되돌려도 되는지 판단"],
    ["멱등성 키", "단계마다 Idempotency-Key를 만들어 보냄 (계획:대상:단계:a시도)", "같은 키 재요청을 걸러 처음 결과 반환"],
    ["권한", "역할·조건식으로 계획 때와 실행 직전에 판정", "업무 권한(담당 심사자인가) 확인"],
    ["사람 승인", "되돌릴 수 없는 액션은 실행 전 사람이 계획을 승인", "–"],
    ["실행 기록", "계획, 실행, 단계별 HTTP 결과, 보상 순서", "업무 이력(action_log)과 거절 사유"],
    ["업무 규칙", "없음", "평가 R01–R07, 상태 전이, 한도·중복 검사"],
    ["원자성·동시성", "없음 (시스템 간 사가 방식일 뿐)", "한 트랜잭션, 잠금, 입력 해시로 최신성 검사"],
], [2.0, 5.6, 4.8], row_h=0.56)
source(s, "근거: 앱 안의 액션 실행기 코드(kinetic/app/app/plans.py, dispatch.py), 시스템 등록 화면 안내문 「서비스는 Idempotency-Key 로 중복을 걸러야 합니다」")


# ── 6. 준비 ─────────────────────────────────────────────
s = slide_("4. 준비 — 업무 시스템 4개를 만들고 Studio에 등록",
           "명세의 네 시스템을 가상으로 만들었다. DB는 Studio와 분리하고, 업무 규칙은 서버에 두고, 테스트 109건으로 정확성을 확인했다",
           "단계 ④ 원천 연결 · ⑧ 실행")
table(s, 0.45, 1.42, 6.60, [
    ["시스템", "API", "인증", "하는 일"],
    ["계약", "6", "API 키", "계약·보장·역할 조회 (읽기 전용)"],
    ["접수", "11", "Basic", "접수, 서류 등록·연결·되돌리기"],
    ["심사", "24", "Bearer", "청구 등록, 서류 확인, 평가, 승인·부지급"],
    ["지급 (모의)", "3", "API 키", "모의 지급, 서명 콜백"],
], [1.4, 0.7, 1.3, 3.2], size=12, row_h=0.55)
pic(s, "01_시스템등록_목록.png", 7.25, 1.42, w=5.60)
caption(s, 7.25, 3.62, 5.60, "Studio 시스템 등록 — 보험 시스템 4개 연결 정상")
panel(s, 0.45, 4.45, 6.10, 2.45, [
    ("h", "업무 DB", {"size": 14}),
    ("b", "PostgreSQL 16, 스키마 4개·테이블 18개 (Studio 내장 DB와 분리)", {"size": 13}),
    ("b", "기본 데이터 B0, 초기화 스크립트, 테스트 109건 모두 통과", {"size": 13}),
    ("b", "계정 분리: 데이터소스는 읽기 전용, 서버만 쓰기", {"size": 13}),
], fill=SIDE)
panel(s, 6.75, 4.45, 6.10, 2.45, [
    ("h", "등록하며 확인한 것", {"size": 14}),
    ("b", "액션 실행기는 인증 비밀값을 자기 프로세스 환경변수에서 읽음 → 환경변수 등록 후 앱 재시작", {"size": 13}),
    ("b", "데이터소스 4개, 시스템 4개 모두 연결 테스트 통과", {"size": 13}),
], fill=SIDE)

# ── 7. 1차 구축 브리프 (실제값) ─────────────────────────
s = slide_("5. 1차 구축 — 구축 브리프 (실제 입력값)",
           "소스: 데이터소스 4개 + 시스템 4개, 대상: 새 스키마 「보험 청구 심사 온톨로지」. 아래는 실제로 넣은 문장이다",
           "단계 ① 범위 정의 · ③ 설계")
panel(s, 0.45, 1.35, 6.10, 2.25, [
    ("h", "구축 의도 (앞부분)", {"size": 13, "after": 3}),
    ("t", "보험금 청구 심사 담당자가 입원 정액보험(테스트 입원일당 A) 청구 한 건을 보며, 계약·보장·입원 사건·증빙·지급 내역을 시스템마다 따로 찾아 대조하지 않고 한 번에 확인하려고 쓴다.", {"size": 11}),
    ("t", "- 사람: 계약 시스템의 고객 번호와 접수 시스템의 청구인 번호가 다르다. identity_token이 같으면 같은 사람이다.", {"size": 11}),
    ("t", "- 계약자·피보험자·수익자는 같은 사람 개념을 쓰되, 계약상 역할(역할 종류와 유효 기간)로 구분한다. … 추출값은 확인값이 아니다.", {"size": 11}),
], fill=SIDE)
panel(s, 0.45, 3.75, 6.10, 3.15, [
    ("h", "골든 퀘스천 6개", {"size": 13, "after": 3}),
    ("t", "1. 가상 인물 B는 계약 시스템과 접수 시스템에서 각각 어떤 번호로 등록돼 있고, 계약 PO-001에서 어떤 역할을 맡고 있나요?", {"size": 11, "after": 2}),
    ("t", "2. 청구 CL-001에서 입원한 사람은 계약 PO-001의 피보험자가 맞나요? 청구를 접수한 사람(계약자)과 구분해서 알려 주세요.", {"size": 11, "after": 2}),
    ("t", "3. 청구 CL-001의 입원은 보장 CV-001의 보장 기간 안에 있고 대기 기간(30일)을 지났나요? 적용되는 심사 기준과 약관은 무엇인가요?", {"size": 11, "after": 2}),
    ("t", "4. 청구 CL-001에 필요한 서류는 무엇이고, 접수된 서류는 확인이 끝났나요? 서류의 확인값이 입원 사건 EV-001과 일치하나요?", {"size": 11, "after": 2}),
    ("t", "5. 보장 CV-001에서 피보험자의 지급 한도는 며칠이고, 이미 지급했거나 예약된 일수를 빼면 며칠이 남나요?", {"size": 11, "after": 2}),
    ("t", "6. 입원 사건 EV-001에 연결된 청구는 몇 건이고, 각 청구의 접수 상태, 심사 상태, 지급 상태는 무엇인가요?", {"size": 11, "after": 2}),
], fill=SIDE)
panel(s, 6.75, 1.35, 6.10, 5.55, [
    ("h", "골든 커맨드 10개", {"size": 13, "after": 3}),
    ("t", "1. 계약 TEST-POLICY-001의 보장 INPATIENT-DAILY-A로 새 청구를 접수해 줘. 접수 담당자 intake-01, 요청 키 REQ-GC-0001, 제출자 IP-0001, 입원자 IP-0002, …", {"size": 11, "after": 2}),
    ("t", "2. 청구 CL-001에 새로 받은 입퇴원확인서를 등록해 기존 서류 DC-001과 교체해 줘. 접수 담당자 intake-01, …", {"size": 11, "after": 2}),
    ("t", "3. 서류 DC-001을 담당 심사자 reviewer-01이 확인 완료로 처리해 줘. 확인값은 피보험자 IP-0002, 의료기관 H-001, …", {"size": 11, "after": 2}),
    ("t", "4. 청구 CL-001을 담당 심사자 reviewer-01로 평가해 줘.", {"size": 11, "after": 2}),
    ("t", "5. 청구 CL-001에 입퇴원확인서 보완을 요청해 줘. 담당 심사자 reviewer-01, …", {"size": 11, "after": 2}),
    ("t", "6. 청구 CL-001의 미해결 심사 업무를 담당 심사자 reviewer-01이 해결 처리해 줘. 해결 근거는 보완 서류 확인.", {"size": 11, "after": 2}),
    ("t", "7. 청구 CL-001을 현재 평가 기준으로 지급 승인해 줘. 담당 심사자 reviewer-01, 결정 사유는 지급 조건 충족.", {"size": 11, "after": 2}),
    ("t", "8. 청구 CL-001을 현재 평가 기준으로 부지급 결정해 줘. 담당 심사자 reviewer-01, 사유는 보장 조건 미충족.", {"size": 11, "after": 2}),
    ("t", "9. 청구 CL-001의 지급 지시를 지급 담당자 payment-01로 지급 요청해 줘.", {"size": 11, "after": 2}),
    ("t", "10. 결과 불명(UNKNOWN)인 지급 지시를 지급 담당자 payment-01로 모의 지급 내역과 대사해 줘.", {"size": 11, "after": 2}),
    ("t", "(… 는 같은 문장의 나머지 인자. 전문은 01_brief/구축_브리프_1차.md)", {"size": 10, "color": MUTED}),
], fill=SIDE)

# ── 8. 1차 구축 결과 ───────────────────────────────────
s = slide_("5. 1차 구축 결과 — 클래스 17, 관계 32, 액션 10",
           "에이전트가 설계·적재·액션 생성·검증을 하고, 골든 퀘스천 6개를 모두 통과했다. 사람은 맞다·틀리다로 검수한다",
           "단계 ③ 설계 · ⑤ 적재 · ⑥ 검증")
for i, (n, l) in enumerate([("17", "클래스"), ("32", "관계"), ("10", "액션"), ("6/6", "골든 퀘스천 통과")]):
    stat(s, 0.45 + i * 3.15, 1.38, 2.95, 1.20, n, l)
pic(s, "02_1차구축_검수와_골든커맨드.png", 0.45, 2.78, h=3.80)
caption(s, 0.45, 6.62, 6.08, "구축 보고 — 골든 퀘스천 답과 판정, 골든 커맨드 미리보기, 스키마 그래프")
panel(s, 6.75, 2.78, 6.10, 4.12, [
    ("h", "모델링에서 볼 점", {"size": 14}),
    ("b", "사람·계약 (7)", {"size": 12, "bold": True}),
    ("s", "Person · ContractCustomer · Claimant · Policy"),
    ("s", "**PolicyRole** · Coverage · RuleSetVersion"),
    ("b", "청구·서류 (5)", {"size": 12, "bold": True}),
    ("s", "ClaimReceipt · InsuranceClaim · InsuranceEvent"),
    ("s", "Document · DocumentVerification"),
    ("b", "업무 기록 (5)", {"size": 12, "bold": True}),
    ("s", "Assessment · ReviewTask · PaymentOrder"),
    ("s", "PaymentRequest · ActionLog"),
    ("b", "모든 클래스가 그래프에 복사하는 **적재 방식** — 액션 대상은 그래프 인스턴스여야 하기 때문 → 뒤의 재적재 문제로 이어짐", {"size": 12}),
], fill=SIDE)

s = slide_("5. 액션의 정의 — Palantir와 Studio",
           "Palantir 액션은 온톨로지를 바꾸는 단일 트랜잭션이고, Studio 액션은 외부 업무 시스템 API를 단계로 묶어 실패하면 역순으로 되돌린다",
           "단계 ⑧ 실행 (Action)")
table(s, 0.45, 1.40, 8.55, [
    ["비교", "Palantir 액션 타입", "Studio 액션"],
    ["정의", "하나 이상의 객체·속성·링크를 바꾸는 **단일 트랜잭션**", "등록 시스템 API를 **단계로 묶은** 실행"],
    ["바꾸는 곳", "온톨로지 자체 (편집 → 라이트백 데이터셋)", "외부 업무 시스템 (그래프는 status만 되씀)"],
    ["원자성", "편집은 전부 아니면 전무. 알림·웹훅은 예외", "없음. 실패하면 역순 **보상** (사가)"],
    ["외부 시스템 쓰기", "라이트백 웹훅 1개(편집 전) 또는 부수 효과 웹훅(편집 후)", "단계마다 API 호출, 단계 수 제한 없음"],
    ["실행 권한", "제출 조건 (submission criteria)", "정책(역할·조건식) + 사람 승인"],
], [1.7, 3.5, 3.35], size=12, row_h=0.80)
panel(s, 9.20, 1.30, 3.70, 5.65, [
    ("h", "Palantir 원문 (번역본)", {"size": 13}),
    ("t", "「액션은 사용자가 정의한 로직에 따라 하나 이상의 객체의 속성을 변경하는 단일 트랜잭션입니다.」", {"size": 12, "italic": True}),
    ("t", "「라이트백 웹훅이 실패하면 액션 적용이 중단되기 때문에, 라이트백으로 설정할 수 있는 웹훅은 하나뿐입니다.」", {"size": 12, "italic": True}),
    ("h", "그래서", {"size": 13}),
    ("b", "Palantir은 외부 시스템 여러 곳을 순서대로 바꾸고 되돌리는 흐름을 액션 하나로 만들지 않는다", {"size": 12}),
    ("b", "Studio는 그 흐름을 액션 하나로 만들지만, 원자성 대신 보상에 기댄다", {"size": 12}),
], fill=SIDE)
source(s, "출처: Palantir 문서 번역본 02_define-ontologies/03_action-types/ (01_overview, 21_consistency-guarantees, 12_side-effects/04_webhooks), Studio kinetic/app/app/plans.py")

s = slide_("5. 보상 — 성공한 단계를 반대 업무로, 역순으로 되돌린다",
           "보상은 지우기가 아니라 「접수 취소」, 「연결 해제」 같은 반대 업무 API 호출이다. 되돌리는 API가 없는 단계는 남는다",
           "단계 ⑧ 실행 (Action)")
textbox(s, 0.45, 1.40, 8.0, 0.35, [("t", "예: 서류 교체 액션 replaceClaimDocument에서 ③ 단계가 실패하면", {"size": 13, "bold": True})])
for i, (t, d, ok) in enumerate([("① registerDocument", "서류 등록 ✓", True), ("② attachDocument", "접수에 연결·교체 ✓", True), ("③ recordEvidenceAttached", "심사 시스템 반영 ✗ 실패", False)]):
    x = 0.45 + i * 2.95
    node(s, x, 1.85, 2.55, 1.00, t, d, line=BLUE if ok else "C00000", tsize=13, color=BLUE if ok else "C00000")
    if i < 2:
        arrow(s, x + 2.58, 2.15, 0.35, 0.38)
node(s, 3.40, 3.25, 2.55, 0.95, "↺ revertAttachment", "② 연결을 되돌림 (보상)", fill="FFF7E6", line="C55A11", dash=True, tsize=13, color="C55A11")
node(s, 0.45, 3.25, 2.55, 0.95, "보상 없음", "① 서류는 연결 없이 남음", fill="F2F2F2", line="BFBFBF", dash=True, tsize=13, color=MUTED)
textbox(s, 6.30, 3.30, 2.5, 0.9, [("t", "되돌리는 순서: ② → ①", {"size": 13, "bold": True, "color": "C55A11"}), ("t", "(실행의 역순)", {"size": 12, "color": MUTED})], anchor="m")
panel(s, 0.45, 4.45, 8.30, 2.45, [
    ("h", "보상(compensation)의 정의", {"size": 16, "after": 8}),
    ("b", "이미 성공한 단계의 효과를 **반대 업무로 되돌리는 별도의 API 호출**", {"size": 14, "after": 8}),
    ("b", "언제: 단계가 실패했을 때(자동), 사용자가 「취소해 줘」라고 할 때", {"size": 14, "after": 8}),
    ("b", "보상 호출에도 별도 멱등성 키(…:c)를 붙임", {"size": 14, "after": 8}),
    ("b", "보상 API가 없는 단계가 있으면 그 액션은 「부분 취소만 가능」", {"size": 14, "after": 8}),
])
panel(s, 9.20, 1.30, 3.70, 5.65, [
    ("h", "보상 API가 꼭 있어야 하는 이유", {"size": 13}),
    ("b", "Studio는 보상을 **언제** 부를지만 정한다. 되돌리는 API 자체는 업무 시스템에 있어야 한다", {"size": 12}),
    ("b", "구축 에이전트는 등록된 API 중 cancel·revert 같은 되돌리기 API를 골라 보상으로 짝짓는다", {"size": 12}),
    ("h", "되돌려도 되는가는 서버가", {"size": 13}),
    ("b", "청구가 있는 접수 취소 → RECEIPT_IN_USE", {"size": 12}),
    ("b", "종결된 청구의 연결 해제 → CLAIM_CLOSED", {"size": 12}),
    ("b", "거절되면 Studio에 「보상 실패」로 남고, 데이터는 어긋나지 않음", {"size": 12}),
], fill=SIDE)

s = slide_("5. 액션을 만들 때 명심할 점 — API 설계가 먼저다",
           "구축 에이전트는 등록된 API로만 액션을 만든다. 쓰기·되돌리기·조회 API와 그 응답 형식을 온톨로지 구축 전에 설계해 두어야 한다",
           "단계 ⑧ 실행 (Action)")
table(s, 0.45, 1.40, 12.40, [
    ["명심할 점", "이유", "이 PoC에서"],
    ["1. **API를 온톨로지보다 먼저 설계**", "에이전트는 등록 시스템의 OpenAPI에 있는 API로만 액션을 만들고, 없는 API는 지어내지 않음", "서버 설계서·API 44개 → 시스템 등록 → 1차 구축"],
    ["2. **쓰기 API마다 되돌리기 API를 짝지음**", "Studio는 보상 시점만 정함. 되돌리는 API는 업무 시스템 몫", "createReceipt ↔ cancelReceipt, attachDocument ↔ revertAttachment"],
    ["3. **되돌려도 되는지는 서버가 판단**", "보상이 늦게 오면 다음 업무가 이미 진행됐을 수 있음", "RECEIPT_IN_USE, CLAIM_CLOSED로 거절"],
    ["4. **중복 거르기는 서버가**", "Studio는 멱등성 키를 보내기만 하고, 재시도하면 키가 바뀜", "업무 키(request_key, 지급 키)로 거르기"],
    ["5. **원자성이 필요한 일은 API 하나 안에**", "Studio의 단계 묶음은 트랜잭션이 아님", "승인(지급 지시·한도 예약·상태·이력)은 서버 한 트랜잭션"],
    ["6. **대상은 그래프에 적재된 인스턴스**", "가상 클래스는 대상이 될 수 없고, 액션 뒤 재적재 필요", "17개 클래스 모두 적재 방식, 접수 뒤 재적재"],
    ["7. **실행자와 승인을 따로 챙김**", "데스크톱 사용자는 1명, 실행 역할은 정해진 목록", "actor_id로 서버가 권한 검사, 승인·부지급은 사람 승인"],
], [3.6, 4.9, 3.9], size=12, row_h=0.62)

# ── 14. 액션 10개 ───────────────────────────────────────
s = slide_("5. 1차 구축 결과 — 액션 10개의 구성",
           "명세 Action 11개 중 10개. 지급 결과 수신(A10)은 밖에서 오는 신호라 Studio로 만들 수 없다",
           "단계 ⑧ 실행 (Action)")
table(s, 0.45, 1.40, 12.40, [
    ["액션", "대상", "단계 (시스템 API)", "보상", "사람 승인"],
    ["청구 접수 submitClaimReceipt", "계약", "접수 createReceipt → 심사 registerClaim", "접수 취소", "대상 2건 이상"],
    ["서류 교체 replaceClaimDocument", "청구", "서류 등록 → 연결·교체 → 심사 반영", "연결 되돌리기", "대상 2건 이상"],
    ["서류 확인 verifyDocument", "서류", "심사 verifyEvidence", "–", "대상 2건 이상"],
    ["평가 evaluateClaim", "청구", "심사 evaluateClaim", "–", "대상 2건 이상"],
    ["보완 요청 requestEvidence", "청구", "심사 requestEvidence", "–", "대상 2건 이상"],
    ["업무 해결 resolveReviewTask", "심사 업무", "심사 resolveReviewTask", "–", "대상 2건 이상"],
    ["지급 승인 approveClaim", "청구", "현재 청구 조회 → 심사 approveClaim", "–", "**항상**"],
    ["부지급 rejectClaim", "청구", "현재 청구 조회 → 심사 rejectClaim", "–", "**항상**"],
    ["지급 요청 requestPayment", "지급 지시", "심사 requestPayment", "–", "**항상**"],
    ["대사 reconcilePayment", "지급 지시", "심사 reconcilePayment", "–", "대상 2건 이상"],
], [3.3, 1.3, 4.6, 1.7, 1.5], row_h=0.42)
source(s, "사람 승인 규칙(실행기 plans.py): 허용 대상 수 > confirm_threshold. 지급 승인·부지급·지급 요청은 0이라 항상, 나머지는 1이라 대상이 2건 이상일 때만. 승인·부지급은 먼저 청구를 다시 읽어 현재 평가로 결정")


# ── 14. 서류 업로드 순서와 이유 ─────────────────────────
s = slide_("6. 서류를 업무 DB까지 — 왜 구축 → 질의·액션 → 재적재 순서인가",
           "Studio는 화면마다 할 수 있는 일이 나뉘어 있다. 그래서 서류 한 건을 업무에 반영하려면 세 화면을 이 순서로 거친다",
           "단계 ⑤ 적재 · ⑧ 실행 · ⑨ 앱")
steps = [("① 구축", "서류 업로드", "서류 2개를 올려 그래프에 「미접수 서류」로 추가", "파일은 **구축 화면만** 받는다. 업로드는 인제스천 자료를 올리는 기능"),
         ("② 질의·액션", "청구 접수", "「업로드한 청구서대로 접수해 줘」 → 업무 DB에 접수·청구", "업무 DB를 바꾸는 **액션 실행**은 질의·액션에서만 된다"),
         ("③ 구축", "재적재", "업무 시스템 조회 API로 새 접수·청구를 그래프에 다시 적재", "그래프는 **복사본**이다. 액션은 DB만 바꾸고 그래프는 안 바꾼다"),
         ("④ 앱", "확인", "청구 심사 화면에서 새 청구 CL-002를 연다", "앱과 다음 액션은 **그래프**를 읽는다")]
for i, (scr, name, what, why) in enumerate(steps):
    x = 0.45 + i * 3.20
    box(s, x, 1.45, 2.75, 2.20, WHITE, line=BLUE, radius=0.06)
    textbox(s, x + 0.12, 1.53, 2.5, 2.05, [
        ("t", scr, {"size": 12, "bold": True, "color": MUTED, "after": 2}),
        ("t", name, {"size": 18, "bold": True, "color": BLUE, "after": 6}),
        ("t", what, {"size": 12}),
    ])
    box(s, x, 3.80, 2.75, 1.45, PANEL, radius=0.06)
    textbox(s, x + 0.12, 3.85, 2.5, 1.35, [("t", "이유", {"size": 11, "bold": True, "color": BLUE, "after": 2}), ("t", why, {"size": 12})])
    if i < 3:
        arrow(s, x + 2.80, 2.35)
panel(s, 0.45, 5.45, 12.40, 1.45, [
    ("h", "업로드는 인제스천 기능이다 (앱 코드로 확인)", {"size": 14, "after": 4}),
    ("b", "파일을 받는 모드는 구축뿐(allowsFiles: true). 질의·액션과 질문 응답은 파일을 받지 않는다", {"size": 12}),
    ("b", "올린 파일은 세션의 업로드 폴더에 저장되고 구축 에이전트에게 [업로드 문서]로 전달된다. 시스템 스펙·골든 퀘스천 txt·품질 CSV 업로드는 별도 용도", {"size": 12}),
], fill=SIDE)
s = slide_("6. Studio는 비정형 문서를 어떻게 처리하나",
           "파일은 구축 화면에서만 받는다. 무엇으로 만들지는 구축 에이전트가 파일마다 판단하고, 경로는 셋이다",
           "단계 ⑤ 추출·적재")
node(s, 0.45, 2.55, 1.90, 1.30, "업로드", "구축 화면\nPDF · DOCX\nXLSX · PPTX", fill=SIDE, line=LINE)
arrow(s, 2.42, 3.02, 0.40, 0.38)
node(s, 2.90, 2.55, 2.05, 1.30, "구축 에이전트", "파일을 열어 구조를 보고 경로 선택", fill=WHITE, line=BLUE)
paths = [("① 파서 스크립트", "에이전트가 파일마다 파서를 써서 실행\n(pdfplumber, 제목·문단, openpyxl)", "batch_ingest\n바로 적재", "이번 PoC"),
         ("② 문장 사실 추출", "extract_triples: 같은 조각을 LLM이 3번 추출\n스키마가 허용한 관계만, 원문 인용", "신뢰도 게이트\n자동 / 검수 / 보류", "OpenAI 필요"),
         ("③ 표 적재", "table_ingest: 열 → 속성, ID 열 → 관계\n원천 점검 규칙으로 잘못된 행 거름", "신뢰도 게이트\n자동 / 검수 / 보류", "")]
for i, (t, d, out, tag) in enumerate(paths):
    y = 1.45 + i * 1.20
    arrow(s, 5.02, y + 0.33, 0.40, 0.36)
    node(s, 5.50, y, 4.30, 1.02, t, d, fill=WHITE, line=BLUE, tsize=13)
    arrow(s, 9.87, y + 0.33, 0.40, 0.36)
    node(s, 10.35, y, 2.50, 1.02, out, tag or None, fill=PANEL, line=LINE, tsize=12)
panel(s, 0.45, 5.15, 6.10, 1.75, [
    ("h", "세 경로는 함께도, 따로도 쓰인다", {"size": 14}),
    ("b", "한 구축 안에서 파일마다 다른 경로를 쓸 수 있음. 경로는 에이전트가 고르고 화면 메뉴는 없음", {"size": 12}),
    ("b", "구축 의도에 「표는 표 적재로」처럼 지시 가능. 이번 PoC 청구서·확인서는 ① 경로", {"size": 12}),
], fill=SIDE)
panel(s, 6.75, 5.15, 6.10, 1.75, [
    ("h", "OpenAI 키를 넣으면", {"size": 14}),
    ("b", "② 문장 추출이 켜짐 (키가 없으면 「OPENAI_API_KEY 가 없어 LLM 추출을 할 수 없습니다」)", {"size": 12}),
    ("b", "**스캔·사진 PDF는 여전히 안 됨** — 세 경로 모두 PDF의 글자층을 읽고, OCR 코드는 v0.1.1에서 연결되지 않음", {"size": 12}),
], fill=SIDE)
source(s, "근거: 내장 지침 ingestion-patterns.md(「하나의 프로젝트에서 여러 패턴이 혼합될 수 있습니다」), 백엔드 quality/extraction.py(openai_llm), tabular.py(LLM 없음), document_indexing/(호출처 없음)")


# ── 16. ① 업로드 결과 ──────────────────────────────────
s = slide_("6. ① 구축 — 스키마 변경 없이 서류 노드 2개 추가",
           "대상을 「추가 인제스천」으로 고르면 기존 클래스만 쓴다. 이름만 적힌 청구서에서 값을 읽어 기존 서류(Document) 클래스에 넣었다",
           "단계 ⑤ 추출·적재")
pic(s, "03_업로드구축_적재보고.png", 0.45, 1.42, h=4.40)
caption(s, 0.45, 5.86, 7.04, "업로드 구축 보고 — 적재한 서류와 추출값, Cypher 검증 PASS")
panel(s, 7.70, 1.30, 5.15, 5.60, [
    ("h", "넣은 것", {"size": 13}),
    ("b", "문서 2개(청구서 docx, 확인서 pdf), 의도 한 줄, 골든 퀘스천 1개, 골든 커맨드 없음", {"size": 12}),
    ("h", "읽어 낸 값 (UP-S1-01 청구서)", {"size": 13}),
    ("b", "청구인 가상 인물 B, 계약 TEST-POLICY-001, H-002, 06-02 – 06-05, ACC-0101, 하루 100,000원", {"size": 12}),
    ("b", "피보험자 토큰 TKN-B는 이름으로 추정 → 신뢰도 0.85로 낮춤", {"size": 12}),
    ("h", "확인", {"size": 13}),
    ("b", "새 클래스·새 액션 없음, 가짜 접수·청구 노드 없음", {"size": 12}),
    ("b", "관계가 없는 것은 정상 — 서류는 접수에만 연결되는데 아직 접수가 없음", {"size": 12}),
], fill=SIDE)

# ── 17. ② 청구 접수 ────────────────────────────────────
s = slide_("6. ② 질의·액션 — 업로드한 청구서로 실제 청구 접수",
           "에이전트가 기존 접수 액션을 골라, 서류의 이름·문장을 온톨로지로 업무 번호로 바꿔 인자를 채웠다",
           "단계 ⑧ 실행 (Action)")
code(s, 0.45, 1.38, 12.40, 0.55, "업로드한 보험금 청구서 UP-S1-01의 내용대로 계약 PO-001에 청구를 접수해 줘. 요청 키 REQ-UP-S1-01, 접수 담당자 intake-01.")
pic(s, "06_질의액션_접수실행결과.png", 0.45, 2.10, w=6.10)
caption(s, 0.45, 5.94, 6.10, "실행 결과 — 접수 시스템 ✓ · 심사 시스템 ✓, 만들어진 레코드")
table(s, 6.75, 2.10, 6.10, [
    ["액션 인자", "값", "온톨로지에서 찾은 길"],
    ["보장 코드", "INPATIENT-DAILY-A", "PO-001의 보장, 1일 10만 원"],
    ["제출자·입원자", "IP-0002", "이름 → 토큰 TKN-B → 청구인"],
    ["사고·의료기관", "ACC-0101, H-002", "청구서"],
], [1.5, 1.9, 2.7], size=12, row_h=0.55)
panel(s, 6.75, 4.50, 6.10, 2.40, [
    ("h", "업무 DB에 생긴 것 (직접 조회)", {"size": 14}),
    ("b", "접수 **RC-0002** — 요청 키 REQ-UP-S1-01, 제출자·입원자 IP-0002", {"size": 13}),
    ("b", "청구 **CL-002** — 계약 PO-001, 보장 CV-001, 상태 RECEIVED", {"size": 13}),
    ("b", "입원 사건 **EV-002** — 확인 전(UNVERIFIED)", {"size": 13}),
], fill=SIDE)

# ── 18. ③ 재적재 → ④ 앱 ────────────────────────────────
s = slide_("6. ③ 재적재 → ④ 앱 — 새 청구 CL-002가 화면에",
           "구축 화면에서 업무 시스템 조회 API로 다시 적재하자, 청구 심사 화면에서 CL-002를 고를 수 있게 됐다",
           "단계 ⑤ 적재 · ⑨ 앱")
pic(s, "09_청구심사화면_CL-002.png", 0.45, 1.42, h=5.10)
caption(s, 0.45, 6.58, 6.12, "청구 심사 화면 — CL-002: 제출자·입원자 B, 계약 고객 C-10002, 피보험자·수익자 역할")
panel(s, 6.85, 1.30, 6.00, 2.70, [
    ("h", "재적재 (구축, 시스템 4개)", {"size": 14}),
    ("b", "의도: 조회 API로 접수·청구·사건 재적재, 있는 노드는 키로 갱신", {"size": 12}),
    ("b", "결과: 갱신 3건, 신규 3건(RC-0002, CL-002, EV-002), 중복 없음", {"size": 12}),
    ("b", "앱이 따라가는 관계 5개 생성 (관계 일괄 적재는 Studio 버그 → Cypher로 우회)", {"size": 12}),
], fill=SIDE)
panel(s, 6.85, 4.15, 6.00, 2.75, [
    ("h", "앱의 빨간 표시는 오류가 아니다", {"size": 14}),
    ("b", "「입원한 사람의 피보험자 여부」가 빨간색 — **입원일 기록 없음**", {"size": 12}),
    ("b", "입원 사건의 날짜는 서류 확인 뒤에 채워진다. 피보험자가 아니라는 뜻이 아님", {"size": 12}),
    ("b", "신고 날짜는 접수에 있으니, 확인 전에는 신고값으로 보여 주도록 앱을 고칠 수 있음", {"size": 12}),
], fill=SIDE)
# ── 21. 시나리오 2 ──────────────────────────────────────
s = slide_("6. 발표 시연 — 시나리오 2는 서류만 올린다",
           "액션이 모두 갖춰져 있으므로, 서류만 올리면 같은 흐름이 돈다. 이번에는 계약자가 자기 입원을 청구한다",
           "단계 ⑤ 적재 · ⑧ 실행")
table(s, 0.45, 1.42, 8.55, [
    ["항목", "시나리오 2"],
    ["서류", "가상 인물 A가 「제가 계약자로 가입한 보험」으로 본인 입원(7월 10일 – 14일, H-004)을 청구. 확인서 환자 A(TKN-A)"],
    ["구축", "서류 2개만 업로드 (시스템·골든 커맨드 없음)"],
    ["접수", "계약자는 청구할 수 있어 **접수는 통과**"],
    ["심사", "평가 R01 FAIL — **입원한 사람이 피보험자가 아님** → 부지급 후보 (서버 테스트 T11과 같은 판정)"],
], [1.4, 7.15], row_h=0.85)
panel(s, 9.20, 1.30, 3.70, 5.65, [
    ("h", "보여 주는 것", {"size": 13}),
    ("b", "서류에 쓴 말(「제가 가입한 보험」)과 계약상 역할(계약자 ≠ 피보험자)을 온톨로지가 구분", {"size": 13}),
    ("b", "같은 사람이 시스템마다 다른 번호(IP-0001 / C-10001)여도 하나로 이어 역할을 판정", {"size": 13}),
    ("b", "스키마 변경 없이 데이터만 더해 업무가 돔", {"size": 13}),
], fill=SIDE)

# ── 22. 구조적 한계 ─────────────────────────────────────
s = slide_("7. 한계 — Studio 설계에서 오는 것",
           "대부분은 업무 시스템이 대신 맡아 해결했다. 운영에 쓰려면 그래프 동기화가 가장 큰 숙제다",
           "단계 ⑩ 운영·진화")
table(s, 0.45, 1.40, 12.40, [
    ["한계", "영향", "대응"],
    ["액션은 업무 DB만 바꾸고, 그래프에는 status 하나만 되써 넣음", "새 청구·평가 같은 새 레코드는 **재적재해야** 그래프·앱에 보임", "액션 뒤 구축 화면에서 재적재"],
    ["액션 대상은 그래프에 적재된 인스턴스만", "1차 구축의 17개 클래스가 모두 적재 방식 → 재적재 부담", "위와 같음"],
    ["파일은 구축 화면에서만 받음", "서류를 바로 업무에 반영할 수 없음", "구축(적재) → 질의·액션(실행)"],
    ["원자성·동시성 제어 없음", "승인 같은 업무는 Studio만으로 안전하지 않음", "업무 시스템의 트랜잭션·잠금"],
    ["외부 콜백 수신 불가", "A10 지급 결과 수신을 액션으로 못 만듦", "지급 → 심사 시스템 직접 콜백"],
    ["사용자 1명(lite-user), 실행 역할은 정해진 목록", "접수·심사·지급 담당자를 역할로 나눌 수 없음", "서버가 actor_id로 권한 검사"],
    ["재시도 때 멱등성 키가 바뀜", "응답 유실 후 재시도는 새 요청으로 보임", "업무 키(요청 키·지급 키)로 중복 거르기"],
], [4.3, 4.6, 3.5], row_h=0.58)

s = slide_("7. Studio 개선 제안 — 이번 PoC에서 겪은 불편 8건",
           "가장 큰 것은 액션 뒤 재적재(동기화)와 질의 범위다. 엔티티 그래프와 시스템 선택 표시처럼 화면에서 바로 막히는 문제도 있었다",
           "단계 ⑩ 운영·진화")
table(s, 0.45, 1.40, 12.40, [
    ["번호", "겪은 상황", "원인 (확인한 범위)", "개선 제안"],
    ["1", "**액션 뒤 매번 재적재** — 접수해도 앱·그래프에 새 청구가 안 보임", "액션은 업무 DB만 바꾸고, 그래프에는 status 하나만 되써 넣음", "**「동기화」 버튼**으로 적재 클래스를 한 번에 재적재, 액션 뒤 자동 재조회"],
    ["2", "**재적재도 「구축」으로** — 스키마를 안 바꿔도 의도·골든 퀘스천 필수", "시작 버튼 조건: 의도 1개 + 골든 퀘스천 1개 이상", "의도 없이 도는 「데이터 추가·재적재」 모드"],
    ["3", "**엔티티 그래프가 안 나옴** — 「엔티티」를 눌러도 빈 화면, 안내 없음", "전체 엔티티 조회가 속성을 함수 인자로 펼쳐 100개 한도 초과", "클래스별로 나눠 조회해 그리기, 실패하면 원인 표시"],
    ["4", "**시스템을 골라도 반응 없음** — 데이터소스는 노란색 표시, 시스템은 그대로", "시스템 칩의 선택 스타일이 없음", "데이터소스와 같은 선택 표시"],
    ["5", "**대화 목록 표시가 실제와 다름** — 보험 구축 대화가 「공급망 운영 (예제)」로 보임", "기본 대화가 처음 대상 이름을 유지, 열기만 해도 시각 갱신", "구축 대상으로 표시 갱신, 열 때는 시각 유지"],
    ["6", "**품질 점검 실패** — 검수 대기·보류 건수를 알 수 없음", "백엔드 SQL의 GROUP BY 오류", "쿼리 수정"],
    ["7", "**용어가 화면마다 다름** — 가상 노드·가상 클래스, 인스턴스·엔티티·노드", "화면·튜토리얼마다 따로 쓴 용어 (부록 용어 비교)", "용어 통일, 적재 방식 클래스에 화면 이름 부여"],
    ["8", "**질의할 온톨로지를 고를 수 없음** — 보험과 공급망 예제를 한꺼번에 대상으로 함", "질의 요청에 대상 스키마가 없고, 스키마 조회 도구는 그래프 전체를 돌려줌", "질의·액션에도 대상 온톨로지 선택, 그 범위로 조회·액션 제한"],
], [0.7, 4.6, 3.8, 3.3], size=12, row_h=0.60)
source(s, "근거: 앱 화면 코드(시작 버튼 조건, 시스템 칩 스타일, 질의 요청 형식), 백엔드(ontology_graph_schema, 오류 메시지), sessions.db(읽기 전용), PoC 중 사용자 확인")

# ── 27. 부록: 산출물 ────────────────────────────────────
s = slide_("[Appendix] 산출물 위치",
           "모든 작업물은 04_insurance_ontology_poc/ 아래에 있다")
table(s, 0.45, 1.42, 12.40, [
    ["폴더", "내용"],
    ["00_spec/", "명세 원본, 쉬운 해설, Palantir 설계 가이드 해설"],
    ["01_brief/", "1차·2차 구축 브리프, 골든 퀘스천"],
    ["02_data/", "DB 스키마, B0, 테스트 변형, 업로드 서류(upload/시나리오1·2), 서류 생성 스크립트"],
    ["03_systems/", "업무 시스템 서버 4개, 서버 설계서, 시나리오 테스트"],
    ["04_ontology/", "Studio에서 내보낸 스키마(클래스 17·관계 32)와 액션 10개 정의"],
    ["05_tests/", "서버 테스트 결과 (109/109)"],
    ["06_app/", "청구 심사 화면(코드 앱) 소스"],
    ["notes/", "시스템 구성 보고서, Studio 기능 대조"],
], [2.4, 10.0], row_h=0.55)

# ── 28. 부록: 용어 ──────────────────────────────────────
s = slide_("[Appendix] 용어",
           "이 보고서에서 쓴 Studio·PoC 용어")
table(s, 0.45, 1.42, 12.40, [
    ["용어", "뜻"],
    ["추가 인제스천", "기존 온톨로지(스키마)에 데이터만 더하는 구축. 기존 클래스만 씀"],
    ["재적재", "업무 시스템의 현재 값을 그래프에 다시 복사하는 추가 인제스천"],
    ["적재 방식(materialized) 클래스", "인스턴스를 그래프에 복사해 둔 클래스. 액션의 대상이 될 수 있음"],
    ["골든 퀘스천 / 골든 커맨드", "온톨로지가 답해야 할 질문 / 할 수 있어야 할 지시. 구축 검증 기준"],
    ["계획 (plan)", "액션 실행 전 대상과 인자를 정한 것. 만들기만 해서는 아무것도 바뀌지 않음"],
    ["보상", "실패하거나 취소한 실행을 역순으로 되돌리는 호출"],
    ["멱등성 키", "같은 요청이 여러 번 와도 한 번만 처리하게 하는 키"],
    ["B0", "모든 테스트가 출발하는 기본 데이터 세트"],
], [3.4, 9.0], row_h=0.55)

# ── 부록: 정답 없이 「의심」을 판단하는 방법 ─────────────
s = slide_("[Appendix] 정답 없이 평가하는 지표 — RAGAS의 참조 불필요 지표",
           "기대 답(reference)이 없으면 「맞는가」는 잴 수 없다. 대신 「질문에 맞는가, 근거에 기대는가, 여러 번 해도 같은가」를 잰다")
table(s, 0.45, 1.40, 12.40, [
    ["지표", "입력", "계산", "재는 것"],
    ["Answer Relevancy\n(Response Relevancy)", "**질문, 답**", "답만 보고 질문을 N개(기본 3) 거꾸로 만들고, 원래 질문과의 임베딩 코사인 평균", "답이 질문 의도에 맞는가\n사실 여부는 보지 않음"],
    ["Aspect Critic", "**질문, 답** + 기준 정의", "LLM 판정을 여러 번 하고 다수결, 결과 0/1", "정한 기준(예: 간결한가, 해로운가)을 만족하는가"],
    ["Faithfulness", "질문, 답, 검색 근거", "답을 주장 단위로 나누고, 근거로 뒷받침되는 주장의 비율", "답이 근거에 기대는가 (지어내지 않았나)"],
    ["Response Groundedness", "답, 검색 근거", "서로 다른 판정 템플릿 2개로 0/1/2 → 0–1로 바꿔 평균", "위와 같음 (NVIDIA 지표)"],
    ["Context Relevance", "질문, 검색 근거", "독립 판정 2회로 0/1/2 → 평균", "가져온 근거가 질문과 관련 있는가"],
    ["Context Utilization", "질문, 답, 검색 근거", "근거 조각마다 답에 쓰였는지 LLM 판정, 순위 가중 정밀도", "쓸모 있는 근거를 앞에 가져왔는가"],
], [2.6, 2.3, 4.5, 3.0], size=12, row_h=0.62)
panel(s, 0.45, 5.95, 12.40, 0.95, [
    ("b", "질문과 답만으로 되는 것은 **Answer Relevancy**와 **Aspect Critic**뿐이다. 나머지는 검색 근거가 더 필요하다", {"size": 13}),
    ("b", "Factual Correctness, Answer Accuracy, Context Recall처럼 **정답이 맞는지** 재는 지표는 기대 답(reference)이 있어야 한다", {"size": 13}),
], fill=SIDE)
source(s, "출처: RAGAS 공식 문서 docs.ragas.io (stable, available metrics — answer relevance, faithfulness, context precision, general purpose, nvidia metrics), 2026-11-04 확인")

s = slide_("[Appendix] Studio의 골든 퀘스천 판정 — 실행 결과에 근거한 자기 보고",
           "골든 퀘스천에는 점수 공식이 없다. 에이전트가 실제로 실행해 행이 나왔는지 보고, 상태·신뢰도를 스스로 적는다. 맞는지는 사람이 판정한다")
flow = [("1", "실제로 실행", "질문마다 답하는 길(그래프 질의, 데이터소스 SQL, 둘 다)을 정하고 실행"),
        ("2", "행 수로 판정", "결과 행이 0이면 FAIL → 스키마·데이터를 고쳐 최대 3회 반복"),
        ("3", "자기 보고", "최종 보고서에 상태, 신뢰도, 결과 행 수를 에이전트가 직접 적음"),
        ("4", "백엔드 정리", "계산 없음. 값이 빠지면 「답변 가능·보통」, 보고가 없으면 「아직 어려움·낮음」"),
        ("5", "사람 검수", "배지를 보고 맞다·틀리다. 틀리다와 피드백은 다음 구축에 전달")]
for i, (n, h, d) in enumerate(flow):
    x = 0.45 + i * 2.50
    box(s, x, 1.45, 2.30, 2.55, WHITE, line=BLUE, radius=0.06)
    textbox(s, x + 0.10, 1.55, 2.10, 2.35, [("t", n, {"size": 20, "bold": True, "color": LINE, "after": 0}),
                                            ("t", h, {"size": 15, "bold": True, "color": BLUE, "after": 6}),
                                            ("t", d, {"size": 12})])
table(s, 0.45, 4.25, 7.40, [
    ["보고 항목", "값", "화면 배지"],
    ["status", "answerable\npartially_answerable\nnot_yet_answerable", "답변 가능\n부분적으로 답변 가능\n아직 답변 어려움"],
    ["confidence", "high / medium / low", "신뢰도 높음 / 보통 / 낮음"],
    ["evidence_row_count", "실행 결과 행 수", "(보고서 본문에 표시)"],
], [1.8, 3.0, 2.6], size=12, row_h=0.55)
panel(s, 8.05, 4.25, 4.80, 2.65, [
    ("h", "그래서 「의심」의 근거는", {"size": 14}),
    ("b", "실행해서 답할 데이터가 나왔는가 (행 수)", {"size": 13}),
    ("b", "에이전트가 스스로 매긴 상태·신뢰도", {"size": 13}),
    ("b", "기대 답과의 대조는 없음 — **사람의 맞다·틀리다**가 정답 판정", {"size": 13}),
], fill=SIDE)
source(s, "근거: 앱 내장 지침 skills/ontology-build/references/validation.md, 백엔드 agent_session/service.py 708–709·805–806행, REA 분석 menus/01-ontology-build/code-trace.md 3절")

s = slide_("[Appendix] 추출 사실의 「의심」 판정 — 신뢰도 게이트 S_c",
           "문서에서 뽑은 사실은 바로 쓰지 않고, 정답 없이 계산하는 복합 신뢰도로 자동 적재·검수 대기·보류로 나눈다")
box(s, 0.45, 1.40, 12.40, 0.70, fill="F2F2F2", radius=0.03)
textbox(s, 0.60, 1.40, 12.10, 0.70, [("t", "S_c  =  G_onto  ×  m_vocab  ×  ( 0.3 · S_llm  +  0.5 · S_ground  +  0.2 · S_graph )", {"size": 20, "bold": True, "color": BLUE, "align": PP_ALIGN.CENTER})], anchor="m")
table(s, 0.45, 2.30, 7.60, [
    ["신호", "계산", "RAGAS에서 비슷한 것"],
    ["S_llm 생성 신뢰도", "α·S_logprob + (1−α)·S_freq\nS_freq = 같은 청크를 **3번 추출**해 같은 사실이 나온 비율 (logprob은 기본 꺼짐)", "Aspect Critic의 다수결 (자기일관성)"],
    ["S_ground 원문 근거", "e^(−0.02·d) × (½·어휘 근거 + ½·정규화 코사인)\nd = 주어·목적어 사이 단어 수", "Faithfulness,\nResponse Groundedness"],
    ["S_graph 그래프 지지", "기존 그래프 2–3홉 지지 경로 1−e^(−Σ). 없으면 0.5, 같은 관계가 이미 있으면 1", "해당 없음"],
    ["G_onto 스키마 게이트", "없는 클래스·관계, 정의역·치역 위반이면 0", "해당 없음"],
], [1.8, 3.6, 2.2], size=12, row_h=0.80)
table(s, 8.25, 2.30, 4.60, [
    ["결과", "조건"],
    ["자동 적재", "S_c ≥ 0.85, 경고 없음"],
    ["검수 대기", "0.60 ≤ S_c < 0.85 또는 경고 있음"],
    ["보류함", "S_c < 0.60 또는 스키마 위반"],
], [1.4, 3.2], size=12, row_h=0.55)
panel(s, 8.25, 4.65, 4.60, 2.25, [
    ("h", "항상 사람이 보는 것", {"size": 13}),
    ("b", "스키마 제안, 빠진 값 보정, 링크 예측, 동일 개체 제안 — 근거가 원문이 아니라 추론", {"size": 12}),
    ("b", "이번 PoC 업로드는 에이전트가 파서로 적재하고 신뢰도를 직접 매김. 이 게이트의 LLM 추출은 OpenAI 키가 필요", {"size": 12}),
], fill=SIDE)
source(s, "근거: 백엔드 quality/confidence.py(공식), policy.py(가중치 0.3·0.5·0.2, 임계 0.85·0.60, 샘플 3), pipeline.py, extraction.py")

# ── 부록: Palantir와 Studio 용어 비교 ──────────────────
s = slide_("[Appendix] Palantir와 Studio의 온톨로지 용어 ① 구조",
           "같은 개념은 대부분 이름만 다르다. Studio는 같은 것을 화면마다 다르게 부르고, materialization은 두 제품에서 뜻이 다르다")
table(s, 0.45, 1.40, 12.40, [
    ["개념", "Palantir Foundry", "Studio 화면·튜토리얼", "Studio 내부 이름"],
    ["대상의 형", "객체 타입 (object type)", "클래스", "_OntologyClass"],
    ["대상 하나", "객체 (object)", "인스턴스 · 엔티티 · 노드 (섞어 씀)", "_Entity"],
    ["특성", "속성 (property) + 공유 속성·값 타입·구조체", "속성", "properties"],
    ["관계의 형", "링크 타입 (link type), N:N은 조인 테이블", "관계, 관계 타입", "_OntologyRelationship"],
    ["원천 데이터", "백킹 데이터소스 (데이터셋·가상 테이블)", "데이터소스 (DB 스키마 하나)", "datasource"],
    ["원천을 복사 없이 읽는 형", "별도 개념 없음 (객체는 객체 DB에 인덱싱)", "**가상 노드 · 가상 관계 · 가상 클래스**", "binding_kind = virtual"],
    ["그래프에 복사해 둔 형", "객체 DB에 인덱싱된 객체 (기본)", "화면 이름 없음 (튜토리얼 「저장 그래프」)", "binding_kind = materialized"],
    ["materialization", "원본 + 사용자 편집을 합친 **데이터셋**", "(그래프에 복사한 클래스)", "materialized — **뜻이 다름**"],
    ["공통 형태", "인터페이스 (interface)", "없음", "–"],
], [2.4, 3.9, 3.6, 2.5], size=12, row_h=0.50)
source(s, "빈도 (앱 화면 코드 / 튜토리얼): 가상 노드 12 / 52, 가상 관계 0 / 15, 가상 클래스 5 / 0, 엔티티 20 / 10, 인스턴스 10 / 26. 출처: Palantir 문서 번역본(02_research/palantir), Studio v0.1.1")


# ── 발표문(슬라이드 노트) ───────────────────────────────
import os
import importlib.util


def _title(slide):
    for sh in slide.shapes:
        if sh.has_text_frame and sh.text_frame.text.strip():
            return sh.text_frame.text.strip()
    return ""


# 기존 덱의 사용자 메모([스크립트] 앞부분)를 제목으로 보존한다
_memos = {}
if os.path.exists(OUT):
    try:
        old = Presentation(OUT)
        for sl in old.slides:
            if sl.has_notes_slide:
                txt = sl.notes_slide.notes_text_frame.text
                memo = txt.split("[스크립트]")[0].strip()
                if memo:
                    _memos[_title(sl)] = memo
    except Exception as exc:  # 덱을 못 읽어도 빌드는 계속
        print("memo read failed:", exc)

_spec = importlib.util.spec_from_file_location("notes_script", os.path.join(os.path.dirname(os.path.abspath(__file__)), "notes_script.py"))
_ns = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_ns)
_keys = sorted(_ns.NOTES, key=len, reverse=True)
_unmatched = []
for sl in prs.slides:
    t = _title(sl)
    key = next((k for k in _keys if t.startswith(k)), None)
    script = _ns.NOTES[key].strip() if key else ""
    if not key:
        _unmatched.append(t)
    body = "[스크립트]\n" + script if script else ""
    memo = _memos.pop(t, "")
    sl.notes_slide.notes_text_frame.text = (memo + "\n\n" + body).strip() if memo else body
if _unmatched:
    print("NO SCRIPT:", _unmatched)
if _memos:
    print("UNMATCHED MEMOS:", list(_memos))

prs.save(OUT)
print("slides", len(prs.slides))
