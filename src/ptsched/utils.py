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
                result.append(
                    str(pathlib.Path(directory).joinpath(file).relative_to(dir))
                )
    return result


def find_file_pairs(dir=str(pathlib.Path.cwd())):
    files = find_files(dir)
    pairs = []
    for file in files:
        pairs.append((file, "out/" + file + ".md"))
    return pairs


def find_updated_file_pairs(dir=str(pathlib.Path.cwd())):
    pairs = find_file_pairs(dir)
    updated_pairs = []
    for input_file, output_file in pairs:
        input_path = pathlib.Path(dir) / input_file
        output_path = pathlib.Path(dir) / output_file

        # If output file doesn't exist, include the pair
        if not output_path.exists():
            updated_pairs.append((input_file, output_file))
            continue

        # If input file is newer than output file, include the pair
        input_mtime = input_path.stat().st_mtime
        output_mtime = output_path.stat().st_mtime
        if input_mtime > output_mtime:
            updated_pairs.append((input_file, output_file))

    return updated_pairs


def get_dates(start_date: datetime.date, end_date: datetime.date) -> set[datetime.date]:
    result = set()
    while start_date <= end_date:
        result.add(start_date)
        start_date += datetime.timedelta(days=1)
    return result
