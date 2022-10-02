import os
import shutil
from pathlib import Path

from src.generator_interface import GeneratorInterface
from src.notifier import notify
from gens.ts.dc_interface_ts import DCInterfaceTS
from gens.ts.remote_interface_ts import RemoteInterfaceTS
from gens.ts.remote_ts import RemoteTS
from gens.ts.object_init_ts import ObjectInitTS
from gens.ts.function_parsing_ts import FunctionParsingTS
from gens.ts.mapping_ts import MappingTS


class TypeScriptGenerator(GeneratorInterface):
    notify = notify.new_category("TypeScriptGenerator")

    def start(self):
        self.notify.info("Configured generator for typescript...")

        self.generate_dc_interfaces()
        self.generate_remote_interfaces()
        self.generate_remotes()
        self.generate_object_init()
        self.generate_function_parsing()
        self.generate_mapping()
        self.copy_static_files()

        self.notify.info(f"Finished building!")

    def generate_dc_interfaces(self):
        """
        Generates all the distributed class interfaces.
        This includes structs.
        :return:
        """
        self.notify.info("Generating DC interfaces...")

        out_path = Path().absolute() / self.outDir / "generated/dc"
        out_path.mkdir(parents=True, exist_ok=True)

        for name, dclass in self.dc_loader.dclasses_by_name.items():
            interface = DCInterfaceTS(name, dclass, out_path)
            interface.write()
            self.notify.debug(f"Wrote interface class '{name}'")

        self.notify.info("Done!")

    def generate_remote_interfaces(self):
        self.notify.info("Generating remote interfaces...")

        out_path = Path().absolute() / self.outDir / "generated/iremote"
        out_path.mkdir(parents=True, exist_ok=True)

        for name, dclass in self.dc_loader.dclasses_by_name.items():
            if dclass.isStruct():
                continue

            interface = RemoteInterfaceTS(name, dclass, out_path)
            interface.write()

        self.notify.info("Done!")

    def generate_remotes(self):
        self.notify.info("Generating remotes...")

        out_path = Path().absolute() / self.outDir / "generated/remote"
        out_path.mkdir(parents=True, exist_ok=True)

        for name, dclass in self.dc_loader.dclasses_by_name.items():
            if dclass.isStruct():
                continue

            remote = RemoteTS(name, dclass, out_path)
            remote.write()

        self.notify.info("Done!")

    def generate_object_init(self):
        self.notify.info("Generating object initialization...")

        out_path = Path().absolute() / self.outDir / "generated/fn"
        out_path.mkdir(parents=True, exist_ok=True)

        obj = ObjectInitTS(self.dc_loader, out_path)
        obj.write()

        self.notify.info("Done!")

    def generate_function_parsing(self):
        self.notify.info("Generating function parsing...")

        out_path = Path().absolute() / self.outDir / "generated/fn"
        out_path.mkdir(parents=True, exist_ok=True)

        func = FunctionParsingTS(self.dc_loader, out_path)
        func.write()

        self.notify.info("Done!")

    def generate_mapping(self):
        self.notify.info("Generating mapping...")

        out_path = Path().absolute() / self.outDir / "generated/fn"
        out_path.mkdir(parents=True, exist_ok=True)

        mapping = MappingTS(self.dc_loader, out_path)
        mapping.write()

        self.notify.info("Done!")

    def copy_static_files(self):
        self.notify.info("Copying static files...")

        out_path = Path().absolute() / self.outDir / "otp"
        if os.path.exists(out_path) and os.path.isdir(out_path):
            # Clean any existing static files.
            shutil.rmtree(out_path)

        shutil.copytree("./gens/ts/static", out_path)

        self.notify.info("Done!")
