"""Drive the local demo in Chromium; save only fictional, authenticated screens."""

import json
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
credentials = json.loads((ROOT / ".local-data/credentials.json").read_text())
with socket.socket() as listener:
    listener.bind(("127.0.0.1", 0))
    port = listener.getsockname()[1]
base = f"http://127.0.0.1:{port}"
server = subprocess.Popen(
    [sys.executable, "manage.py", "runserver", f"127.0.0.1:{port}", "--noreload"],
    cwd=ROOT,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
try:
    for _ in range(100):
        try:
            urllib.request.urlopen(base + "/login/", timeout=1).close()
            break
        except (urllib.error.URLError, ConnectionError):
            if server.poll() is not None:
                raise RuntimeError("Demo server exited before startup") from None
            time.sleep(0.1)
    else:
        raise RuntimeError("Demo server did not become ready")
    with sync_playwright() as driver:
        browser = driver.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000}, device_scale_factor=1)

        def login(name):
            page.goto(base + "/login/")
            page.get_by_label("Username").fill(name)
            page.get_by_label("Password").fill(credentials[name])
            page.get_by_role("button", name="Sign in", exact=True).click()
            page.wait_for_url(base + "/")

        login("employee.alex")
        if page.get_by_role("link", name="Open document", exact=True).count() != 3:
            raise AssertionError("Expected three assigned documents")
        shots = ROOT / "docs/images"
        shots.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(shots / "documents.png"), full_page=True)
        page.get_by_role("link", name="Open document", exact=True).first.click()
        if "FICTIONAL TRAINING RECORD" not in page.locator("pre").inner_text():
            raise AssertionError("Document body missing")
        with page.expect_download() as info:
            page.get_by_role("link", name="Download text file").click()
        downloaded = Path(info.value.path()).read_text()
        if "FICTIONAL TRAINING RECORD" not in downloaded:
            raise AssertionError("Download did not contain fictional document")
        response = page.goto(base + "/documents/4/download/")
        if response.status != 404:
            raise AssertionError("Direct download bypassed authorization")
        page.screenshot(path=str(shots / "access-denied.png"), full_page=True)
        page.get_by_role("button", name="Sign out").click()
        login("reviewer")
        if page.get_by_role("link", name="Open document", exact=True).count():
            raise AssertionError("Reviewer unexpectedly received document access")
        page.get_by_role("link", name="Audit trail", exact=True).click()
        if "document.download" not in page.locator("table").inner_text():
            raise AssertionError("Audit event missing")
        page.screenshot(path=str(shots / "audit.png"), full_page=True)
        for width in (390, 320):
            page.set_viewport_size({"width": width, "height": 844})
            if page.evaluate("document.documentElement.scrollWidth > window.innerWidth"):
                raise AssertionError("Mobile reviewer view overflows viewport")
        page.get_by_role("button", name="Sign out").click()
        login("employee.alex")
        page.set_viewport_size({"width": 390, "height": 844})
        if page.evaluate("document.documentElement.scrollWidth > window.innerWidth"):
            raise AssertionError("Mobile document list overflows viewport")
        page.screenshot(path=str(shots / "mobile.png"), full_page=True)
        browser.close()
    print(
        "Browser checks passed: login, list, view, download, denial, reviewer isolation, audit, logout, mobile."
    )
finally:
    server.terminate()
    server.wait(timeout=10)
