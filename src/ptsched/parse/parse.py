import sys
import json
from lark import Lark

import ptsched.utils as utils
import ptsched.parse.utils as parse_utils
import ptsched.parse.outputs as outputs
from ptsched.parse.transformer import ScheduleTransformer


def parse_file(file):
    result = {}
    result["courses"] = {}

    lark = Lark(parse_utils.get_grammar(), start="schedule", propagate_positions=True)

    file_contents = file.read()

    initial_pass = lark.parse(file_contents)

    transformed_pass = ScheduleTransformer().transform(initial_pass)

    print(transformed_pass)

    validated_pass = validate_schedule(transformed_pass)

    print("Exiting early for debugging...")
    exit(0)

    return validated_pass


def validate_schedule(schedule):
    # Implement validation logic here
    pass


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

    try:
        schedule = parse_file(infile)
    except utils.PTSchedParseException as error:
        print("Error parsing file:", error, file=sys.stderr)
        exit(1)
    except utils.PTSchedValidationException as error:
        print("Validation error:", error, file=sys.stderr)
        exit(1)
    except utils.PTSchedException as error:
        print("Error creating schedule:", error, file=sys.stderr)
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

    if kwargs.get("ast"):
        json.dump(schedule, outfile, default=str, indent=2)
        return
    if kwargs.get("list_courses"):
        for course in schedule["courses"]:
            print(course, file=outfile)
        return

    if kwargs.get("dry_run"):
        return

    result = {}
    for course in sorted(schedule["courses"].keys()):
        for day in sorted(schedule["courses"][course].keys()):
            if day not in result.keys():
                result[day] = {}
            if course not in result[day].keys():
                result[day][course] = []
            for task in schedule["courses"][course][day]:
                result[day][course].append(task)

    if kwargs.get("json"):
        json.dump(result, outfile, default=str, indent="\t")
        return

    if kwargs.get("list_days"):
        for day in result:
            print(day, file=outfile)
        return

    if kwargs.get("markdown"):
        outputs.output_markdown(result, outfile)
        return
    elif kwargs.get("normal"):
        outputs.output_default(result, outfile)
        return
