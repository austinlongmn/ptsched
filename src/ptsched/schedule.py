import os

import datetime
import multiprocessing

import ptsched.utils as utils
from ptsched.update import update_file


def schedule_cmd(arguments):
    schedule(**vars(arguments))


def schedule(**kwargs):
    file_pairs = utils.find_file_pairs()

    with multiprocessing.Pool(5) as pool:
        pool.map(update_file, file_pairs)

    if not kwargs.get("no_vcs"):
        os.system("git add \\*.ptsched")
        os.system(
            'git commit -m "Schedule edit at %s"'
            % datetime.datetime.now().strftime("%a %d %b %Y, %I:%M %p")
        )
