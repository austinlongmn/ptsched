import importlib.resources
from typing import Optional

TERMINAL_RED = "\033[31m"
TERMINAL_RESET = "\033[0m"


def get_grammar() -> str:
    return importlib.resources.read_text(
        "ptsched", "data", "ptsched.lark", encoding="utf-8"
    )


def display_error_line(
    message: str,
    lineno: int,
    colno: int,
    file_contents: str,
    filename: str,
    endcolno: Optional[int] = None,
) -> str:
    lines = file_contents.splitlines()

    # Get column position (meta.column is 1-based)
    col_start = colno
    col_end = endcolno or col_start + 1

    # Ensure we have valid line numbers
    if lineno < 1 or lineno > len(lines):
        return f"Error: {message}"

    # Get the problematic line (convert to 0-based index)
    error_line = lines[lineno - 1]

    # Print the error message
    result = ""
    result += (
        f"{TERMINAL_RED}Error at {filename}:{lineno} - {message}{TERMINAL_RESET}\n\n"
    )

    # Print the line with line number
    result += f"{lineno:4d} | {error_line}\n"

    # Print carets pointing to the error location
    # Account for the line number prefix and spaces
    prefix_len = len(f"{lineno:4d} | ")
    caret_line = TERMINAL_RED + " " * prefix_len + " " * (col_start - 1) + "^"

    # If we have an end column, show a range with multiple carets
    if col_end > col_start + 1:
        caret_line += "^" * (col_end - col_start - 1)

    caret_line += TERMINAL_RESET

    result += caret_line + "\n"

    return result


def display_error(message, meta, file_contents, filename):
    return display_error_line(
        message, meta.line, meta.column, file_contents, filename, meta.end_column
    )
