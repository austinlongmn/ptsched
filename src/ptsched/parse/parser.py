import ptsched.parse.utils as parse_utils
from lark import Lark

ptsched_parser = Lark(
    parse_utils.get_grammar(), start="schedule", propagate_positions=True
)
