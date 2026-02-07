import os
import shutil
from pathlib import Path

from src.generator_interface import GeneratorInterface
from src.notifier import notify
from gens.ts.dc_interface_ts import DCInterfaceTS
from gens.ts.remote_interface_ts import RemoteInterfaceTS
from gens.ts.remote_ts import RemoteTS
from gens.ts.struct_parsing_ts import StructParsingTS
from gens.ts.object_init_ts import ObjectInitTS
from gens.ts.function_parsing_ts import FunctionParsingTS
from gens.ts.mapping_ts import MappingTS


class TypeScriptGenerator(GeneratorInterface):
    notify = notify.new_category("TypeScriptGenerator")

    def start(self):
        self.notify.info("Configured generator for typescript...")

        self.cleanup_out_dir()

        # Client (CL) specific generations.
        if self.context in ["cl", "both"]:
            self.generate_dc_interfaces()
            self.generate_remote_interfaces()
            self.generate_remotes()
            self.generate_struct_parsing()
            self.generate_object_init()
            self.generate_function_parsing()
            self.generate_mapping()

        # Server (AI/UD) specific generations.
        if self.context in ["ai", "both"]:
            self.generate_dclasses()

        self.copy_static_files()

        self.notify.info(f"Finished building!")

    def cleanup_out_dir(self):
        out_path = Path().absolute() / self.outDir / "generated"
        if os.path.exists(out_path) and os.path.isdir(out_path):
            # Clean any existing build files.
            shutil.rmtree(out_path)

    def generate_dc_interfaces(self):
        """
        Generates interfaces for all the distributed classes (including structs).
        These will contain the typings for *all* of the dclass fields,
        both fields the client can send and ones it can receive.
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
        """
        Generates interfaces for all the distributed classes, excluding structs.
        These will contain the typings for only fields marked clsend/ownsend.
        :return:
        """
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
        """
        Generates "remote" classes based on the previously generated remote interfaces
        that implement the actual packing of datagrams to be sent on the wire.
        :return:
        """
        self.notify.info("Generating remotes...")

        out_path = Path().absolute() / self.outDir / "generated/remote"
        out_path.mkdir(parents=True, exist_ok=True)

        for name, dclass in self.dc_loader.dclasses_by_name.items():
            if dclass.isStruct():
                continue

            remote = RemoteTS(name, dclass, out_path)
            remote.write()

        self.notify.info("Done!")

    def generate_struct_parsing(self):
        """
        Generates functions used to parse structs defined in our dc files.
        :return:
        """
        self.notify.info("Generating struct parsing...")

        out_path = Path().absolute() / self.outDir / "generated/fn"
        out_path.mkdir(parents=True, exist_ok=True)

        struct = StructParsingTS(self.dc_loader, out_path)
        struct.write()

        self.notify.info("Done!")

    def generate_object_init(self):
        """
        Generates functions to parse/initialize distributed objects coming into our view.
        These will be fields marked required/ownrecv.
        :return:
        """
        self.notify.info("Generating object initialization...")

        out_path = Path().absolute() / self.outDir / "generated/fn"
        out_path.mkdir(parents=True, exist_ok=True)

        obj = ObjectInitTS(self.dc_loader, out_path)
        obj.write()

        self.notify.info("Done!")

    def generate_function_parsing(self):
        """
        Generates function to parse distributed object field updates coming from the server.
        :return:
        """
        self.notify.info("Generating function parsing...")

        out_path = Path().absolute() / self.outDir / "generated/fn"
        out_path.mkdir(parents=True, exist_ok=True)

        func = FunctionParsingTS(self.dc_loader, out_path)
        func.write()

        self.notify.info("Done!")

    def generate_mapping(self):
        """
        Generates a static mapping between distributed object class/field IDs to the functions
        we have previously generated.
        :return:
        """
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
