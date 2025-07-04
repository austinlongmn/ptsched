import argparse
import json
import uuid
import sys
import pathlib

import ptsched.utils as utils


def init(arguments):
    schedule_argument_parser = argparse.ArgumentParser(
        "ptsched init", description="Initialize a ptsched directory"
    )
    schedule_argument_parser.add_argument(
        "-s",
        "--set-default",
        action="store_true",
        help="Sets the directory as the default ptsched directory for the user. A new ptsched directory will not be created.",
    )
    args = schedule_argument_parser.parse_args(arguments)

    if args.set_default:
        try:
            with open(utils.config_path) as r_file:
                config = json.load(r_file)
        except FileNotFoundError:
            config = {}
        config["defaultDirectory"] = str(pathlib.Path.cwd())
        with open(utils.config_path, "w") as w_file:
            json.dump(config, w_file)
        return

    try:
        with open(".ptscheddir", "x") as directory_file:
            ptsched_directory = {}
            directory_id = uuid.uuid4().hex.upper()
            ptsched_directory["directoryID"] = directory_id
            ptsched_directory["files"] = []

            utils.update_directory(ptsched_directory)

            json.dump(ptsched_directory, directory_file)
    except FileExistsError:
        print("A ptsched directory already exists in this folder.", file=sys.stderr)
        exit(17)
