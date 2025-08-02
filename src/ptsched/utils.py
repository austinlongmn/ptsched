import datetime
import pathlib
import os
import re


class PTSchedException(Exception):
    pass


class PTSchedParseException(PTSchedException):
    pass


class PTSchedValidationException(PTSchedException):
    pass


def parse_date(weekday, day_number, range_start, range_end, lineno):
    if range_start.month == range_end.month:
        month = range_start.month
    else:
        month = range_start.month if day_number >= range_start.day else range_end.month

    if range_start.year == range_end.year:
        year = range_start.year
    else:
        year = range_start.year if day_number >= range_start.day else range_end.year

    result = datetime.date(year, month, day_number)
    if weekday == -1:
        raise PTSchedParseException(
            'Invalid day of week "%s" at line %d' % (weekday, lineno)
        )
    if result.weekday() != weekday:
        raise PTSchedValidationException(
            'Day of week "%s" does not match date at line %d' % (weekday, lineno)
        )
    if not (result >= range_start and result <= range_end):
        raise PTSchedValidationException("Date not in range at line %d" % lineno)

    return result


def scan(dir=str(pathlib.Path.cwd())):
    result = []
    path = pathlib.Path(dir)
    for directory, _, files in os.walk(str(path)):
        if ".ptschedignore" in files:
            continue
        for file in files:
            if file.endswith(".ptsched"):
                result.append(str(pathlib.Path(directory).joinpath(file)))
    return result


def find_files(dir=str(pathlib.Path.cwd())):
    result = []
    path = pathlib.Path(dir)
    for directory, _, files in os.walk(str(path)):
        if ".ptschedignore" in files:
            continue
        for file in files:
            if file.endswith(".ptsched"):
                result.append(str(pathlib.Path(directory).joinpath(file)))
    return result


def find_file_pairs(dir=str(pathlib.Path.cwd())):
    files = find_files(dir)
    pairs = []
    for file in files:
        pairs.append((file, "out/" + file))
    return pairs


def parse_dates(line, result, lineno):
    """
    parse the contents of line as a date range

    line -- the line contents of the file containing the date range
    result -- the result - this will be modified by the function
    lineno -- the line number for diagnostic messages

    This function parses the contents of line and puts the results into result.
    Upon successful completion, result["start_date"] and result["end_date"] will
    be set to the parsed values (datetime.datetime objects).
    """
    re_result = re.match(r"^\s*(.+?)\s*[-–—]\s*(.+?)\s*$", line)
    try:
        if not re_result:
            raise ValueError()
        result["start_date"] = datetime.datetime.strptime(
            re_result.group(1), "%d %B %Y"
        ).date()
        result["end_date"] = datetime.datetime.strptime(
            re_result.group(2), "%d %B %Y"
        ).date()
    except ValueError:
        raise PTSchedParseException(
            "Invalid dates at line %d: %s" % (lineno, line.removesuffix("\n"))
        )

    s_date = result["start_date"]
    e_date = result["end_date"]

    if s_date > e_date:
        raise PTSchedValidationException(
            "Start date cannot exceed end date at line %d" % (lineno)
        )

    if s_date.month != e_date.month:
        if (e_date.month - s_date.month) > 1 or e_date.day >= s_date.day:
            raise PTSchedValidationException(
                "Date range cannot exceed 1 month at line %d" % (lineno)
            )


config_path = str(pathlib.Path.home().joinpath(".ptschedconfig"))
