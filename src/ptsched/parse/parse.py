import sys
import json

import ptsched.parse.outputs as outputs
from ptsched.parse.transformer import ScheduleTransformer
from ptsched.parse.validate import validate_schedule, ValidationErrors
from ptsched.parse.parser import ptsched_parser
from ptsched.parse.error_handling import lark_error_handler
from lark.exceptions import UnexpectedInput


def parse_str(contents, filename):
    result = {}
    result["courses"] = {}

    initial_pass = ptsched_parser.parse(contents)

    transformed_pass = ScheduleTransformer().transform(initial_pass)

    validated_pass = validate_schedule(transformed_pass, contents, filename)

    return validated_pass


def parse_cmd(arguments):
    parse(**vars(arguments))


def parse(**kwargs):
    filename = kwargs.get("filename")
    if filename is not None:
        try:
            infile = open(filename)
        except OSError as error:
            print("Error when opening file:", error, file=sys.stderr)
            exit(1)
    else:
        infile = sys.stdin

    file_contents = infile.read()

    try:
        schedule = parse_str(file_contents, filename)
    except UnexpectedInput as e:
        print(lark_error_handler(e, file_contents, infile.name), file=sys.stderr)
        exit(1)
    except ValidationErrors as e:
        e.display_errors()
        exit(1)
    finally:
        if infile != sys.stdin:
            infile.close()

    output_filename = kwargs.get("output")
    if output_filename is not None:
        try:
            outfile = open(output_filename, mode="w")
        except OSError as error:
            print("Error when opening file:", error, file=sys.stderr)
            exit(1)
    else:
        outfile = sys.stdout

    if kwargs.get("list_courses"):
        for course in schedule["courses"]:
            print(course, file=outfile)
        return

    if kwargs.get("dry_run"):
        return

    if kwargs.get("json"):
        json.dump(schedule, outfile, default=str, indent="\t")
        return

    if kwargs.get("list_days"):
        for day in schedule:
            print(day, file=outfile)
        return

    if kwargs.get("markdown"):
        for idx, day in enumerate(outputs.render_markdown(schedule)):
            print(("\n" if idx > 0 else "") + day["content"], file=outfile, end="")
        return
    elif kwargs.get("normal"):
        for idx, day in enumerate(outputs.render_default(schedule)):
            print(
                ("\n" if idx > 0 else "") + day["date"] + ":\n\n" + day["content"],
                file=outfile,
                end="",
            )
        return
