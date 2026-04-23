import os
from pathlib import Path
from time import perf_counter

import src.scanner as scanner_module
from src.scanner import Scanner


ONE_GIB = 1024 ** 3
LARGE_FILE_COUNT = 1000
WASTE_FILE_COUNT = 100
MAX_SCAN_SECONDS = 30.0


def _write_small_file(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"x")
    return path


class _SizedStat:
    def __init__(self, stats: os.stat_result, size: int):
        self._stats = stats
        self.st_size = size

    def __getattr__(self, name):
        return getattr(self._stats, name)


def test_performance_ac1_large_metadata_scan(tmp_path, monkeypatch):
    root = tmp_path / "ac1_large_metadata_test"
    root.mkdir()

    large_files = [
        _write_small_file(root / f"mock_1gb_file_{index}.log")
        for index in range(LARGE_FILE_COUNT)
    ]
    waste_files = [
        _write_small_file(root / "node_modules" / "some_package" / f"index_{index}.js")
        for index in range(WASTE_FILE_COUNT)
    ]

    actual_bytes_on_disk = sum(path.stat().st_size for path in [*large_files, *waste_files])
    assert actual_bytes_on_disk == LARGE_FILE_COUNT + WASTE_FILE_COUNT

    reported_sizes = {
        os.path.normcase(os.fspath(path)): ONE_GIB
        for path in [*large_files, *waste_files]
    }
    real_stat = scanner_module.os.stat

    def fake_stat(path, *args, **kwargs):
        stats = real_stat(path, *args, **kwargs)
        fake_size = reported_sizes.get(os.path.normcase(os.fspath(path)))
        if fake_size is None:
            return stats
        return _SizedStat(stats, fake_size)

    scanner = Scanner(str(root))
    monkeypatch.setattr(scanner_module.os, "stat", fake_stat)

    start = perf_counter()
    raw_results = scanner.scan()
    elapsed = perf_counter() - start

    assert elapsed < MAX_SCAN_SECONDS, f"AC-1 Failed: large-metadata scan took {elapsed:.2f} seconds."

    large_file_items = [
        item for item in raw_results
        if item["relative_path"].startswith("mock_1gb_file_")
    ]
    assert len(large_file_items) == LARGE_FILE_COUNT
    assert all(item["size"] == ONE_GIB for item in large_file_items)

    node_modules_items = [item for item in raw_results if item["relative_path"] == "node_modules"]
    assert len(node_modules_items) == 1
    assert node_modules_items[0]["is_dir"] is True
    assert node_modules_items[0]["size"] == WASTE_FILE_COUNT * ONE_GIB
    assert all(
        not item["relative_path"].startswith("node_modules" + os.sep)
        for item in raw_results
    )

    total_size = sum(item["size"] for item in raw_results)
    expected_total_size = (LARGE_FILE_COUNT + WASTE_FILE_COUNT) * ONE_GIB
    assert total_size == expected_total_size
