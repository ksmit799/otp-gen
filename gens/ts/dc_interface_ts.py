from src.notifier import notify
from gens.ts.constants_ts import GENERATED_FILE_HEADER
from gens.ts.util_ts import (
    get_ts_type_for_subatomic_type,
    format_ts_params_for_atomic_field,
    write_generated_file,
)
from src.util import is_server_field

struct_template = """{header}
{imports}
export default class {className} {{
{fields}
}}
"""

class_template = """{header}
{imports}
export default interface I{className}{extends} {{
{fields}
}}
"""


class DCInterfaceTS:
    notify = notify.new_category("DCInterfaceTS")

    def __init__(self, name, dclass, out_path):
        self.name = name
        self.dclass = dclass
        self.outPath = out_path
        self.outName = ""
        self.outBuffer = ""

        if dclass.isStruct():
            self._gen_struct_buffer()
        else:
            self._gen_class_buffer()

    def _gen_struct_buffer(self):
        self.outName = f"{self.name}.ts"

        imports = ""
        existing_imports = set()

        fields = ""
        for i in range(self.dclass.get_num_fields()):
            field = self.dclass.get_field(i)
            dc_parameter = field.asParameter()
            if not dc_parameter:
                self.notify.warning(
                    f"Got non parameter field in struct: {self.name} - {field.getName()}"
                )
                continue

            fields += f"\tpublic {field.getName()}!: "

            dc_param_simple = dc_parameter.asSimpleParameter()
            dc_param_class = dc_parameter.asClassParameter()
            dc_param_array = dc_parameter.asArrayParameter()

            if dc_param_simple:
                # We have a simple generic type parameter.
                fields += (
                    f"{get_ts_type_for_subatomic_type(dc_param_simple.getType())};\n"
                )
            elif dc_param_class:
                # We have a singular class parameter.
                class_name = dc_param_class.getClass().getName()
                if class_name not in existing_imports:
                    imports += f'import {class_name} from "./{class_name}";\n'
                    existing_imports.add(class_name)

                fields += f"{class_name};\n"
            else:
                # We have an array of *something*.
                elem_param_simple = dc_param_array.getElementType().asSimpleParameter()
                elem_param_class = dc_param_array.getElementType().asClassParameter()

                if elem_param_class:
                    # We have an array of classes.
                    class_name = elem_param_class.getClass().getName()
                    if class_name not in existing_imports:
                        imports += f'import {class_name} from "./{class_name}";\n'
                        existing_imports.add(class_name)

                    fields += f"{class_name}[];\n"
                else:
                    # We have an array of generic types.
                    fields += f"{get_ts_type_for_subatomic_type(elem_param_simple.getType())}[];\n"

        if fields:
            # Chop off our last char (\n)
            fields = fields[:-1]

        self.outBuffer = struct_template.format(
            header=GENERATED_FILE_HEADER,
            className=self.name,
            imports=imports,
            fields=fields,
        )

    def _gen_class_buffer(self):
        self.outName = f"I{self.name}.ts"

        imports = ""
        extends = ""
        existing_imports = set()

        if self.dclass.get_num_parents():
            # This distributed class inherits from at least one parent.
            extends = " extends "
            for i in range(self.dclass.get_num_parents()):
                parent = self.dclass.get_parent(i)
                name = f"I{parent.getName()}"  # Prepend with an 'I'
                imports += f'import {name} from "./{name}";\n'
                extends += f"{name}, "

            # Chop off our last two chars (, )
            extends = extends[:-2]

        fields = ""
        for i in range(self.dclass.get_num_fields()):
            field = self.dclass.get_field(i)
            atomic_field = field.asAtomicField()
            # TODO: DC parameters.
            if not atomic_field:
                self.notify.warning(
                    f"Got non atomic field {self.name} - {field.getName()}"
                )
                continue

            # Don't include server-only fields.
            # Clients should never interact with these.
            if is_server_field(field):
                continue

            params, new_imports = format_ts_params_for_atomic_field(
                atomic_field, "./", existing_imports, notify=self.notify
            )
            imports += new_imports
            fields += f"\t{field.getName()}({params}): void;\n"

        if fields:
            # Chop off our last char (\n)
            fields = fields[:-1]

        self.outBuffer = class_template.format(
            header=GENERATED_FILE_HEADER,
            className=self.name,
            imports=imports,
            extends=extends,
            fields=fields,
        )

    def write(self):
        if self.outName and self.outBuffer:
            write_generated_file(self.outPath, self.outName, self.outBuffer)
