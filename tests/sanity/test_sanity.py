import os
import subprocess
import sys


MODULES = ("src.api", "src.classifier", "src.main")


def test_package_style_imports_work_from_repo_root():
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    module_list = ",".join(repr(name) for name in MODULES)
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import importlib; "
                f"mods=[{module_list}]; "
                "[importlib.import_module(name) for name in mods]"
            ),
        ],
        capture_output=True,
        text=True,
        cwd=".",
        env=env,
    )
    assert result.returncode == 0, result.stderr or result.stdout


def test_cli_help_renders_without_encoding_errors():
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "cp1254"
    result = subprocess.run(
        [sys.executable, "src/main.py", "--help"],
        capture_output=True,
        text=True,
        cwd=".",
        env=env,
    )
    assert result.returncode == 0, result.stderr or result.stdout


def test_cli_scan_runs_on_a_small_directory(tmp_path):
    (tmp_path / "sample.txt").write_text("ok", encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "cp1254"
    result = subprocess.run(
        [sys.executable, "src/main.py", "scan", str(tmp_path)],
        capture_output=True,
        text=True,
        cwd=".",
        env=env,
    )
    assert result.returncode == 0, result.stderr or result.stdout
