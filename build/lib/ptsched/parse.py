import argparse
import sys
import json

from .utils import *

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
