from pathlib import PurePosixPath, PureWindowsPath


def is_plain_file_name(value: str) -> bool:
    """Return True only for a bare file name, not a path."""
    if not value:
        return False

    windows_path = PureWindowsPath(value)
    posix_path = PurePosixPath(value)

    if windows_path.is_absolute() or posix_path.is_absolute():
        return False

    if windows_path.name != value:
        return False

    if posix_path.name != value:
        return False

    return True


def get_file_extension(file_name: str) -> str:
    """Return the file extension (without leading dot) for a file name or path."""
    if not file_name:
        return ""

    windows_suffix = PureWindowsPath(file_name).suffix
    posix_suffix = PurePosixPath(file_name).suffix

    # Prefer whichever parser identifies a suffix for cross-platform path strings.
    suffix = windows_suffix or posix_suffix
    if not suffix.startswith("."):
        return ""

    return suffix[1:]
