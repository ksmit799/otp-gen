from src.notifier import notify
from gens.ts.util_ts import get_ts_type_for_subatomic_type


template = """/**
 * THIS FILE WAS AUTOMATICALLY GENERATED BY OTP GEN
 * DO NOT MODIFY
 */
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

            params = ""
            arg_index = 1
            for k in range(atomic_field.getNumElements()):
                elem = atomic_field.getElement(k)
                elem_class = elem.asClassParameter()
                elem_simple = elem.asSimpleParameter()
                elem_array = elem.asArrayParameter()

                if elem_class:
                    # This is (always?) a struct arg.
                    elem_dc_class = elem_class.getClass()
                    if not elem_dc_class.isStruct():
                        self.notify.warning(
                            f"Got non-struct class as field param: {self.name} - {field.getName()}"
                        )
                        continue

                    class_name = elem_dc_class.getName()
                    if class_name not in existing_imports:
                        imports += f'import {class_name} from "../dc/{class_name}";\n'
                        existing_imports.add(class_name)

                    params += f"arg{arg_index}: {class_name}, "

                elif elem_simple:
                    elem_type = elem_simple.getType()
                    params += (
                        f"arg{arg_index}: {get_ts_type_for_subatomic_type(elem_type)}, "
                    )

                elif elem_array:
                    elem_param_simple = elem_array.getElementType().asSimpleParameter()
                    elem_param_class = elem_array.getElementType().asClassParameter()

                    if elem_param_class:
                        # We have an array of classes.
                        class_name = elem_param_class.getClass().getName()
                        if class_name not in existing_imports:
                            imports += (
                                f'import {class_name} from "../dc/{class_name}";\n'
                            )
                            existing_imports.add(class_name)

                        params += f"arg{arg_index}: {class_name}[], "
                    else:
                        # We have an array of generic types.
                        params += f"arg{arg_index}: {get_ts_type_for_subatomic_type(elem_param_simple.getType())}[], "

                arg_index += 1

            if params:
                # Slice off last two chars (, )
                params = params[:-2]

            fields += f"\t{field.getName()}({params}): void;\n"

        if fields:
            # Chop off our last char (\n)
            fields = fields[:-1]

        self.outBuffer = template.format(
            className=self.name, imports=imports, extends=extends, fields=fields
        )

    def write(self):
        if not self.outName or not self.outBuffer:
            return

        with open(self.outPath / self.outName, "w") as out_file:
            out_file.write(self.outBuffer)
