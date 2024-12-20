import argparse
import sys

from .utils import *

# Syntax of schedule file

# 20 May 2024 - 26 May 2024 ~ Date range must be at very first line of file
# ~ Comments begin with a tilde ("~")

# # ABC0000 Course Name ~ Name of course

# - Mon 20 ~ Tasks date
# Task 1
# Task 2
# Task 3 ~ Put tasks under date

# - Tue 21 ~ New date
# Task 4

# # XYZ0000 New Course Name

# - Mon 20
# Task ABC

from .parse import parse
from .init import init
from .syscal import syscal
from .schedule import schedule
from .find import find

subcommands = {
	"parse":    parse,
	"init":     init,
	"syscal":   syscal,
	"schedule": schedule,
	"find":     find
}

valid_subcommand_description = ""
for subcommand in subcommands:
	valid_subcommand_description += subcommand + ", "
valid_subcommand_description = valid_subcommand_description.removesuffix(", ")

def main():
	# this is for displaying error and help messages
	mock_argument_parser = argparse.ArgumentParser(
		prog="ptsched",
		description="ptsched schedules your class work into your calendar."
	)
	mock_argument_parser.add_argument("subcommand", help="The operation to run. Valid options are %s" % valid_subcommand_description)
	mock_argument_parser.add_argument("arguments", help="Arguments to pass to the operation", nargs="*")

	if len(sys.argv) == 1:
		# this should throw and halt the program
		mock_argument_parser.parse_args(sys.argv[1:])
		raise Exception("Unexpectedly continued after faulty arguments.")
	elif sys.argv[1] == "--help" or sys.argv[1] == "-h":
		arr = sys.argv[:]
		arr.append("--help")
		mock_argument_parser.parse_args(arr)

	subcommand = sys.argv[1]
	arguments = sys.argv[2:]

	if not subcommand in subcommands:
		print("Error: invalid subcommand \"%s\". Valid subcommands are %s" % (subcommand, subcommands), file=sys.stderr)
		exit(1)

	subcommands[subcommand](arguments)

if __name__ == "__main__":
	main()
