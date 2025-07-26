import re
import sys
import json

import ptsched.utils as utils


def parse_file(file):
    result = {}
    result["courses"] = {}

    is_parsing_dates = True
    course_name = None
    date = None

    lineno = 1

    line = file.readline()
    while line != "":
        line = re.sub(r"\s?~.+", "", line)
        line = line.removesuffix("\n")
        line = line.strip()
        if re.match(r"^\d{4}-\d{2}-\d{2}:$", line):
            raise utils.PTSchedParseException(
                "Putting dates in this format with a colon at the end of the line could cause conflicts: line %d"
                % lineno
            )
        if line != "":
            if is_parsing_dates:
                utils.parse_dates(line, result, lineno)

                is_parsing_dates = False
            else:
                re_result = re.match(r"^#\s+(.+?)\s*$", line)
                if re_result is not None:
                    course_name = re_result.group(1)
                    if course_name in result.keys():
                        raise utils.PTSchedValidationException(
                            'Cannot redefine course "%s": line %d'
                            % (course_name, lineno)
                        )
                    result["courses"][course_name] = {}
                elif course_name is not None:
                    re_result = re.match(r"^-\s+(.+?)\s+(\d?\d)\s*$", line)
                    if re_result is not None:
                        try:
                            date = utils.parse_date(
                                re_result.group(1),
                                int(re_result.group(2)),
                                result["start_date"],
                                result["end_date"],
                                lineno,
                            )
                        except (ValueError, AttributeError):
                            raise utils.PTSchedParseException(
                                "Invalid date at line %d: %s"
                                % (lineno, line.removesuffix("\n"))
                            )
                        date_str = str(date)
                        if date_str in result["courses"][course_name].keys():
                            raise utils.PTSchedValidationException(
                                'Cannot redefine day %s for course "%s": line %d'
                                % (date_str, course_name, lineno)
                            )
                        result["courses"][course_name][date_str] = []
                    elif date is not None:
                        date_str = str(date)
                        result["courses"][course_name][date_str].append(line)
                    else:
                        raise utils.PTSchedParseException(
                            "Expected date, but line did not match: line %d" % lineno
                        )
                else:
                    raise utils.PTSchedParseException(
                        "Expected course name, but line did not match: line %d" % lineno
                    )

        line = file.readline()
        lineno += 1

    return result


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
        output_markdown(result, outfile)
        return
    elif kwargs.get("normal"):
        output_default(result, outfile)
        return


def output_default(result, outfile):
    try:
        counter = 0
        sorted_days = sorted(result.keys())
        length = len(sorted_days)
        for day in sorted_days:
            print(day + ":\n", file=outfile)

            sorted_courses = sorted(result[day].keys())
            counter2 = 0
            length2 = len(sorted_courses)
            for course in sorted_courses:
                print(course + ":", file=outfile)
                for task in result[day][course]:
                    print(task, file=outfile)
                if not (counter >= length - 1 and counter2 >= length2 - 1):
                    print(file=outfile)
                counter2 += 1
            counter += 1
    finally:
        if outfile != sys.stdout:
            outfile.close()


def output_markdown(result, outfile):
    try:
        counter = 0
        sorted_days = sorted(result.keys())
        length = len(sorted_days)
        for day in sorted_days:
            print("# Tasks: " + day + "\n", file=outfile)

            sorted_courses = sorted(result[day].keys())
            counter2 = 0
            length2 = len(sorted_courses)
            for course in sorted_courses:
                print("## " + course + "\n", file=outfile)
                for task in result[day][course]:
                    print("- [ ] " + task, file=outfile)
                if not (counter >= length - 1 and counter2 >= length2 - 1):
                    print(file=outfile)
                counter2 += 1
            counter += 1
    finally:
        if outfile != sys.stdout:
            outfile.close()
