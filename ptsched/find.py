import argparse
import json

from .utils import *

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
