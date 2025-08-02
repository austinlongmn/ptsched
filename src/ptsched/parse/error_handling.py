from lark.exceptions import UnexpectedInput
from ptsched.parse.parser import ptsched_parser
from ptsched.parse.utils import display_error_line


def lark_error_handler(
    error: UnexpectedInput, file_contents: str, filename: str
) -> str:
    error_message = error.match_examples(
        ptsched_parser.parse,
        {
            "No metadata": [
                """
# Class A

- Tue 20
"""
            ],
            "Missing dash in metadata": [
                """1 January 2024 31 January 2024

# Class A

- Tue 20
""",
                """15 Feb 2024 20 Feb 2024

# Class A

- Wed 21
""",
            ],
            "Invalid date format in metadata": [
                """January 1 2024 - February 1 2024

# Class A

- Tue 20
""",
                """1/1/2024 - 2/1/2024

# Class A

- Tue 20
""",
                """32 January 2024 - 1 February 2024

# Class A

- Tue 20
""",
            ],
            "Invalid month name": [
                """1 Janvier 2024 - 1 February 2024

# Class A

- Tue 20
""",
                """1 Janaury 2024 - 1 February 2024

# Class A

- Tue 20
""",
            ],
            "Invalid year format": [
                """1 January 24 - 1 February 2024

# Class A

- Tue 20
""",
                """1 January 202 - 1 February 2024

# Class A

- Tue 20
""",
            ],
            "Missing class declaration hash": [
                """1 January 2024 - 31 January 2024

Class A

- Tue 20
""",
                """1 January 2024 - 31 January 2024

 Class A

- Tue 20
""",
            ],
            "Missing class name": [
                """1 January 2024 - 31 January 2024

#

- Tue 20
""",
                """1 January 2024 - 31 January 2024

#

- Tue 20
""",
            ],
            "Missing day declaration dash": [
                """1 January 2024 - 31 January 2024

# Class A

Tue 20
""",
                """1 January 2024 - 31 January 2024

# Class A

 Tue 20
""",
            ],
            "Invalid day of week": [
                """1 January 2024 - 31 January 2024

# Class A

- Tues 20
""",
                """1 January 2024 - 31 January 2024

# Class A

- Tuesday 32
""",
                """1 January 2024 - 31 January 2024

# Class A

- Wenesday 20
""",
            ],
            "Invalid day of month": [
                """1 January 2024 - 31 January 2024

# Class A

- Tue 32
""",
                """1 January 2024 - 31 January 2024

# Class A

- Wed 0
""",
                """1 January 2024 - 31 January 2024

# Class A

- Thu 100
""",
            ],
            "Task starting with forbidden characters": [
                """1 January 2024 - 31 January 2024

# Class A

- Tue 20
    - This is not allowed
""",
                """1 January 2024 - 31 January 2024

# Class A

- Wed 21
    # This is not allowed either
""",
            ],
            "Missing day of month in date declaration": [
                """1 January 2024 - 31 January 2024

# Class A

- Tuesday
""",
                """1 January 2024 - 31 January 2024

# Class A

- Fri
""",
            ],
            "Incomplete metadata dates": [
                """1 January - 31 January 2024

# Class A

- Tue 20
""",
                """January 2024 - February 2024

# Class A

- Wed 21
""",
                """2024 - 2024

# Class A

- Thu 22
""",
            ],
            "Empty schedule": ["", "   ", "\n\n\n"],
            "Only metadata, no body": [
                """1 January 2024 - 31 January 2024""",
                """15 Feb 2024 - 20 Feb 2024

""",
            ],
            "Class with no days": [
                """1 January 2024 - 31 January 2024

# Class A

# Class B

- Wed 21
"""
            ],
            "Day with malformed tasks": [
                """1 January 2024 - 31 January 2024

# Class A

- Tue 20
    Task 1
    Task 2
""",
                """1 January 2024 - 31 January 2024

# Class A

- Wed 21
Task without proper indentation
""",
            ],
            "Multiple consecutive dashes": [
                """1 January 2024 - 31 January 2024

# Class A

-- Tue 20
""",
                """1 January 2024 - 31 January 2024

# Class A

- - Wed 21
""",
            ],
            "Multiple consecutive hashes": [
                """1 January 2024 - 31 January 2024

## Class A

- Tue 20
""",
                """1 January 2024 - 31 January 2024

# # Class A

- Wed 21
""",
            ],
            "Invalid whitespace in metadata": [
                """1  January  2024  -  31  January  2024

# Class A

- Tue 20
""",
                """1	January	2024	-	31	January	2024

# Class A

- Wed 21
""",
            ],
            "Metadata on wrong line": [
                """
1 January 2024 - 31 January 2024
# Class A

- Tue 20
""",
                """# Class A
1 January 2024 - 31 January 2024

- Wed 21
""",
            ],
            "Mixed date formats": [
                """1 Jan 2024 - 31 January 2024

# Class A

- Tue 20
""",
                """1 January 2024 - 31 Feb 2024

# Class A

- Wed 21
""",
            ],
            "Missing required newlines": [
                """1 January 2024 - 31 January 2024# Class A
- Tue 20
""",
                """1 January 2024 - 31 January 2024

# Class A- Wed 21
""",
            ],
        },
    )

    return display_error_line(
        error_message if error_message else "Unexpected input.",
        error.line,
        error.column,
        file_contents,
        filename,
    )
