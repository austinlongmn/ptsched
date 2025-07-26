import os
import argparse
import datetime
import multiprocessing

import ptsched.utils as utils
from ptsched.update import update_file


def schedule(arguments):
    schedule_argument_parser = argparse.ArgumentParser(
        "ptsched schedule",
        description="Schedules changed .ptsched files to a directory.",
    )
    schedule_argument_parser.add_argument(
        "-q", "--quiet", action="store_true", help="Do not output extra information"
    )
    schedule_argument_parser.add_argument(
        "--no-vcs", action="store_true", help="Do not commit changes to version control"
    )
    args = schedule_argument_parser.parse_args(arguments)

    file_pairs = utils.find_file_pairs()

    with multiprocessing.Pool(5) as pool:
        pool.map(update_file, file_pairs)

    if not args.no_vcs:
        os.system("git add \\*.ptsched")
        os.system(
            'git commit -m "Schedule edit at %s"'
            % datetime.datetime.now().strftime("%a %d %b %Y, %I:%M %p")
        )
