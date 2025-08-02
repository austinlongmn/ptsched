from lark import Transformer, v_args


class ScheduleTransformer(Transformer):
    def schedule(self, items):
        return {"metadata": items[0], "classes": items[1]}

    @v_args(meta=True)
    def metadata(self, meta, items):
        return {"start_date": items[0], "end_date": items[1], "meta": meta}

    @v_args(meta=True)
    def class_(self, meta, items):
        return {"name": items[0], "days": items[1], "meta": meta}

    @v_args(meta=True)
    def date_declaration(self, meta, items):
        return {"day_of_week": items[0], "day_of_month": items[1], "meta": meta}

    def body(self, items):
        return items

    @v_args(meta=True)
    def class_declaration(self, meta, items):
        return {"name": str(items[0]), "meta": meta}

    def day_list(self, items):
        return items

    def class_day_tasks(self, items):
        return {"date_specifier": items[0], "tasks": items[1] if len(items) > 1 else []}

    def task_list(self, items):
        return items

    @v_args(meta=True)
    def task(self, meta, items):
        return {"task": str(items[0]), "meta": meta}

    @v_args(meta=True)
    def day_of_week(self, meta, items):
        return {"day_of_week": items[0], "meta": meta}

    @v_args(meta=True)
    def day_of_month(self, meta, items):
        return {"day_of_month": int(items[0]), "meta": meta}

    @v_args(meta=True)
    def year(self, meta, items):
        return {"year": int(items[0]), "meta": meta}

    @v_args(meta=True)
    def month(self, meta, items):
        return {"month": items[0], "meta": meta}

    @v_args(meta=True)
    def date(self, meta, items):
        return {
            "date_info": {"year": items[2], "month": items[1], "day": items[0]},
            "meta": meta,
        }

    def monday(self, items):
        return 0

    def tuesday(self, items):
        return 1

    def wednesday(self, items):
        return 2

    def thursday(self, items):
        return 3

    def friday(self, items):
        return 4

    def saturday(self, items):
        return 5

    def sunday(self, items):
        return 6

    def january(self, items):
        return 1

    def february(self, items):
        return 2

    def march(self, items):
        return 3

    def april(self, items):
        return 4

    def may(self, items):
        return 5

    def june(self, items):
        return 6

    def july(self, items):
        return 7

    def august(self, items):
        return 8

    def september(self, items):
        return 9

    def october(self, items):
        return 10

    def november(self, items):
        return 11

    def december(self, items):
        return 12
