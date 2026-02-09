import os
import shutil
from pathlib import Path

from gens.ts.struct_packing_ts import StructPackingTS
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
            self.generate_struct_packing()
            self.generate_object_init()
            self.generate_function_parsing()
            self.generate_mapping()

        # Server (AI/UD) specific generations.
        if self.context in ["ai", "both"]:
            # self.generate_dclasses()
            pass

        self.copy_static_files()

        self.notify.info(f"Finished building!")

    def cleanup_out_dir(self):
        out_path = Path().absolute() / self.outDir / "generated"
        if os.path.exists(out_path) and os.path.isdir(out_path):
            shutil.rmtree(out_path)

    def _out_path(self, subdir):
        path = Path().absolute() / self.outDir / "generated" / subdir
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _run_per_class(
        self, step_name, subdir, writer_class, skip_structs=False, debug_each=False
    ):
        self.notify.info(step_name)
        out_path = self._out_path(subdir)
        for name, dclass in self.dc_loader.dclasses_by_name.items():
            if skip_structs and dclass.isStruct():
                continue
            writer_class(name, dclass, out_path).write()
            if debug_each:
                self.notify.debug(f"Wrote '{name}'")
        self.notify.info("Done!")

    def _run_single(self, step_name, subdir, writer_class, **writer_kwargs):
        self.notify.info(step_name)
        out_path = self._out_path(subdir)
        writer_class(self.dc_loader, out_path, **writer_kwargs).write()
        self.notify.info("Done!")

    def generate_dc_interfaces(self):
        """Interfaces for all distributed classes (including structs)."""
        self._run_per_class(
            "Generating DC interfaces...",
            "dc",
            DCInterfaceTS,
            skip_structs=False,
            debug_each=True,
        )

    def generate_remote_interfaces(self):
        """Interfaces for non-struct classes, typings for clsend/ownsend only."""
        self._run_per_class(
            "Generating remote interfaces...",
            "iremote",
            RemoteInterfaceTS,
            skip_structs=True,
        )

    def generate_remotes(self):
        """Remote classes implementing datagram packing for clsend/ownsend."""
        self._run_per_class(
            "Generating remotes...",
            "remote",
            RemoteTS,
            skip_structs=True,
        )

    def generate_struct_parsing(self):
        """Functions to parse structs from DC files."""
        self._run_single(
            "Generating struct parsing...",
            "fn",
            StructParsingTS,
        )

    def generate_struct_packing(self):
        """Functions to pack structs into datagrams."""
        self._run_single(
            "Generating struct packing...",
            "fn",
            StructPackingTS,
        )

    def generate_object_init(self):
        """Functions to init distributed objects (required/ownrecv)."""
        self._run_single(
            "Generating object initialization...",
            "fn",
            ObjectInitTS,
        )

    def generate_function_parsing(self):
        """Functions to parse field updates from the server."""
        self._run_single(
            "Generating function parsing...",
            "fn",
            FunctionParsingTS,
        )

    def generate_mapping(self):
        """Static mapping from class/field IDs to generated functions."""
        self._run_single(
            "Generating mapping...",
            "fn",
            MappingTS,
        )

    def copy_static_files(self):
        self.notify.info("Copying static files...")

        out_path = Path().absolute() / self.outDir / "otp"
        if os.path.exists(out_path) and os.path.isdir(out_path):
            # Clean any existing static files.
            shutil.rmtree(out_path)

        shutil.copytree("./gens/ts/static", out_path)

        self.notify.info("Done!")
