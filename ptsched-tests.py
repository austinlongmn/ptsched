#!/usr/bin/env python3
import unittest
import json
import os
import sys
import io

import ptsched

class Test_ptsched(unittest.TestCase):
	def test_parser(self):
		for (input_filename, expected_output_filename) in self.get_input_and_expected_outputs("ast.json", "24"):
			with open(input_filename) as input_file, open(expected_output_filename) as expected_output_file:
				self.assertEqual(
					json.loads(json.dumps(ptsched.parse_file(input_file), default=str)),
					json.load(expected_output_file), msg="File %s failed the AST test." % input_filename
				)
	
	def test_final_results(self):
		for output_type in ["normal", "md"]:
			for (input_filename, expected_output_filename) in self.get_input_and_expected_outputs("out.txt", "24", output_type):
				with open(expected_output_filename) as expected_output_file:
					output_arg = "-m" if output_type == "md" else "-n"
					ptsched.parse(["-o", "temp_test_result", input_filename, output_arg])
					with open("temp_test_result") as result:
						self.assertEqual(result.read(), expected_output_file.read(), msg="File %s failed the final results test." % input_filename)
		os.remove("temp_test_result")

	def test_throws(self):
		for (input_filename, expected_output_filename) in self.get_input_and_expected_outputs("error.txt", "throwing"):
			with open(expected_output_filename) as expected_error_file, open(input_filename) as input_file:
				error_details = expected_error_file.read()
				split = error_details.splitlines()
				error_type = split[0]
				error_message = split[1]
				if error_type == "PTSchedParseException":
					error = ptsched.PTSchedParseException
				elif error_type == "PTSchedValidationException":
					error = ptsched.PTSchedValidationException
				
				with self.assertRaises(error) as cm:
					ptsched.parse_file(input_file)

				self.assertEqual(str(cm.exception), str(error(error_message)))

	def get_input_and_expected_outputs(self, suffix, criteria, output_type="normal"):
		result = []
		for (dir, _, files) in os.walk("test-data/input"):
			if "expected-output" in dir or "out" in dir or not criteria in dir:
				continue
			for file in files:
				if not "ptsched" in file:
					continue
				input_filename = dir + "/" + file
				test_directory = f"{dir.replace("input/", f"expected-output-{output_type}/")}/{file}/{suffix}"
				result.append((input_filename, test_directory))
		self.assertNotEqual(len(result), 0)
		return result
	
	def test_schedule(self):
		os.chdir("dev/test-environment")
		try:
			if os.path.exists(".ptscheddir"):
				os.unlink(".ptscheddir")
			ptsched.init([])
			ptsched.schedule(["--no-vcs", "--quiet"])
		finally:
			os.chdir("../..")

if __name__ == "__main__":
	unittest.main()
