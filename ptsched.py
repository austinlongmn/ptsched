#!/usr/bin/env python3
import argparse
import re
import datetime
import os
import sys
import uuid
import json
import subprocess
import multiprocessing
import time
import pathlib

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

config_path = str(pathlib.Path.home().joinpath(".ptschedconfig"))

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

# MARK: init
def init(arguments):
	schedule_argument_parser = argparse.ArgumentParser("ptsched init", description="Initialize a ptsched directory")
	schedule_argument_parser.add_argument("-s", "--set-default", action="store_true", help="Sets the directory as the default ptsched directory for the user. A new ptsched directory will not be created.")
	args = schedule_argument_parser.parse_args(arguments)

	if args.set_default:
		try:
			with open(config_path) as r_file:
				config = json.load(r_file)
		except FileNotFoundError:
			config = {}
		config["defaultDirectory"] = str(pathlib.Path.cwd())
		with open(config_path, "w") as w_file:
			json.dump(config, w_file)
		return

	try:
		with open(".ptscheddir", 'x') as directory_file:
			ptsched_directory = {}
			directory_id = uuid.uuid4().hex.upper()
			ptsched_directory["directoryID"] = directory_id
			ptsched_directory["files"] = []

			update_directory(ptsched_directory)
			
			json.dump(ptsched_directory, directory_file)
	except FileExistsError as error:
		print("A ptsched directory already exists in this folder.", file=sys.stderr)
		exit(17)

def scan(dir=str(pathlib.Path.cwd())):
	result = []
	path = pathlib.Path(dir)
	for (directory, dirs, files) in os.walk(str(path)):
		if ".ptschedignore" in files:
			continue
		for file in files:
			if file.endswith(".ptsched"):
				result.append(str(pathlib.Path(directory).joinpath(file)))
	return result

# MARK: find
def find(arguments):
	find_argument_parser = argparse.ArgumentParser("ptsched find", description="Finds the default ptsched file for new additions")
	find_argument_parser.add_argument("-d", "--directory", help="Gives the directory instead of the file")
	args = find_argument_parser.parse_args(arguments)

	try:
		with open(config_path) as config_file:
			config = json.load(config_file)
			ptsched_directory = config["defaultDirectory"]

			if args.directory:
				print(ptsched_directory)
				return
		
			results = {}
			for filename in scan(ptsched_directory):
				with open(filename) as file:
					result = {}
					parse_dates(file.readline(), result, 1)
					date = datetime.datetime.now().timestamp()
					time = datetime.datetime.min.time()
					start_date = datetime.datetime.combine(result["start_date"], time).timestamp()
					end_date = datetime.datetime.combine(result["end_date"], time).timestamp()
					interval1 = abs(start_date - date)
					interval2 = abs(end_date - date)
					results[filename] = min(interval1, interval2)
			
			def convert(key):
				return results[key]

			print(min(results.keys(), key=convert))

						
	except FileNotFoundError:
		print("No ptsched configuration has been set. Run\n\n\tptsched --set-default\n\nin your directory of choice.")

# MARK: schedule
def schedule(arguments):
	schedule_argument_parser = argparse.ArgumentParser("ptsched schedule", description="Schedules changed .ptsched files into your calendar via syscal")
	schedule_argument_parser.add_argument("-q", "--quiet", action="store_true", help="Do not output extra information")
	schedule_argument_parser.add_argument("--no-vcs", action="store_true", help="Do not commit changes to version control")
	args = schedule_argument_parser.parse_args(arguments)

	try:
		with open(".ptscheddir") as directory_file:
			directory_info = json.load(directory_file)
	except FileNotFoundError:
		print("No initialized ptsched directory.", file=sys.stderr)
		exit(1)

	update_directory(directory_info)

	files = directory_info["files"]
	c_args = []
	for idx in range(0, len(files)):
		c_args.append((
			files[idx]["filename"],
			files[idx]["lastScheduled"],
			idx,
			args.quiet
		))

	with multiprocessing.Pool(5) as pool:
		result = pool.map(syscal_if_needed, c_args)
	
	did_change_files = False
	for file_results in result:
		if file_results[0] != None:
			files[file_results[1]]["lastScheduled"] = time.time()
			did_change_files = True
	
	if did_change_files and not args.no_vcs:
		os.system("git add \\*.ptsched")
		os.system("git commit -m \"Schedule edit at %s\"" % datetime.datetime.now().strftime('%a %d %b %Y, %I:%M %p'))
	
	with open(".ptscheddir", "w") as directory_file:
		json.dump(directory_info, directory_file)

def syscal_if_needed(file_info_and_id): # (filename, schedule date, id)
	if file_info_and_id[1] == None or os.path.getmtime(file_info_and_id[0]) > float(file_info_and_id[1]):
		if not file_info_and_id[3]:
			print("ptsched syscal", file_info_and_id[0])
		syscal([file_info_and_id[0]])
		return (time.time(), file_info_and_id[2])
	return (None, file_info_and_id[2])

def update_directory(current):
	files = set(scan())
	new = files.difference([x["filename"] for x in current["files"]])
	for file in new:
		current["files"].append({
			"filename": file,
			"lastScheduled": None
		})

# MARK: syscal
def syscal(arguments):
	schedule_argument_parser = argparse.ArgumentParser("ptsched syscal", description="Launches a helper program to write ptsched schedules to the system calendar")
	schedule_argument_parser.add_argument("filename", help="The schedule file to use")
	args = schedule_argument_parser.parse_args(arguments)

	output_tmp_filename = tmp_filename()
	parse(["-o", output_tmp_filename, args.filename])
	with open(output_tmp_filename) as file:
		parse_output = file.read()
	os.remove(output_tmp_filename)

	days = re.finditer(r"(\d{4}-\d{2}-\d{2}):\n\n((?:.(?!\d{4}-\d{2}-\d{2}:\n\n))+)", parse_output, re.DOTALL)

	writing_subprocess = subprocess.Popen("ptsched-event-helper", stdin=subprocess.PIPE, stdout=subprocess.PIPE)
	id = 0
	for day in days:
		write_to_calendar(id, day[1], day[2], writing_subprocess.stdin)
		id += 1

	writing_subprocess.stdin.flush()
	writing_subprocess.stdin.close()
	writing_subprocess.wait()
	
def write_to_calendar(id, date, contents, subprocess_input):
	subprocess_input.write(("%d\nUPDATE\n%s\n%s\nEND REQUEST\n" % (id, date, contents.removesuffix("\n"))).encode())
	subprocess_input.flush()

def tmp_filename():
	return subprocess.check_output(["mktemp", "-t", "ptsched"]).decode("utf-8").removesuffix("\n")

def parse_dates(line, result, lineno):
	"""
	parse the contents of line as a date range

	line -- the line contents of the file containing the date range
	result -- the result - this will be modified by the function
	lineno -- the line number for diagnostic messages

	This function parses the contents of line and puts the results into result.
	Upon successful completion, result["start_date"] and result["end_date"] will
	be set to the parsed values (datetime.datetime objects).
	"""
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
		if (re.match(r"^\d{4}-\d{2}-\d{2}:$", line)):
			raise PTSchedParseException("Putting dates in this format with a colon at the end of the line could cause conflicts: line %d" % lineno)
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
	output_group = parse_argument_parser.add_mutually_exclusive_group()
	output_group.add_argument("-a", "--ast", action="store_true", help="Outputs the abstract syntax tree of the file")
	output_group.add_argument("-c", "--list-courses", action="store_true", help="List courses in the file")
	output_group.add_argument("-y", "--list-days", action="store_true", help="List days in the file, output format is YYYY-MM-DD")
	output_group.add_argument("-j", "--json", action="store_true", help="Outputs in JSON format")
	output_group.add_argument("-m", "--markdown", action="store_true", help="Outputs in Markdown format")
	output_group.add_argument("-n", "--normal", action="store_true", help="Outputs in normal format (the default)", default=True)
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

	output_filename = args.output
	if output_filename != None:
		try:
			outfile = open(output_filename, mode="w")
		except OSError as error:
			print("Error when opening file:", error, file=sys.stderr)
			exit(1)
	else:
		outfile = sys.stdout

	if args.ast:
		json.dump(schedule, outfile, default=str, indent=2)
		return
	if args.list_courses:
		for course in schedule["courses"]:
			print(course, file=outfile)
		return

	if args.dry_run: return

	result = {}
	for course in sorted(schedule["courses"].keys()):
		for day in sorted(schedule["courses"][course].keys()):
			if (not (day in result.keys())):
				result[day] = {}
			if (not (course in result[day].keys())):
				result[day][course] = []
			for task in schedule["courses"][course][day]:
				result[day][course].append(task)

	if args.json:
		json.dump(result, outfile, default=str, indent="\t")
		return

	if args.list_days:
		for day in result:
			print(day, file=outfile)
		return
	
	if args.markdown:
		output_markdown(result, outfile)
		return
	elif args.normal:
		output_default(result, outfile)
		return

def output_default(result, outfile):
	try:
		counter = 0
		sorted_days = sorted(result.keys())
		length = len(sorted_days)
		for day in sorted_days:
			print(day + ":\n", file=outfile)

			sorted_courses = sorted(result[day].keys())
			counter2 = 0
			length2 = len(sorted_courses)
			for course in sorted_courses:
				print(course + ":", file=outfile)
				for task in result[day][course]:
					print(task, file=outfile)
				if not (counter >= length-1 and counter2 >= length2-1):
					print(file=outfile)
				counter2 += 1
			counter += 1
	finally:
		if outfile != sys.stdout:
			outfile.close()

def output_markdown(result, outfile):
	try:
		counter = 0
		sorted_days = sorted(result.keys())
		length = len(sorted_days)
		for day in sorted_days:
			print("# Tasks: " + day + "\n", file=outfile)

			sorted_courses = sorted(result[day].keys())
			counter2 = 0
			length2 = len(sorted_courses)
			for course in sorted_courses:
				print("## " + course + "\n", file=outfile)
				for task in result[day][course]:
					print("- [ ] " + task, file=outfile)
				if not (counter >= length-1 and counter2 >= length2-1):
					print(file=outfile)
				counter2 += 1
			counter += 1
	finally:
		if outfile != sys.stdout:
			outfile.close()

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

	subcommands[subcommand](arguments)

if __name__ == "__main__":
	main()
