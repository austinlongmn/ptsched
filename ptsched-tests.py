#!/usr/bin/env python3
import unittest
import json
import os
import signal
import subprocess
import time

import ptsched

class Test_ptsched(unittest.TestCase):
	def test_helper(self):
		signal.alarm(3)
		helper = subprocess.Popen("out/bin/ptsched-event-helper", stdin=subprocess.PIPE, stdout=subprocess.PIPE)
		id = 0
		queryStartDate = "2024-08-26"
		queryEndDate = "2024-08-30"
		request = "QUERY:" + json.dumps({
			"id": id,
			"queryStartDate": queryStartDate,
			"queryEndDate": queryEndDate
		}) + "\n"
		helper.stdin.write(request.encode())
		helper.stdin.flush()
		result = helper.stdout.readline()
		self.assertDictEqual(json.loads(result), {
			"id": id,
			"eventIdentifiers": {
				"2024-08-26": "74E9AB48-60A7-4CF4-BFDD-08717FFC3B9E:8148FDC0-45E2-4716-B1C8-733C6D1A2CFD",
				"2024-08-27": "74E9AB48-60A7-4CF4-BFDD-08717FFC3B9E:DB093BDD-275D-41E6-9742-C84F253B2BA8",
				"2024-08-28": "74E9AB48-60A7-4CF4-BFDD-08717FFC3B9E:8B6A9A7B-D656-4000-8CCE-694AE440E1DD",
				"2024-08-29": "74E9AB48-60A7-4CF4-BFDD-08717FFC3B9E:54291713-37A0-4C89-B917-25AF38B1976E",
				"2024-08-30": "74E9AB48-60A7-4CF4-BFDD-08717FFC3B9E:AF40C127-AECF-4F60-BF5F-EDC7088F7246"
			}
		})
		id += 1
		print("testing update")

		request = "UPDATE:" + json.dumps({
			"id": id,
			"eventIdentifier": "74E9AB48-60A7-4CF4-BFDD-08717FFC3B9E:8148FDC0-45E2-4716-B1C8-733C6D1A2CFD",
			"contents": "Test at %f" % time.time()
		})
		result = helper.stdout.readline()
		obj_result = json.loads(result)
		self.assertTrue(obj_result["id"] == id)
		print(obj_result)
		id += 1

		helper.stdin.close()
		helper.stdout.close()
		helper.wait()
		signal.alarm(0)
	
	def test_parser(self):
		for (input_filename, expected_output_filename) in self.get_input_and_expected_outputs("ast.json", "24"):
			with open(input_filename) as input_file, open(expected_output_filename) as expected_output_file:
				self.assertEqual(
					json.loads(json.dumps(ptsched.parse_file(input_file), default=str)),
					json.load(expected_output_file), msg="File %s failed the AST test." % input_filename
				)
	
	def test_final_results(self):
		for (input_filename, expected_output_filename) in self.get_input_and_expected_outputs("out.txt", "24"):
			with open(expected_output_filename) as expected_output_file:
				ptsched.parse(["-o", "temp_test_result", input_filename])
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

	def get_input_and_expected_outputs(self, suffix, criteria):
		result = []
		for (dir, _, files) in os.walk("test-data/input"):
			if "expected-output" in dir or "out" in dir or not criteria in dir:
				continue
			for file in files:
				if not "ptsched" in file:
					continue
				input_filename = dir + "/" + file
				test_directory = "%s%s%s%s%s" % (dir.replace("input/", "expected-output/"), "/", file, "/", suffix)
				result.append((input_filename, test_directory))
		self.assertNotEqual(len(result), 0)
		return result

if __name__ == "__main__":
	unittest.main()
