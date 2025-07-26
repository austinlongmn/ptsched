import json
import uuid
import sys
import pathlib

import ptsched.utils as utils


def init_cmd(arguments):
    init(**vars(arguments))


def init(**kwargs):
    if kwargs.get("set_default"):
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
