from fastapi.testclient import TestClient

from src.actions import Actions
from src.api import app


client = TestClient(app)


def test_api_scan_rejects_missing_directory():
    response = client.post("/api/scan", json={"path": "C:/definitely/missing/wastewise-path"})

    assert response.status_code == 404
    assert "Dizin bulunamadı" in response.json()["detail"]


def test_api_scan_rejects_file_path(tmp_path):
    target_file = tmp_path / "single.txt"
    target_file.write_text("x", encoding="utf-8")

    response = client.post("/api/scan", json={"path": str(target_file)})

    assert response.status_code == 400
    assert "dizin değil" in response.json()["detail"]


def test_api_action_invalid_action_type(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    target = root / "test.log"
    target.write_text("x", encoding="utf-8")

    response = client.post(
        "/api/action",
        json={
            "action": "magic_delete",
            "target_path": str(target),
            "root_path": str(root),
        },
    )

    assert response.status_code == 400
    assert "Geçersiz aksiyon" in response.json()["detail"]


def test_api_action_missing_target(tmp_path):
    root = tmp_path / "root"
    root.mkdir()

    response = client.post(
        "/api/action",
        json={
            "action": "delete",
            "root_path": str(root),
        },
    )

    assert response.status_code == 422


def test_api_action_missing_root_path(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    target = root / "test.log"
    target.write_text("x", encoding="utf-8")

    response = client.post(
        "/api/action",
        json={
            "action": "delete",
            "target_path": str(target),
        },
    )

    assert response.status_code == 422


def test_api_action_rejects_missing_target_on_disk(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    target = root / "missing.log"

    response = client.post(
        "/api/action",
        json={
            "action": "delete",
            "target_path": str(target),
            "root_path": str(root),
        },
    )

    assert response.status_code == 400
    assert "Hedef bulunamadi" in response.json()["detail"]


def test_api_action_rejects_path_outside_root(tmp_path):
    root = tmp_path / "root"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    target = outside / "secret.txt"
    target.write_text("secret", encoding="utf-8")

    response = client.post(
        "/api/action",
        json={
            "action": "delete",
            "target_path": str(target),
            "root_path": str(root),
        },
    )

    assert response.status_code == 400
    assert "Kok dizin disinda" in response.json()["detail"]


def test_api_action_rejects_root_path_target(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    (root / "keep.txt").write_text("x", encoding="utf-8")

    response = client.post(
        "/api/action",
        json={
            "action": "delete",
            "target_path": str(root),
            "root_path": str(root),
        },
    )

    assert response.status_code == 400
    assert "Kok dizinin kendisi" in response.json()["detail"]


def test_api_action_rejects_archive_directory_target(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    target = root / "sample.txt"
    target.write_text("x", encoding="utf-8")

    first_response = client.post(
        "/api/action",
        json={
            "action": "archive",
            "target_path": str(target),
            "root_path": str(root),
        },
    )
    assert first_response.status_code == 200

    archive_dir = root / Actions.ARCHIVE_DIR_NAME
    response = client.post(
        "/api/action",
        json={
            "action": "archive",
            "target_path": str(archive_dir),
            "root_path": str(root),
        },
    )

    assert response.status_code == 400
    assert "Arsiv dizininin kendisi" in response.json()["detail"]


def test_api_action_rejects_file_inside_archive_directory(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    target = root / "sample.txt"
    target.write_text("x", encoding="utf-8")

    first_response = client.post(
        "/api/action",
        json={
            "action": "archive",
            "target_path": str(target),
            "root_path": str(root),
        },
    )
    assert first_response.status_code == 200

    archive_file = next((root / Actions.ARCHIVE_DIR_NAME).glob("*.zip"))
    response = client.post(
        "/api/action",
        json={
            "action": "archive",
            "target_path": str(archive_file),
            "root_path": str(root),
        },
    )

    assert response.status_code == 400
    assert "Arsiv dizini icindeki dosyalar" in response.json()["detail"]
