import argparse
import importlib.resources as resources
import sys
import os
import re
import subprocess

from ptsched.parse import parse


def syscal(arguments):
    schedule_argument_parser = argparse.ArgumentParser(
        "ptsched syscal",
        description="Launches a helper program to write ptsched schedules to the system calendar",
    )
    schedule_argument_parser.add_argument("filename", help="The schedule file to use")
    args = schedule_argument_parser.parse_args(arguments)

    output_tmp_filename = tmp_filename()
    parse(["-o", output_tmp_filename, args.filename])
    with open(output_tmp_filename) as file:
        parse_output = file.read()
    os.remove(output_tmp_filename)

    days = re.finditer(
        r"(\d{4}-\d{2}-\d{2}):\n\n((?:.(?!\d{4}-\d{2}-\d{2}:\n\n))+)",
        parse_output,
        re.DOTALL,
    )

    with resources.path("ptsched.bin", "event-helper") as helper_path:
        writing_subprocess = subprocess.Popen(
            helper_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE
        )
        id = 0
        for day in days:
            write_to_calendar(id, day[1], day[2], writing_subprocess.stdin)
            id += 1

        if writing_subprocess.stdin is not None:
            writing_subprocess.stdin.flush()
            writing_subprocess.stdin.close()
        else:
            print("Warning: stdin does not exist on subprocess.", file=sys.stderr)
        writing_subprocess.wait()


def write_to_calendar(id, date, contents, subprocess_input):
    subprocess_input.write(
        (
            "%d\nUPDATE\n%s\n%s\nEND REQUEST\n"
            % (id, date, contents.removesuffix("\n"))
        ).encode()
    )
    subprocess_input.flush()


def tmp_filename():
    return (
        subprocess.check_output(["mktemp", "-t", "ptsched"])
        .decode("utf-8")
        .removesuffix("\n")
    )
