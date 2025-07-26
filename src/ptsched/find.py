import json
import datetime

import ptsched.utils as utils


def find_cmd(arguments):
    find(**vars(arguments))


def find(**kwargs):
    try:
        with open(utils.config_path) as config_file:
            config = json.load(config_file)
            ptsched_directory = config["defaultDirectory"]

            if kwargs.get("directory"):
                print(ptsched_directory)
                return

            results = {}
            for filename in utils.scan(ptsched_directory):
                with open(filename) as file:
                    result = {}
                    utils.parse_dates(file.readline(), result, 1)
                    date = datetime.datetime.now().timestamp()
                    time = datetime.datetime.min.time()
                    start_date = datetime.datetime.combine(
                        result["start_date"], time
                    ).timestamp()
                    end_date = datetime.datetime.combine(
                        result["end_date"], time
                    ).timestamp()
                    interval1 = abs(start_date - date)
                    interval2 = abs(end_date - date)
                    results[filename] = min(interval1, interval2)

            def convert(key):
                return results[key]

            print(min(results.keys(), key=convert))

    except FileNotFoundError:
        print(
            "No ptsched configuration has been set. Run\n\n\tptsched --set-default\n\nin your directory of choice."
        )
