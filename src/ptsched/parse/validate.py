import datetime
import sys
from ptsched.parse.utils import display_error, get_dates
from typing import List

WEEKDAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


class ValidationError(Exception):
    def __init__(self, message: str, meta, file_contents: str, file_name: str):
        self.message = display_error(message, meta, file_contents, file_name)


class ValidationErrors(Exception):
    def __init__(self, errors):
        self.errors = errors

    def display_errors(self):
        for error in self.errors:
            print(error.message, file=sys.stderr)


def validate_schedule(schedule, file_contents: str, file_name: str):
    metadata = schedule["metadata"]

    errors = []

    start_date_info = metadata["start_date"]["date_info"]

    start_year = start_date_info["year"]["year"]
    start_month = start_date_info["month"]["month"]
    start_day = start_date_info["day"]["day_of_month"]

    start_date = datetime.date(start_year, start_month, start_day)

    end_date_info = metadata["end_date"]["date_info"]

    end_year = end_date_info["year"]["year"]
    end_month = end_date_info["month"]["month"]
    end_day = end_date_info["day"]["day_of_month"]

    end_date = datetime.date(end_year, end_month, end_day)

    if start_date > end_date:
        # Fatal error, so raise immediately
        raise ValidationErrors(
            [
                ValidationError(
                    "End date cannot be before start date",
                    metadata["end_date"]["meta"],
                    file_contents,
                    file_name,
                )
            ]
        )

    result = {"metadata": {"start_date": start_date, "end_date": end_date}, "days": []}

    existing_class_names = set()
    required_days = get_dates(start_date, end_date)
    for class_ in schedule["classes"]:
        class_name = class_["name"]["name"]

        if class_name in existing_class_names:
            errors.append(
                ValidationError(
                    f'Duplicate class declarations: "{class_name}"',
                    class_["name"]["meta"],
                    file_contents,
                    file_name,
                )
            )
        existing_class_names.add(class_name)

        class_days = class_["days"]

        existing_class_days = set()
        for day in class_days:
            day_date = parse_date(
                day["date_specifier"]["day_of_week"]["day_of_week"],
                day["date_specifier"]["day_of_month"]["day_of_month"],
                start_date,
                end_date,
                day["date_specifier"]["meta"],
                file_contents,
                file_name,
                errors,
            )

            if day_date in existing_class_days:
                errors.append(
                    ValidationError(
                        f'Duplicate class days: "{day_date.isoformat()}"',
                        day["date_specifier"]["meta"],
                        file_contents,
                        file_name,
                    )
                )
            existing_class_days.add(day_date)

            transformed_day = next(
                (x for x in result["days"] if x["date"] == day_date.isoformat()), None
            )

            if transformed_day is None:
                transformed_day = {"date": day_date.isoformat(), "classes": []}
                result["days"].append(transformed_day)

            transformed_class = next(
                (x for x in transformed_day["classes"] if x["name"] == class_name), None
            )

            if transformed_class is None:
                transformed_class = {"name": class_name, "tasks": []}
                transformed_day["classes"].append(transformed_class)

            for task in day["tasks"]:
                transformed_class["tasks"].append(task["task"])

        missing_days = required_days - existing_class_days
        if missing_days:
            errors.append(
                ValidationError(
                    f"{class_name} is missing {', '.join(sorted((x.isoformat() for x in missing_days)))}",
                    class_["name"]["meta"],
                    file_contents,
                    file_name,
                )
            )

    if errors:
        raise ValidationErrors(errors)

    return result


def parse_date(
    weekday: int,
    day_number: int,
    range_start: datetime.date,
    range_end: datetime.date,
    meta,
    file_contents: str,
    file_name: str,
    errors: List[ValidationError],
):
    if range_start.month == range_end.month:
        month = range_start.month
    else:
        month = range_start.month if day_number >= range_start.day else range_end.month

    if range_start.year == range_end.year:
        year = range_start.year
    else:
        year = range_start.year if day_number >= range_start.day else range_end.year

    result = datetime.date(year, month, day_number)
    if result.weekday() != weekday:
        errors.append(
            ValidationError(
                f'Day of week "{WEEKDAYS[weekday]}" does not match date "{result.isoformat()}" ({WEEKDAYS[result.weekday()]}).',
                meta,
                file_contents,
                file_name,
            )
        )
    if not (result >= range_start and result <= range_end):
        errors.append(
            ValidationError(
                "Date not in schedule range", meta, file_contents, file_name
            )
        )

    return result
