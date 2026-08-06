from src.notifier import notify
from gens.ts.constants_ts import GENERATED_FILE_HEADER
from gens.ts.util_ts import (
    get_ts_type_for_subatomic_type,
    format_ts_params_for_atomic_field,
    write_generated_file,
)

struct_template = """{header}
{imports}
export default class {className} {{
{fieldDeclarations}

    constructor(
{constructorParams}
    ) {{
{constructorAssignments}
    }}
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
        field_declarations = []
        constructor_params = []
        constructor_assignments = []

        for i in range(self.dclass.get_num_fields()):
            field = self.dclass.get_field(i)
            dc_parameter = field.asParameter()
            if not dc_parameter:
                self.notify.warning(
                    f"Got non parameter field in struct: {self.name} - {field.getName()}"
                )
                continue

            param_name = field.getName()
            dc_param_simple = dc_parameter.asSimpleParameter()
            dc_param_class = dc_parameter.asClassParameter()
            dc_param_array = dc_parameter.asArrayParameter()

            if dc_param_simple:
                ts_type = get_ts_type_for_subatomic_type(dc_param_simple.getType())
                field_declarations.append(f"\tpublic {param_name}!: {ts_type};")
                constructor_params.append(f"\t\t{param_name}: {ts_type}")
                constructor_assignments.append(f"\t\tthis.{param_name} = {param_name};")
            elif dc_param_class:
                class_name = dc_param_class.getClass().getName()
                if class_name not in existing_imports:
                    imports += f'import {class_name} from "./{class_name}";\n'
                    existing_imports.add(class_name)
                field_declarations.append(f"\tpublic {param_name}!: {class_name};")
                constructor_params.append(f"\t\t{param_name}: {class_name}")
                constructor_assignments.append(f"\t\tthis.{param_name} = {param_name};")
            else:
                elem_param_simple = dc_param_array.getElementType().asSimpleParameter()
                elem_param_class = dc_param_array.getElementType().asClassParameter()

                if elem_param_class:
                    class_name = elem_param_class.getClass().getName()
                    if class_name not in existing_imports:
                        imports += f'import {class_name} from "./{class_name}";\n'
                        existing_imports.add(class_name)
                    field_declarations.append(
                        f"\tpublic {param_name}!: {class_name}[];"
                    )
                    constructor_params.append(f"\t\t{param_name}: {class_name}[]")
                else:
                    ts_type = get_ts_type_for_subatomic_type(
                        elem_param_simple.getType()
                    )
                    field_declarations.append(f"\tpublic {param_name}!: {ts_type}[];")
                    constructor_params.append(f"\t\t{param_name}: {ts_type}[]")
                constructor_assignments.append(f"\t\tthis.{param_name} = {param_name};")

        field_declarations_str = "\n".join(field_declarations)
        constructor_params_str = ",\n".join(constructor_params)
        constructor_assignments_str = "\n".join(constructor_assignments)

        self.outBuffer = struct_template.format(
            header=GENERATED_FILE_HEADER,
            className=self.name,
            imports=imports,
            fieldDeclarations=field_declarations_str,
            constructorParams=constructor_params_str,
            constructorAssignments=constructor_assignments_str,
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
