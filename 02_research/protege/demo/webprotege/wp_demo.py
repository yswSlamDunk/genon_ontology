"""WebProtégé 로컬 시연: 로그인 → 홈 → 프로젝트 생성(pizza.owl 업로드) → 편집 화면 캡쳐."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

CHROME = str(next(Path.home().glob(
    "Library/Caches/ms-playwright/chromium-*/chrome-mac-arm64/"
    "Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing")))
BASE = "http://localhost:5050"
step = sys.argv[1]
out = Path(sys.argv[2])
creds = dict(l.split("=", 1) for l in Path(sys.argv[3]).read_text().split())
owl = sys.argv[4] if len(sys.argv) > 4 else None


def shot(page, name):
    page.wait_for_timeout(2500)
    page.screenshot(path=str(out / name))
    print("saved", name)


def dump(page):
    for el in page.query_selector_all("input, button, a, textarea"):
        t = (el.inner_text() or el.get_attribute("placeholder") or el.get_attribute("type") or "").strip()
        if el.is_visible():
            print(" -", el.evaluate("e => e.tagName"), repr(t[:40]))


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME, headless=True)
    page = b.new_page(viewport={"width": 1440, "height": 900}, locale="en-US")
    page.goto(BASE + "/")
    page.wait_for_timeout(4000)
    if step == "explore":
        dump(page)
        shot(page, "web-01-login.png")
    else:
        inputs = page.locator("input:visible")
        inputs.nth(0).fill(creds["username"])
        page.locator("input[type=password]:visible").fill(creds["password"])
        page.get_by_role("button", name="Sign In").click()
        page.wait_for_timeout(5000)
        if step == "settings":
            page.goto(BASE + "/#application/settings")
            page.wait_for_timeout(4000)
            txt = page.locator("input[type=text]:visible")
            txt.nth(1).fill("admin@example.com")
            page.locator("select:visible").first.select_option(label="http")
            txt.nth(2).fill("localhost")
            txt.nth(4).fill("5050")
            for label in ["Account creation enabled", "Project creation enabled", "Project upload enabled"]:
                page.get_by_label(label).check()
            txt.nth(5).fill("50")
            page.get_by_label("Email notifications enabled").uncheck()
            print("buttons:", [b.inner_text() for b in page.query_selector_all("button") if b.is_visible()])
            page.screenshot(path=str(out / "web-02b-settings.png"), full_page=True)
            page.get_by_role("button", name="Apply").click()
            page.wait_for_timeout(3000)
            page.goto(BASE + "/")
            shot(page, "web-02c-home-configured.png")
        if step == "home":
            dump(page)
            shot(page, "web-02-home.png")
        elif step == "create":
            page.get_by_text("Create New Project").first.click()
            page.wait_for_timeout(2000)
            dump(page)
            shot(page, "web-03-create-dialog.png")
            dialog_inputs = page.locator("input[type=text]:visible")
            dialog_inputs.nth(0).fill("Pizza Demo")
            page.locator("textarea:visible").first.fill("Protégé pizza 샘플 온톨로지 업로드 시연")
            page.locator("input[type=file]").set_input_files(owl)
            shot(page, "web-03-create-dialog.png")
            page.get_by_role("button", name="Create New Project").last.click()
            page.wait_for_timeout(8000)
            shot(page, "web-04-after-create.png")
            dump(page)
        if step == "open":
            page.get_by_text("Pizza Demo").first.click()
            page.wait_for_timeout(12000)
            print("tabs/links:", [t.strip() for t in page.locator("a:visible, button:visible").all_inner_texts() if t.strip()][:40])
            shot(page, "web-05-project-classes.png")
            def row(name):
                return page.locator(".gt-tree__row").filter(
                    has=page.get_by_text(name, exact=True)).first
            for name in ["DomainConcept", "Food", "Pizza", "NamedPizza"]:
                row(name).click(); page.wait_for_timeout(800)
                page.keyboard.press("ArrowRight"); page.wait_for_timeout(1500)
            row("Margherita").click()
            shot(page, "web-06-class-margherita.png")
            for tab, fname in [("Properties", "web-07-properties.png"),
                               ("Individuals", "web-08-individuals.png"),
                               ("History", "web-09-history.png")]:
                page.locator("a:visible, div:visible").filter(has_text=tab).locator("text=" + tab).first.click()
                page.wait_for_timeout(3000)
                shot(page, fname)
    b.close()
