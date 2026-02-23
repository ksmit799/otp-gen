import unittest
import argparse
from src.util import getArgParser


class TestUtil(unittest.TestCase):

    def test_get_arg_parser_return_type(self):
        parser = getArgParser()
        self.assertIsInstance(parser, argparse.ArgumentParser)

    def test_get_arg_parser_default_values(self):
        parser = getArgParser()
        args = parser.parse_args([])
        self.assertEqual(args.language, "ts")
        self.assertEqual(args.out, "dist")
        self.assertEqual(args.notify_level, "INFO")
        self.assertIsNone(args.dc_files)

    def test_get_arg_parser_custom_values(self):
        parser = getArgParser()
        args = parser.parse_args(
            [
                "--language",
                "typescript",
                "--dc-files",
                "sample.dc",
                "sample2.dc",
                "build",
                "--notify-level",
                "ERROR",
            ]
        )
        self.assertEqual(args.language, "typescript")
        self.assertEqual(args.dc_files, ["sample.dc", "sample2.dc"])
        self.assertEqual(args.out, "build")
        self.assertEqual(args.notify_level, "ERROR")

    def test_get_arg_parser_bad_language_value(self):
        parser = getArgParser()
        with self.assertRaises(SystemExit):
            parser.parse_args(["--language", "python"])

    def test_get_arg_parser_bad_notify_level_value(self):
        parser = getArgParser()
        with self.assertRaises(SystemExit):
            parser.parse_args(["--notify-level", "DEBUG"])

    def test_get_arg_parser_bad_out_value_int(self):
        parser = getArgParser()
        with self.assertRaises(TypeError):
            parser.parse_args(["--out", 1])
