import argparse
import sys

from src.notifier import notify, LoggingNotifier
from src.dc_loader import DCLoader


if __name__ == "__main__":
    # Parse CLI args.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--language",
        choices=["ts", "typescript"],
        help="The language of the generated files.",
    )
    parser.add_argument(
        "--dc-files",
        nargs="*",
        help="An array of DC file paths to be loaded.",
    )
    parser.add_argument(
        "--out",
        default="dist",
        help="The path to output generated files.",
    )
    parser.add_argument(
        "--notify-level",
        choices=["INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Notify level.",
    )

    args = parser.parse_args()

    # Set our global notify level.
    LoggingNotifier.notifyLevel = args.notify_level
    notify = notify.new_category("Main")

    # Import the correct generator for the specified language.
    if args.language in ("ts", "typescript"):
        from gens.ts.type_script_generator import TypeScriptGenerator as Generator
    else:
        notify.error(f"Unimplemented generator for language '{args.language}'")
        sys.exit(1)

    # Load DC files.
    dc_loader = DCLoader()
    dc_loader.read_dc_files(args.dc_files)

    notify.info(f"Build directory path: {args.out}")

    # Start the generator!
    generator = Generator(dc_loader, args.out)
    generator.start()
