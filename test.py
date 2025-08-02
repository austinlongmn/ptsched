from lark import v_args, Transformer, Lark
import datetime

from ptsched.utils import parse_date


def post_transform(schedule):
    start_date = schedule['metadata']['start_date']
    end_date = schedule['metadata']['end_date']

    for class_ in schedule['classes']:
        for day in class_['days']:
            date = datetime.date

parser = Lark(open("src/ptsched/ptsched.lark").read(), start="schedule", propagate_positions=True)

parsed_tree = parser.parse(open( "tests/test_data/input/fa24/2024-06-18.ptsched" ).read())

print(parsed_tree.pretty())

print(ScheduleTransformer().transform(parsed_tree))
