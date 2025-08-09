import os
import sys

import datetime

import ptsched.utils as utils
from ptsched.update import update


def schedule_cmd(arguments):
    schedule(**vars(arguments))


def schedule(**kwargs):
    file_pairs = utils.find_updated_file_pairs()

    failed_files = []
    for schedule_file, output_file in file_pairs:
        try:
            update(schedule_file, output_file)
        except Exception as e:
            failed_files.append((schedule_file, e))

    if failed_files:
        print(f"\nFailed to process {len(failed_files)} file(s).", file=sys.stderr)
        sys.exit(1)

    if not kwargs.get("no_vcs"):
        os.system("git add \\*.ptsched")
        os.system(
            'git commit -m "Schedule edit at %s"'
            % datetime.datetime.now().strftime("%a %d %b %Y, %I:%M %p")
        )
