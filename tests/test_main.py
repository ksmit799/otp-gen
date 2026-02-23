import unittest
from unittest.mock import patch, MagicMock
import sys

from src.main import main


class TestMain(unittest.TestCase):

    @patch("src.main.getArgParser")
    @patch("src.main.DCLoader")
    @patch("src.main.sys.exit")
    def test_main_typescript_success(
        self, mock_exit, mock_dc_loader_cls, mock_get_arg_parser
    ):
        mock_args = MagicMock()
        mock_args.language = "typescript"
        mock_args.notify_level = "DEBUG"
        mock_args.dc_files = ["./samples/sample.dc"]
        mock_args.out = "dist"

        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = mock_args
        mock_get_arg_parser.return_value = mock_parser

        mock_gen_module = MagicMock()
        mock_gen_class = MagicMock()
        mock_gen_module.TypeScriptGenerator = mock_gen_class

        with patch.dict(
            sys.modules, {"gens.ts.type_script_generator": mock_gen_module}
        ):
            main()

        mock_exit.assert_not_called()

        mock_dc_loader_cls.return_value.read_dc_files.assert_called_once_with(
            ["./samples/sample.dc"]
        )

        mock_gen_class.assert_called_once_with(mock_dc_loader_cls.return_value, "dist")
        mock_gen_class.return_value.start.assert_called_once()

    @patch("src.main.getArgParser")
    @patch("src.main.sys.exit")
    def test_main_unsupported_language(self, mock_exit, mock_get_arg_parser):
        mock_args = MagicMock()
        mock_args.language = "python"
        mock_args.notify_level = "INFO"
        mock_args.dc_files = ["./samples/sample.dc"]
        mock_args.out = "dist"

        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = mock_args
        mock_get_arg_parser.return_value = mock_parser

        main()

        mock_exit.assert_called_once_with(1)
