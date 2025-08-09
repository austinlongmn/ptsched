import sys
import os.path
from ptsched.parse import generate_file
from ptsched.utils import get_dates
from ptsched.structures import ScheduleReverse, SchoolClassReverse, DayReverse
from datetime import date, timedelta


def generate_cmd(arguments):
    generate(**vars(arguments))


def generate(**kwargs):
    date_range = get_date_range()
    filename = kwargs.get("outfile")
    if filename is not None:
        # Check if filename points to a directory
        if os.path.isdir(filename):
            start_date_str = date_range[0].strftime("%Y-%m-%d")
            filename = os.path.join(filename, f"{start_date_str}.ptsched")

        try:
            outfile = open(filename, "w")
        except OSError as error:
            print("Error when opening file:", error, file=sys.stderr)
            exit(1)
    else:
        outfile = sys.stdout

    try:
        print(
            generate_file(
                ScheduleReverse(
                    metadata=ScheduleReverse.Metadata(
                        start_date=date_range[0], end_date=date_range[1]
                    ),
                    classes=[
                        SchoolClassReverse(
                            name=x,
                            days=[
                                DayReverse(date=x2, tasks=[])
                                for x2 in sorted(
                                    get_dates(date_range[0], date_range[1])
                                )
                            ],
                        )
                        for x in kwargs.get("classes", [])
                    ],
                )
            ),
            file=outfile,
            end="",
        )
    finally:
        if outfile != sys.stdout:
            outfile.close()


def get_date_range():
    """Returns a tuple of today (or next Monday if on weekend) until next Friday"""
    today = date.today()
    if today.weekday() >= 5:
        next_monday = today + timedelta(days=(7 - today.weekday()) % 7)
    else:
        next_monday = today
    next_friday = next_monday + timedelta(days=(4 - next_monday.weekday()) % 7)
    return (next_monday, next_friday)
