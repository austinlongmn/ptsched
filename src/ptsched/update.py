import os
import difflib
import re

from ptsched.parse import parse_str_display_errors
from ptsched.parse.outputs import render_markdown


def update_str(new_schedule, current_schedule):
    current_schedule_stripped = re.sub(r"\[x\]", "[ ]", current_schedule)

    diff_result = difflib.Differ().compare(
        current_schedule_stripped.splitlines(), new_schedule.splitlines()
    )

    output_string = ""
    current_schedule_lines = current_schedule.splitlines()
    current_line = 0
    for line in diff_result:
        if line.startswith("?"):
            continue
        elif line.startswith("+"):
            output_string += re.sub(r"^\+ ", "", line) + "\n"
        elif line.startswith("-"):
            current_line += 1
        elif line.startswith(" "):
            if "[x]" in current_schedule_lines[current_line]:
                output_string += re.sub(r"\[ \]", "[x]", line[2:]) + "\n"
            else:
                output_string += line[2:] + "\n"
            current_line += 1

    return output_string


def update_file(new_schedule, current_schedule_file):
    """Updates the markdown file with the new schedule, keeping the Markdown check boxes checked if tasks are already completed."""
    try:
        with open(current_schedule_file, "r") as file:
            current_schedule = file.read()
    except FileNotFoundError:
        current_schedule = ""

    output_string = update_str(new_schedule, current_schedule)

    os.makedirs(os.path.dirname(current_schedule_file), exist_ok=True)

    with open(current_schedule_file, "w") as file:
        file.write(output_string)


def update(schedule_file, output_file):
    """Updates the markdown file with the new schedule, keeping the Markdown check boxes checked if tasks are already completed."""

    with open(schedule_file, "r") as file:
        new_schedule = file.read()

    schedule = parse_str_display_errors(new_schedule, schedule_file)

    output = render_markdown(schedule)

    update_file(output, output_file)
