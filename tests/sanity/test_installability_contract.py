from pathlib import Path
import tomllib

from src.main import resolve_default_command


ROOT = Path(__file__).resolve().parents[2]


def _load_pyproject() -> dict:
    with (ROOT / "pyproject.toml").open("rb") as fh:
        return tomllib.load(fh)


def test_default_command_falls_back_to_serve_without_webview():
    assert resolve_default_command(webview_available=False) == "serve"
    assert resolve_default_command(webview_available=True) == "app"


def test_pyproject_declares_runtime_dev_desktop_and_build_surfaces():
    project = _load_pyproject()["project"]
    dependencies = project["dependencies"]
    extras = project["optional-dependencies"]

    assert any(dep.startswith("fastapi") for dep in dependencies)
    assert any(dep.startswith("uvicorn") for dep in dependencies)
    assert any(dep.startswith("pydantic") for dep in dependencies)
    assert any(dep.startswith("rich") for dep in dependencies)

    assert any(dep.startswith("pywebview") for dep in extras["desktop"])
    assert any(dep.startswith("win10toast") for dep in extras["desktop"])

    assert any(dep.startswith("pytest") for dep in extras["dev"])
    assert any(dep.startswith("playwright") for dep in extras["dev"])
    assert any(dep.startswith("httpx") for dep in extras["dev"])

    assert any(dep.startswith("pyinstaller") for dep in extras["build"])
    assert any(dep.startswith("pywin32") for dep in extras["build"])


def test_requirement_wrappers_exist_for_runtime_dev_and_build():
    assert (ROOT / "requirements.txt").read_text(encoding="utf-8").strip() == "-e ."
    assert (ROOT / "requirements-dev.txt").read_text(encoding="utf-8").strip() == "-e .[dev]"
    assert (ROOT / "requirements-build.txt").read_text(encoding="utf-8").strip() == "-e .[desktop,build]"
