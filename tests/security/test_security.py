from src.actions import Actions


def test_delete_rejects_root_path_deletion(tmp_path):
    (tmp_path / "keep.txt").write_text("x", encoding="utf-8")

    result = Actions(str(tmp_path)).delete(str(tmp_path))

    assert result["success"] is False, result
    assert tmp_path.exists()


def test_archive_rejects_internal_archive_directory_target(tmp_path):
    target_file = tmp_path / "sample.txt"
    target_file.write_text("x", encoding="utf-8")

    actions = Actions(str(tmp_path))
    first_archive = actions.archive(str(target_file))
    assert first_archive["success"] is True, first_archive

    result = actions.archive(str(tmp_path / Actions.ARCHIVE_DIR_NAME))

    assert result["success"] is False, result
    assert (tmp_path / Actions.ARCHIVE_DIR_NAME).exists()
