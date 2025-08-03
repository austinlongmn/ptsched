import argparse

# Syntax of schedule file

# 20 May 2024 - 26 May 2024 ~ Date range must be at very first line of file
# ~ Comments begin with a tilde ("~")

# # ABC0000 Course Name ~ Name of course

# - Mon 20 ~ Tasks date
# Task 1
# Task 2
# Task 3 ~ Put tasks under date

# - Tue 21 ~ New date
# Task 4

# # XYZ0000 New Course Name

# - Mon 20
# Task ABC

from ptsched.parse import parse_cmd
from ptsched.init import init_cmd
from ptsched.syscal import syscal_cmd
from ptsched.schedule import schedule_cmd
from ptsched.find import find_cmd
from ptsched.generate import generate_cmd


def main():
    argument_parser = argparse.ArgumentParser(
        prog="ptsched",
        description="ptsched schedules your class work into your calendar.",
    )
    subparsers = argument_parser.add_subparsers(required=True)

    parse_argument_parser = subparsers.add_parser(
        "parse", description="Parse a ptsched file and output the result"
    )
    parse_argument_parser.set_defaults(func=parse_cmd)
    parse_argument_parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="Parse file, but do not output anything.",
    )
    output_group = parse_argument_parser.add_mutually_exclusive_group()
    output_group.add_argument(
        "-a",
        "--ast",
        action="store_true",
        help="Outputs the abstract syntax tree of the file",
    )
    output_group.add_argument(
        "-c", "--list-courses", action="store_true", help="List courses in the file"
    )
    output_group.add_argument(
        "-y",
        "--list-days",
        action="store_true",
        help="List days in the file, output format is YYYY-MM-DD",
    )
    output_group.add_argument(
        "-j", "--json", action="store_true", help="Outputs in JSON format"
    )
    output_group.add_argument(
        "-m", "--markdown", action="store_true", help="Outputs in Markdown format"
    )
    output_group.add_argument(
        "-n",
        "--normal",
        action="store_true",
        help="Outputs in normal format (the default)",
        default=True,
    )
    parse_argument_parser.add_argument(
        "-o", "--output", help="The file to output to (default is STDOUT)"
    )
    parse_argument_parser.add_argument(
        "filename", help="The file to read (default is STDIN)", nargs="?"
    )

    schedule_argument_parser = subparsers.add_parser(
        "schedule",
        description="Schedules changed .ptsched files into your calendar via syscal",
    )
    schedule_argument_parser.set_defaults(func=schedule_cmd)
    schedule_argument_parser.add_argument(
        "-q", "--quiet", action="store_true", help="Do not output extra information"
    )
    schedule_argument_parser.add_argument(
        "--no-vcs", action="store_true", help="Do not commit changes to version control"
    )

    syscal_argument_parser = subparsers.add_parser(
        "syscal",
        description="Launches a helper program to write ptsched schedules to the system calendar",
    )
    syscal_argument_parser.set_defaults(func=syscal_cmd)
    syscal_argument_parser.add_argument("filename", help="The schedule file to use")

    find_argument_parser = subparsers.add_parser(
        "find", description="Finds the default ptsched file for new additions"
    )
    find_argument_parser.set_defaults(func=find_cmd)
    find_argument_parser.add_argument(
        "-d", "--directory", help="Gives the directory instead of the file"
    )

    init_argument_parser = subparsers.add_parser(
        "init", description="Initialize a ptsched directory"
    )
    init_argument_parser.set_defaults(func=init_cmd)
    init_argument_parser.add_argument(
        "-s",
        "--set-default",
        action="store_true",
        help="Sets the directory as the default ptsched directory for the user. A new ptsched directory will not be created.",
    )

    generate_argument_parser = subparsers.add_parser(
        "generate", description="Generates a ptsched file from a template"
    )
    generate_argument_parser.set_defaults(func=generate_cmd)
    generate_argument_parser.add_argument("-o", "--output", help="Output file")
    generate_argument_parser.add_argument(
        "-c",
        "--class",
        help="A class to generate output for",
        action="append",
        dest="classes",
    )

    args = argument_parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
