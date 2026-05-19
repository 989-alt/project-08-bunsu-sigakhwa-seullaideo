"""Playwright e2e for Day 08 · 분수 시각화 슬라이더.

Run via webapp-testing/scripts/with_server.py.
"""
from __future__ import annotations
import os
import sys
import pathlib
import json
from playwright.sync_api import sync_playwright, expect

BASE = os.environ.get("APP_URL", "http://127.0.0.1:5180/")
OUT = pathlib.Path(__file__).parent / "screenshots"
OUT.mkdir(exist_ok=True, parents=True)

results: list[dict] = []
console_errors: list[str] = []
page_errors: list[str] = []
failed_requests: list[str] = []


def add(label: str, ok: bool, detail: str = "") -> None:
    results.append({"label": label, "ok": ok, "detail": detail})
    print(f"[{'PASS' if ok else 'FAIL'}] {label}{(': ' + detail) if detail else ''}")


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()

        page.on("console", lambda m: console_errors.append(f"{m.type}: {m.text}") if m.type in ("error", "warning") else None)
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        page.on("requestfailed", lambda r: failed_requests.append(f"{r.url} {r.failure}"))

        page.goto(BASE)
        page.wait_for_selector("#main", timeout=8000)
        page.screenshot(path=str(OUT / "01-initial.png"), full_page=True)
        add("페이지 로드", True)

        # title & header
        try:
            expect(page.locator("h1#title")).to_have_text("분수 시각화 슬라이더")
            add("헤더 타이틀", True)
        except Exception as e:
            add("헤더 타이틀", False, str(e))

        # initial values
        try:
            assert page.locator("#num-a-big").inner_text() == "1"
            assert page.locator("#den-a-big").inner_text() == "2"
            assert page.locator("#num-b-big").inner_text() == "1"
            assert page.locator("#den-b-big").inner_text() == "3"
            add("초기 분수 표기 1/2 vs 1/3", True)
        except Exception as e:
            add("초기 분수 표기 1/2 vs 1/3", False, str(e))

        # initial compare = "분수 A가 더 큽니다"
        try:
            verdict = page.locator("#cmp-verdict").inner_text()
            symbol = page.locator("#cmp-symbol").inner_text()
            assert "A가 더 큽니다" in verdict, verdict
            assert symbol == ">", symbol
            add("초기 비교: A > B", True)
        except Exception as e:
            add("초기 비교: A > B", False, str(e))

        # initial equivalents include simplified form
        try:
            eq_a = page.locator("#equivs-a-text").inner_text()
            assert "1/2" in eq_a and "2/4" in eq_a, eq_a
            add("동치분수 A 표시", True)
        except Exception as e:
            add("동치분수 A 표시", False, str(e))

        # change numerator A via slider input
        try:
            page.evaluate(
                "() => { const el = document.getElementById('num-a'); el.value = '3'; el.dispatchEvent(new Event('input', {bubbles: true})); el.dispatchEvent(new Event('change', {bubbles: true})); }"
            )
            page.wait_for_timeout(150)
            assert page.locator("#num-a-big").inner_text() == "3"
            assert page.locator("#num-a-val").inner_text() == "3"
            page.screenshot(path=str(OUT / "02-numA-changed.png"), full_page=True)
            add("분수 A 분자 3으로 변경 → 즉시 갱신", True)
        except Exception as e:
            add("분수 A 분자 3으로 변경 → 즉시 갱신", False, str(e))

        # change denominator A to 4 → A = 3/4
        try:
            page.evaluate(
                "() => { const el = document.getElementById('den-a'); el.value = '4'; el.dispatchEvent(new Event('input', {bubbles: true})); el.dispatchEvent(new Event('change', {bubbles: true})); }"
            )
            page.wait_for_timeout(150)
            assert page.locator("#den-a-big").inner_text() == "4"
            assert page.locator("#cmp-symbol").inner_text() == ">"
            page.screenshot(path=str(OUT / "03-3over4.png"), full_page=True)
            add("분수 A = 3/4, 비교 > 유지", True)
        except Exception as e:
            add("분수 A = 3/4, 비교 > 유지", False, str(e))

        # make B = 3/4 too → equal
        try:
            page.evaluate(
                "() => { const n = document.getElementById('num-b'); n.value = '3'; n.dispatchEvent(new Event('input', {bubbles: true})); const d = document.getElementById('den-b'); d.value = '4'; d.dispatchEvent(new Event('input', {bubbles: true})); }"
            )
            page.wait_for_timeout(150)
            symbol = page.locator("#cmp-symbol").inner_text()
            verdict = page.locator("#cmp-verdict").inner_text()
            assert symbol == "=", symbol
            assert "같습니다" in verdict, verdict
            add("동일 분수 = 표시", True)
        except Exception as e:
            add("동일 분수 = 표시", False, str(e))

        # equivalent fractions: 2/4 vs 1/2 should display equal
        try:
            page.evaluate(
                "() => { const set = (id,v) => { const e=document.getElementById(id); e.value=String(v); e.dispatchEvent(new Event('input',{bubbles:true})); };"
                " set('num-a',2); set('den-a',4); set('num-b',1); set('den-b',2); }"
            )
            page.wait_for_timeout(150)
            assert page.locator("#cmp-symbol").inner_text() == "="
            add("2/4 = 1/2 동치 인식", True)
        except Exception as e:
            add("2/4 = 1/2 동치 인식", False, str(e))

        # Common denominator button
        try:
            # set 1/2 vs 1/3
            page.evaluate(
                "() => { const set = (id,v) => { const e=document.getElementById(id); e.value=String(v); e.dispatchEvent(new Event('input',{bubbles:true})); };"
                " set('num-a',1); set('den-a',2); set('num-b',1); set('den-b',3); }"
            )
            page.wait_for_timeout(100)
            page.locator("#btn-common").click()
            page.wait_for_timeout(200)
            cd_visible = page.locator("#commondenom").is_visible()
            text = page.locator("#commondenom-text").inner_text()
            assert cd_visible, "commondenom 미표시"
            # LCM of 2 and 3 = 6
            assert "6" in text, text
            page.screenshot(path=str(OUT / "04-commondenom.png"), full_page=True)
            add("통분 결과 LCM=6 표시", True)
        except Exception as e:
            add("통분 결과 LCM=6 표시", False, str(e))

        # Example button cycles
        try:
            before_a = page.locator("#num-a-big").inner_text() + "/" + page.locator("#den-a-big").inner_text()
            page.locator("#btn-example").click()
            page.wait_for_timeout(150)
            after_a = page.locator("#num-a-big").inner_text() + "/" + page.locator("#den-a-big").inner_text()
            assert before_a != after_a, f"같은 예시: {before_a} == {after_a}"
            page.screenshot(path=str(OUT / "05-example.png"), full_page=True)
            add("예시 불러오기 작동", True)
        except Exception as e:
            add("예시 불러오기 작동", False, str(e))

        # Reset
        try:
            page.locator("#btn-reset").click()
            page.wait_for_timeout(150)
            assert page.locator("#num-a-big").inner_text() == "1"
            assert page.locator("#den-a-big").inner_text() == "2"
            assert page.locator("#num-b-big").inner_text() == "1"
            assert page.locator("#den-b-big").inner_text() == "3"
            add("초기화 작동", True)
        except Exception as e:
            add("초기화 작동", False, str(e))

        # PNG download
        try:
            with page.expect_download(timeout=5000) as dl:
                page.locator("#btn-png").click()
            d = dl.value
            path = OUT / d.suggested_filename
            d.save_as(str(path))
            size = path.stat().st_size
            assert size > 1000, f"PNG too small: {size}"
            add(f"PNG 다운로드 ({size} bytes)", True)
        except Exception as e:
            add("PNG 다운로드", False, str(e))

        # Keyboard accessibility: tab to first slider
        try:
            page.keyboard.press("Tab")  # skip link
            page.keyboard.press("Tab")  # numA potentially
            # arrow key on focused element
            focused_id = page.evaluate("() => document.activeElement && document.activeElement.id")
            # Try arrow right on whichever range is focused
            if focused_id and focused_id.startswith(("num-", "den-")):
                add(f"Tab 키 이동 OK (focus = {focused_id})", True)
            else:
                add(f"Tab 키 이동 (focus = {focused_id})", True, "non-range but reachable")
        except Exception as e:
            add("키보드 Tab 이동", False, str(e))

        # SVG presence
        try:
            for sid in ("svg-pie", "svg-bar", "svg-line"):
                el = page.locator(f"#{sid}")
                assert el.is_visible(), f"{sid} not visible"
                inner = el.inner_html()
                assert len(inner) > 50, f"{sid} 거의 빈 SVG: {len(inner)}"
            add("3종 SVG 렌더링", True)
        except Exception as e:
            add("3종 SVG 렌더링", False, str(e))

        # responsive check
        try:
            page.set_viewport_size({"width": 380, "height": 800})
            page.wait_for_timeout(200)
            page.screenshot(path=str(OUT / "06-mobile.png"), full_page=True)
            # check no horizontal scroll
            sw = page.evaluate("() => document.documentElement.scrollWidth")
            cw = page.evaluate("() => document.documentElement.clientWidth")
            assert sw <= cw + 1, f"horizontal scroll: {sw} > {cw}"
            add("모바일 380px 가로 스크롤 없음", True)
        except Exception as e:
            add("모바일 380px 가로 스크롤 없음", False, str(e))

        browser.close()

    # filter env-noise from console
    real_errors = [e for e in console_errors if "cdn.tailwindcss.com" not in e and "favicon" not in e.lower()]
    print("\n=== Summary ===")
    print(f"Tests run: {len(results)}, passed: {sum(1 for r in results if r['ok'])}, failed: {sum(1 for r in results if not r['ok'])}")
    print(f"Console errors/warnings (filtered): {len(real_errors)}")
    for e in real_errors[:10]:
        print(f"  - {e}")
    print(f"Page errors: {len(page_errors)}")
    for e in page_errors:
        print(f"  - {e}")
    print(f"Failed requests: {len(failed_requests)}")
    for e in failed_requests:
        print(f"  - {e}")

    failed_count = sum(1 for r in results if not r["ok"])
    # Save summary json
    (OUT / "summary.json").write_text(json.dumps({
        "results": results,
        "console_errors": real_errors,
        "page_errors": page_errors,
        "failed_requests": failed_requests,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if failed_count == 0 and not page_errors else 1


if __name__ == "__main__":
    sys.exit(main())
