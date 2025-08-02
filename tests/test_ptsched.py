#!/usr/bin/env python
import unittest
import os

from ptsched.parse import parse


class Test_ptsched(unittest.TestCase):
    def test_final_results(self):
        for output_type in ["normal", "md"]:
            for (
                input_filename,
                expected_output_filename,
            ) in self.get_input_and_expected_outputs("out.txt", "24", output_type):
                with open(expected_output_filename) as expected_output_file:
                    (
                        parse(
                            output="temp_test_result",
                            filename=input_filename,
                            normal=True,
                        )
                        if output_type == "normal"
                        else parse(
                            output="temp_test_result",
                            filename=input_filename,
                            markdown=True,
                        )
                    )
                    with open("temp_test_result") as result:
                        self.assertEqual(
                            result.read(),
                            expected_output_file.read(),
                            msg="File %s failed the final results test."
                            % input_filename,
                        )
        os.remove("temp_test_result")

    def get_input_and_expected_outputs(self, suffix, criteria, output_type="normal"):
        result = []
        for dir, _, files in os.walk("tests/test_data/input"):
            if "expected-output" in dir or "out" in dir or criteria not in dir:
                continue
            for file in files:
                if "ptsched" not in file:
                    continue
                input_filename = dir + "/" + file
                replaced = dir.replace("input/", f"expected-output-{output_type}/")
                test_directory = f"{replaced}/{file}/{suffix}"
                result.append((input_filename, test_directory))
        self.assertNotEqual(len(result), 0)
        return result


if __name__ == "__main__":
    unittest.main()
