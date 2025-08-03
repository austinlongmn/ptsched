import datetime


class Task:
    """Represents a task."""

    def __init__(self, name: str):
        self.name = name


class SchoolClass:
    """Represents a class currently being taken."""

    def __init__(self, name: str):
        self.name = name


class Day:
    """Represents one day of tasks to do."""

    def __init__(self, date: datetime.date):
        self.date = date

    def __str__(self):
        return self.date.isoformat()


class DayTransformed(Day):
    """Represents a day of tasks to do, organized by class."""

    def __init__(self, date: datetime.date, classes: list["SchoolClassTransformed"]):
        super().__init__(date)
        self.classes = classes


class DayReverse(Day):
    """Represents a day of tasks to do."""

    def __init__(self, date: datetime.date, tasks: list[Task]):
        super().__init__(date)
        self.tasks = tasks


class SchoolClassTransformed(SchoolClass):
    """Represents the tasks for one class on one day."""

    def __init__(self, name: str, tasks: list[Task]):
        super().__init__(name)
        self.tasks = tasks


class SchoolClassReverse(SchoolClass):
    """Represents the tasks in the schedule for one class, organized by day."""

    def __init__(self, name: str, days: list[DayReverse]):
        super().__init__(name)
        self.days = days


class Schedule:
    """A schedule of tasks."""

    class Metadata:
        def __init__(self, start_date: datetime.date, end_date: datetime.date):
            self.start_date = start_date
            self.end_date = end_date

    def __init__(self, metadata: Metadata):
        self.metadata = metadata


class ScheduleTransformed(Schedule):
    """The schedule organized by day and then by class."""

    def __init__(self, metadata: Schedule.Metadata, days: list[DayTransformed]):
        super().__init__(metadata)
        self.days = days

    def to_reverse(self) -> "ScheduleReverse":
        classes = []
        for day in self.days:
            for task in day.tasks:
                classes.append(
                    SchoolClassReverse(task.name, [DayReverse(day.date, [task])])
                )
        return ScheduleReverse(self.metadata, classes)


class ScheduleReverse(Schedule):
    """The schedule organized by class and then by day."""

    def __init__(self, metadata: Schedule.Metadata, classes: list[SchoolClassReverse]):
        super().__init__(metadata)
        self.classes = classes

    def to_transformed(self) -> "ScheduleTransformed":
        days = []
        for cls in self.classes:
            for day in cls.days:
                tasks = []
                for task in day.tasks:
                    tasks.append(Task(task.name))
                days.append(DayTransformed(day.date, tasks))
        return ScheduleTransformed(self.metadata, days)
