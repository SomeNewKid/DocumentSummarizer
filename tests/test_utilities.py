"""Unit tests for utility helpers."""

import pytest

from document_summarizer.utilities import get_file_extension, is_plain_file_name


@pytest.mark.parametrize(
    "value",
    [
        "file.txt",
        "README",
        ".env",
        "report 2026.md",
        "name-with-dashes.log",
    ],
)
def test_is_plain_file_name_accepts_bare_file_names(value: str) -> None:
    """Return True for names that do not include path components."""
    assert is_plain_file_name(value) is True


@pytest.mark.parametrize(
    "value",
    [
        "",
        "/etc/hosts",
        "C:/Windows/notepad.exe",
        "C:\\Windows\\notepad.exe",
        "./notes.txt",
        "../notes.txt",
        "folder/notes.txt",
        "folder\\notes.txt",
        "folder/",
        "folder\\",
    ],
)
def test_is_plain_file_name_rejects_paths_and_empty_values(value: str) -> None:
    """Return False for empty strings or anything that represents a path."""
    assert is_plain_file_name(value) is False


@pytest.mark.parametrize(
    ("file_name", "expected"),
    [
        ("file.txt", "txt"),
        ("README.md", "md"),
        ("archive.tar.gz", "gz"),
        ("folder/note.log", "log"),
        ("folder\\note.log", "log"),
        ("./relative/path/report.csv", "csv"),
        ("C:/temp/config.json", "json"),
        ("C:\\temp\\config.json", "json"),
        ("no_extension", ""),
        (".env", ""),
        ("folder/", ""),
        ("", ""),
    ],
)
def test_get_file_extension_returns_expected_suffix(
    file_name: str,
    expected: str,
) -> None:
    """Return the last extension segment without a leading dot."""
    assert get_file_extension(file_name) == expected
