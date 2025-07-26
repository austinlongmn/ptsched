import os
import json
import sys
import time
import datetime
import multiprocessing

import ptsched.utils as utils
from ptsched.syscal import syscal


def schedule_cmd(arguments):
    schedule(**vars(arguments))


def schedule(**kwargs):
    try:
        with open(".ptscheddir") as directory_file:
            directory_info = json.load(directory_file)
    except FileNotFoundError:
        print("No initialized ptsched directory.", file=sys.stderr)
        exit(1)

    utils.update_directory(directory_info)

    files = directory_info["files"]
    c_args = []
    for idx in range(0, len(files)):
        c_args.append(
            (files[idx]["filename"], files[idx]["lastScheduled"], idx, kwargs["quiet"])
        )

    with multiprocessing.Pool(5) as pool:
        result = pool.map(syscal_if_needed, c_args)

    did_change_files = False
    for file_results in result:
        if file_results[0] is not None:
            files[file_results[1]]["lastScheduled"] = time.time()
            did_change_files = True

    if did_change_files and not kwargs.get("no_vcs"):
        os.system("git add \\*.ptsched")
        os.system(
            'git commit -m "Schedule edit at %s"'
            % datetime.datetime.now().strftime("%a %d %b %Y, %I:%M %p")
        )

    with open(".ptscheddir", "w") as directory_file:
        json.dump(directory_info, directory_file)


def syscal_if_needed(file_info_and_id):  # (filename, schedule date, id)
    if file_info_and_id[1] is None or os.path.getmtime(file_info_and_id[0]) > float(
        file_info_and_id[1]
    ):
        if not file_info_and_id[3]:
            print("ptsched syscal", file_info_and_id[0])
        syscal([file_info_and_id[0]])
        return (time.time(), file_info_and_id[2])
    return (None, file_info_and_id[2])
