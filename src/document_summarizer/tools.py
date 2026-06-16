"""File system tools."""

from pathlib import Path

from beeai_framework.tools import tool

from document_summarizer.utilities import get_file_extension


@tool
def get_file_contents(file_name: str) -> str | None:
    """
    Return the contents of the file at the specified location.

    Args:
        file_name (str): the name of the file whose content is to be returned

    Returns:
        (str | None): the content of the named file if the file exists and may be read,
                      otherwise None.
    """

    if not file_name:
        raise ValueError("The `file_name` argument was empty.")

    file_extension = get_file_extension(file_name)
    if file_extension not in ["md", "txt"]:
        raise ValueError("The file is of a type not permitted to be read.")

    root_directory = Path.cwd()
    document_directory = root_directory / "documents"
    file_location = document_directory / file_name

    if not file_location.exists():
        raise RuntimeError("The file does not exist in the documents directory.")

    with open(file_location, encoding="utf-8") as file:
        return file.read()
