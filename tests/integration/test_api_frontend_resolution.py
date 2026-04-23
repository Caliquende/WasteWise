from pathlib import Path

from src import api


def test_resolve_frontend_dir_prefers_bundle_root_when_available(tmp_path):
    bundle_frontend = tmp_path / "bundle" / "frontend"
    source_frontend = tmp_path / "source" / "frontend"
    bundle_frontend.mkdir(parents=True)
    source_frontend.mkdir(parents=True)

    resolved = api.resolve_frontend_dir(
        module_path=tmp_path / "source" / "src" / "api.py",
        bundle_root=bundle_frontend.parent,
    )

    assert resolved == bundle_frontend


def test_resolve_frontend_dir_falls_back_to_source_layout(tmp_path):
    source_frontend = tmp_path / "source" / "frontend"
    source_frontend.mkdir(parents=True)

    resolved = api.resolve_frontend_dir(
        module_path=tmp_path / "source" / "src" / "api.py",
        bundle_root=tmp_path / "missing_bundle",
    )

    assert resolved == source_frontend


def test_resolve_frontend_dir_returns_none_when_frontend_missing(tmp_path):
    resolved = api.resolve_frontend_dir(
        module_path=tmp_path / "source" / "api.py",
        bundle_root=tmp_path / "missing_bundle",
    )

    assert resolved is None
