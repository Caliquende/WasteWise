import json
import subprocess
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from src.scanner import Scanner


def _post_json(url: str, payload: dict) -> tuple[int, dict]:
    req = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(req, timeout=5) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def _get_json(url: str) -> tuple[int, dict]:
    with urlopen(url, timeout=5) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def test_scanner_does_not_escape_root_via_directory_junction(tmp_path):
    root = tmp_path / "root"
    outside = tmp_path / "outside"
    link_path = root / "linkdir"

    root.mkdir()
    outside.mkdir()
    (outside / "outside.txt").write_text("secret", encoding="utf-8")

    result = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(link_path), str(outside)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout

    items = Scanner(str(root)).scan()
    relative_paths = {item["relative_path"].replace("\\", "/") for item in items}

    assert "linkdir/outside.txt" not in relative_paths


def test_last_scan_is_not_exposed_to_a_fresh_client(api_server, tmp_path):
    root = tmp_path / "scan-a"
    root.mkdir()
    (root / ".env").write_text("SECRET=1", encoding="utf-8")

    status, _ = _post_json(f"{api_server}/api/scan", {"path": str(root)})
    assert status == 200

    try:
        status, payload = _get_json(f"{api_server}/api/last-scan")
    except HTTPError as exc:
        assert exc.code == 404
    else:
        assert status == 404, payload
