import datetime
import pathlib
import os


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


def get_dates(start_date: datetime.date, end_date: datetime.date) -> set[datetime.date]:
    result = set()
    while start_date <= end_date:
        result.add(start_date)
        start_date += datetime.timedelta(days=1)
    return result
