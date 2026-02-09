from src.notifier import notify
from gens.ts.constants_ts import GENERATED_FILE_HEADER
from gens.ts.util_ts import format_ts_params_for_atomic_field, write_generated_file

template = """{header}
{imports}
export default interface IR{className}{extends} {{
{fields}
}}
"""


class RemoteInterfaceTS:
    notify = notify.new_category("RemoteInterfaceTS")

    def __init__(self, name, dclass, out_path):
        self.name = name
        self.dclass = dclass
        self.outPath = out_path
        self.outName = ""
        self.outBuffer = ""

        self._gen_buffer()

    def _gen_buffer(self):
        self.outName = f"IR{self.name}.ts"

        imports = ""
        extends = ""
        existing_imports = set()

        if self.dclass.get_num_parents():
            # This distributed class inherits from at least one parent.
            extends = " extends "
            for i in range(self.dclass.get_num_parents()):
                parent = self.dclass.get_parent(i)
                name = f"IR{parent.getName()}"  # Prepend with an 'IR'
                imports += f'import {name} from "./{name}";\n'
                extends += f"{name}, "

            # Chop off our last two chars (, )
            extends = extends[:-2]

        fields = ""
        for i in range(self.dclass.get_num_fields()):
            field = self.dclass.get_field(i)
            if not field.isClsend() and not field.isOwnsend():
                # Skip fields that aren't sendable.
                continue

            atomic_field = field.asAtomicField()
            if not atomic_field:
                continue

            params, new_imports = format_ts_params_for_atomic_field(
                atomic_field, "../dc/", existing_imports, notify=self.notify
            )
            imports += new_imports
            fields += f"\t{field.getName()}({params}): void;\n"

        if fields:
            # Chop off our last char (\n)
            fields = fields[:-1]

        self.outBuffer = template.format(
            header=GENERATED_FILE_HEADER,
            className=self.name,
            imports=imports,
            extends=extends,
            fields=fields,
        )

    def write(self):
        if self.outName and self.outBuffer:
            write_generated_file(self.outPath, self.outName, self.outBuffer)
