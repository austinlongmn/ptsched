#!/usr/bin/env python3
import argparse
import re
import datetime
import os
import sys

# debug
import json

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

subcommands = [
	"parse",
	"schedule"
]

valid_subcommand_description = ""
for subcommand in subcommands:
	valid_subcommand_description += subcommand + ", "
valid_subcommand_description = valid_subcommand_description.removesuffix(", ")

# MARK: Helper constructs
class PTSchedException(Exception):
	pass


class PTSchedParseException(PTSchedException):
	pass


class PTSchedValidationException(PTSchedException):
	pass

def parse_date(day_of_week, day_number, range_start, range_end, lineno):
	if (range_start.month == range_end.month):
		month = range_start.month
	else:
		month = range_start.month if day_number >= range_start.day else range_end.month

	if (range_start.year == range_end.year):
		year = range_start.year
	else:
		year = range_start.year if day_number >= range_start.day else range_end.year

	weekday = -1
	if (day_of_week == "Mon"):
		weekday = 0
	elif (day_of_week == "Tue"):
		weekday = 1
	elif (day_of_week == "Wed"):
		weekday = 2
	elif (day_of_week == "Thu"):
		weekday = 3
	elif (day_of_week == "Fri"):
		weekday = 4
	elif (day_of_week == "Sat"):
		weekday = 5
	elif (day_of_week == "Sun"):
		weekday = 6
	
	result = datetime.date(year, month, day_number)
	if (weekday == -1):
		raise PTSchedParseException("Invalid day of week \"%s\" at line %d" % (day_of_week, lineno))
	if (result.weekday() != weekday):
		raise PTSchedValidationException("Day of week \"%s\" does not match date at line %d" % (day_of_week, lineno))
	if (not (result >= range_start and result <= range_end)):
		raise PTSchedValidationException("Date not in range at line %d" % lineno)
	
	return result

# MARK: schedule
def schedule(arguments):
	schedule_argument_parser = argparse.ArgumentParser("ptsched schedule", description="Launches a helper program to write ptsched schedules to the system calendar")
	schedule_argument_parser.add_argument("filename", help="The schedule file to use")
	args = schedule_argument_parser.parse_args(arguments)
	abs_path = os.path.abspath(args.filename)

	# The following is a security risk. Do not share this program.
	# TODO: replace this with a Swift helper program
	exit_status = os.system("echo \"%s\" | shortcuts run ptsched --input-path -" % abs_path)

	exit(exit_status)

def parse_dates(line, result, lineno):
	re_result = re.match(r"^\s*(.+?)\s*[-–—]\s*(.+?)\s*$", line)
	try:
		result["start_date"] = datetime.datetime.strptime(re_result.group(1), "%d %B %Y").date()
		result["end_date"] = datetime.datetime.strptime(re_result.group(2), "%d %B %Y").date()
	except (ValueError, AttributeError):
		raise PTSchedParseException("Invalid dates at line %d: %s" % (lineno, line.removesuffix("\n")))
	
	s_date = result["start_date"]
	e_date = result["end_date"]

	if (s_date > e_date):
		raise PTSchedValidationException("Start date cannot exceed end date at line %d" % (lineno))
	
	if (s_date.month != e_date.month):
		if ((e_date.month - s_date.month) > 1 or e_date.day >= s_date.day):
			raise PTSchedValidationException("Date range cannot exceed 1 month at line %d" % (lineno))

# MARK: parse (main function)
def parse_file(file):
	result = {}
	result["courses"] = {}

	is_parsing_dates = True
	course_name = None
	date = None

	lineno = 1

	line = file.readline()
	while (line != ""):
		line = re.sub(r"\s?~.+", "", line)
		line = line.removesuffix("\n")
		line = line.strip()
		if (line != ""):
			if (is_parsing_dates):
				parse_dates(line, result, lineno)

				is_parsing_dates = False
			else:
				re_result = re.match(r"^#\s+(.+?)\s*$", line)
				if (re_result != None):
					course_name = re_result.group(1)
					if (course_name in result.keys()):
						raise PTSchedValidationException("Cannot redefine course \"%s\": line %d" % (course_name, lineno))
					result["courses"][course_name] = {}
				elif (course_name != None):
					re_result = re.match(r"^-\s+(.+?)\s+(\d?\d)\s*$", line)
					if (re_result != None):
						try:
							date = parse_date(re_result.group(1), int(re_result.group(2)), result["start_date"], result["end_date"], lineno)
						except (ValueError, AttributeError):
							raise PTSchedParseException("Invalid date at line %d: %s" % (lineno, line.removesuffix("\n")))
						date_str = str(date)
						if (date_str in result["courses"][course_name].keys()):
							raise PTSchedValidationException("Cannot redefine day %s for course \"%s\": line %d" % (date_str, course_name, lineno))
						result["courses"][course_name][date_str] = []
					elif (date != None):
						date_str = str(date)
						result["courses"][course_name][date_str].append(line)
					else:
						raise PTSchedParseException("Expected date, but line did not match: line %d" % lineno)
				else:
					raise PTSchedParseException("Expected course name, but line did not match: line %d" % lineno)


		line = file.readline()
		lineno += 1
	
	return result

def parse(arguments):
	parse_argument_parser = argparse.ArgumentParser("ptsched parse", description="Parse a ptsched file and output the result")
	parse_argument_parser.add_argument("-d", "--dry-run", action="store_true", help="Parse file, but do not output anything.")
	parse_argument_parser.add_argument("-D", "--debug", action="store_true", help="Display extra debug information")
	parse_argument_parser.add_argument("-o", "--output", help="The file to output to (default is STDOUT)")
	parse_argument_parser.add_argument("filename", help="The file to read (default is STDIN)", nargs="?")
	args = parse_argument_parser.parse_args(arguments)

	filename = args.filename
	if filename != None:
		try:
			infile = open(filename)
		except OSError as error:
			print("Error when opening file:", error, file=sys.stderr)
			exit(1)
	else:
		infile = sys.stdin

	try:
		schedule = parse_file(infile)
	except PTSchedParseException as error:
		print("Error parsing file:", error, file=sys.stderr)
		exit(1)
	except PTSchedValidationException as error:
		print("Validation error:", error, file=sys.stderr)
		exit(1)
	except PTSchedException as error:
		print("Error creating schedule:", error, file=sys.stderr)
		exit(1)
	finally:
		if infile != sys.stdin:
			infile.close()


	if args.debug: print(json.dumps(schedule, default=str, indent=2))

	if args.dry_run: exit(0)

	events = {}

	for course in sorted(schedule["courses"].keys()):
		for day in sorted(schedule["courses"][course].keys()):
			if (not (day in events.keys())):
				events[day] = ""
			events[day] += course + ":\n"
			for task in schedule["courses"][course][day]:
				events[day] += task + "\n"
			events[day] += "\n"

	output_filename = args.output
	if output_filename != None:
		try:
			outfile = open(output_filename, mode="w")
		except OSError as error:
			print("Error when opening file:", error, file=sys.stderr)
			exit(1)
	else:
		outfile = sys.stdout

	try:
		counter = 0
		length = len(events)
		for day in events:
			events[day] = events[day].removesuffix("\n\n")
			print(day, ":\n\n", events[day], "\n", end="\n" if counter!=length-1 else "", sep="", file=outfile)
			counter += 1
	finally:
		if outfile != sys.stdout:
			outfile.close()

# MARK: Main
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

	if subcommand == "parse":
		subcommand_function = parse
	if subcommand == "schedule":
		subcommand_function = schedule

	subcommand_function(arguments)

if __name__ == "__main__":
	main()
