#!/usr/bin/env python3
import unittest
import json
import os
import sys
import io

import ptsched

class Test_ptsched(unittest.TestCase):
	def test_parser(self):
		for (input_filename, expected_output_filename) in self.get_input_and_expected_outputs("ast.json"):
			with open(input_filename) as input_file, open(expected_output_filename) as expected_output_file:
				self.assertEqual(json.loads(json.dumps(ptsched.parse_file(input_file), default=str)), json.load(expected_output_file), msg="File %s failed the AST test." % input_filename)
	
	def test_final_results(self):
		for (input_filename, expected_output_filename) in self.get_input_and_expected_outputs("out.txt"):
			with open(expected_output_filename) as expected_output_file:
				recovery_stdout = sys.stdout
				strIO = io.StringIO()
				ptsched.parse(["-o", "temp_test_result", input_filename])
				with open("temp_test_result") as result:
					self.assertEqual(result.read(), expected_output_file.read(), msg="File %s failed the final results test." % input_filename)
		os.remove("temp_test_result")


	def get_input_and_expected_outputs(self, suffix):
		result = []
		for (dir, _, files) in os.walk("test-workspace"):
			if "expected-output" in dir or "out" in dir:
				continue
			for file in files:
				if not "ptsched" in file:
					continue
				input_filename = dir + "/" + file
				test_directory = "%s%s%s%s%s" % (dir.replace("test-workspace/", "test-workspace/expected-output/"), "/", file, "/", suffix)
				result.append((input_filename, test_directory))
		return result

if __name__ == "__main__":
	unittest.main()
