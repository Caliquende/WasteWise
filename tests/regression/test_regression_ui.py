import os
import time
from pathlib import Path

from playwright.sync_api import sync_playwright


def test_results_view_shows_empty_state_before_first_scan(api_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(api_server, wait_until="networkidle")
        page.click("#nav-results")

        assert page.locator("#results-empty").is_visible()
        assert not page.locator("#results-container").is_visible()
        browser.close()


def test_forgotten_project_row_identifies_project_and_targets_parent_directory(api_server, tmp_path):
    project_dir = tmp_path / "oldproj"
    git_dir = project_dir / ".git"
    git_dir.mkdir(parents=True)
    (git_dir / "HEAD").write_text("ref: refs/heads/main", encoding="utf-8")

    old_time = time.time() - 200 * 24 * 60 * 60
    os.utime(git_dir, (old_time, old_time))

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(api_server, wait_until="networkidle")
        page.click("#btn-start-scan")
        page.fill("#scan-path", str(tmp_path))
        page.click("#btn-scan")
        page.wait_for_selector("#dashboard-content:not(.hidden)", timeout=30000)
        page.click("#nav-results")

        row = page.locator(".result-item").filter(
            has=page.locator(".result-path", has_text="oldproj")
        ).first
        row_name = row.locator(".result-name").inner_text()
        row.locator(".btn-danger").click()
        modal_target = page.locator(".path-display").inner_text()

        assert row_name == "oldproj (Proje)"
        assert ".git" not in row_name
        assert Path(modal_target).name == "oldproj"
        browser.close()

def test_archive_flow(api_server, tmp_path):
    project_dir = tmp_path / "archive_test"
    target_file = project_dir / "test.log"
    project_dir.mkdir()
    target_file.write_text("log data", encoding="utf-8")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(api_server, wait_until="networkidle")
        page.click("#btn-start-scan")
        page.fill("#scan-path", str(tmp_path))
        page.click("#btn-scan")
        page.wait_for_selector("#dashboard-content:not(.hidden)", timeout=30000)
        page.click("#nav-results")

        row = page.locator(".result-item").filter(
            has=page.locator(".result-path", has_text="archive_test")
        ).first
        row.locator(".btn-archive").click()
        page.locator("#modal-confirm").click()

        toast = page.locator(".toast.toast-success", has_text="Arşivlendi").last
        toast.wait_for(timeout=5000)

        archive_dir = tmp_path / ".wastewise_archive"
        archived_files = list(archive_dir.glob("test.log_*.zip"))

        assert "Arşivlendi: test.log" in toast.inner_text()
        assert not target_file.exists()
        assert archived_files
        assert page.locator("#nav-results").evaluate("el => el.classList.contains('active')")
        assert page.locator("#view-results").evaluate("el => el.classList.contains('active')")
        browser.close()


def test_single_delete_stays_on_results_view(api_server, tmp_path):
    target_file = tmp_path / "delete_me.log"
    target_file.write_text("log data", encoding="utf-8")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(api_server, wait_until="networkidle")
        page.click("#btn-start-scan")
        page.fill("#scan-path", str(tmp_path))
        page.click("#btn-scan")
        page.wait_for_selector("#dashboard-content:not(.hidden)", timeout=30000)
        page.click("#nav-results")

        row = page.locator(".result-item").filter(
            has=page.locator(".result-path", has_text="delete_me.log")
        ).first
        row.locator(".btn-danger").click()
        page.locator("#modal-confirm").click()

        toast = page.locator(".toast.toast-success", has_text="Silindi").last
        toast.wait_for(timeout=5000)

        assert "Silindi: delete_me.log" in toast.inner_text()
        assert not target_file.exists()
        assert page.locator("#nav-results").evaluate("el => el.classList.contains('active')")
        assert page.locator("#view-results").evaluate("el => el.classList.contains('active')")
        browser.close()

def test_bulk_clean_flow(api_server, tmp_path):
    # Create multiple waste items
    created_files = []
    for i in range(3):
        file_path = tmp_path / f"test_{i}.log"
        file_path.write_text("log data", encoding="utf-8")
        created_files.append(file_path)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(api_server, wait_until="networkidle")
        page.click("#btn-start-scan")
        page.fill("#scan-path", str(tmp_path))
        page.click("#btn-scan")
        page.wait_for_selector("#dashboard-content:not(.hidden)", timeout=30000)
        page.click("#nav-results")

        page.click("#btn-bulk-clean")
        page.locator("#modal-confirm").click()

        toast = page.locator(
            ".toast.toast-success",
            has_text="Toplu temizlik tamamlandı",
        ).last
        toast.wait_for(timeout=10000)

        assert "Toplu temizlik tamamlandı: 3 öğe silindi." in toast.inner_text()
        assert all(not file_path.exists() for file_path in created_files)
        browser.close()

def test_filter_correctness(api_server, tmp_path):
    (tmp_path / "test.log").write_text("log data", encoding="utf-8")
    
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(api_server, wait_until="networkidle")
        page.click("#btn-start-scan")
        page.fill("#scan-path", str(tmp_path))
        page.click("#btn-scan")
        page.wait_for_selector("#dashboard-content:not(.hidden)", timeout=30000)
        page.click("#nav-results")

        # By default all is selected
        assert page.locator(".result-item").is_visible()
        
        # Click a filter that shouldn't match logs (e.g. forgotten_projects)
        page.click(".filter-btn[data-filter='forgotten_projects']")
        # The log file row should now be hidden
        row = page.locator(".result-item").first
        assert row.evaluate("el => el.style.display") == "none"
        browser.close()
