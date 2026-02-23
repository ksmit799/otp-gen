import sys

from src.dc_loader import DCLoader
from src.notifier import notify, LoggingNotifier
from src.util import getArgParser


def main():
    args = getArgParser().parse_args()

    LoggingNotifier.notifyLevel = args.notify_level
    main_notify = notify.new_category("Main")

    if args.language not in ("ts", "typescript"):
        main_notify.error(f"Unimplemented generator for language '{args.language}'")
        sys.exit(1)

    from gens.ts.type_script_generator import TypeScriptGenerator as Generator

    dc_loader = DCLoader()
    dc_loader.read_dc_files(args.dc_files)

    main_notify.info(f"Build directory path: {args.out}")

    Generator(dc_loader, args.out).start()


if __name__ == "__main__":
    main()
