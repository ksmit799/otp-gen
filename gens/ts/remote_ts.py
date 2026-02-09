from src.notifier import notify
from gens.ts.constants_ts import GENERATED_FILE_HEADER
from gens.ts.util_ts import (
    format_ts_params_for_atomic_field,
    write_generated_file,
)
from src.util import get_formatted_subatomic_type

template = """{header}
import RemoteBase from "../../otp/dc/RemoteBase";
import ReadHelper from "../../otp/net/ReadHelper";
import StructPacking from "../fn/StructPacking";
{imports}
export default class R{className} extends RemoteBase implements {implements} {{
{fields}
}}
"""


class RemoteTS:
    notify = notify.new_category("RemoteInterfaceTS")

    def __init__(self, name, dclass, out_path):
        self.name = name
        self.dclass = dclass
        self.outPath = out_path
        self.outName = ""
        self.outBuffer = ""

        self._gen_buffer()

    def _gen_buffer(self):
        self.outName = f"R{self.name}.ts"

        name = f"IR{self.name}"  # Prepend with an 'IR'
        imports = f'import {name} from "../iremote/{name}";\n'
        existing_imports = set()

        fields = ""
        for i in range(self.dclass.get_num_inherited_fields()):
            # We implement parent fields here as well.
            field = self.dclass.get_inherited_field(i)
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

            packing = ""
            arg_index = 1
            for k in range(atomic_field.getNumElements()):
                elem = atomic_field.getElement(k)
                elem_class = elem.asClassParameter()
                elem_simple = elem.asSimpleParameter()
                elem_array = elem.asArrayParameter()
                elem_name = elem.getName() or f"arg{arg_index}"

                if elem_class:
                    elem_dc_class = elem_class.getClass()
                    if not elem_dc_class.isStruct():
                        self.notify.warning(
                            f"Got non-struct class as field param: {self.name} - {field.getName()}"
                        )
                        arg_index += 1
                        continue
                    class_name = elem_dc_class.getName()
                    packing += f"\t\tStructPacking.pack{class_name}(dg, {elem_name});\n"

                elif elem_simple:
                    elem_type = elem_simple.getType()
                    elem_type_formatted = get_formatted_subatomic_type(elem_type)
                    is_uint_array = "Array" in elem_type_formatted
                    if is_uint_array:
                        elem_type_formatted = elem_type_formatted.replace("Array", "")
                        packing += f"\t\tReadHelper.writeArrayStatic(dg, {elem_name}, (arrData, arrVal) => {{\n"
                        packing += f"\t\t\tarrData.add{elem_type_formatted}(arrVal);\n"
                        packing += "\t\t});\n"
                    else:
                        packing += f"\t\tdg.add{elem_type_formatted}({elem_name});\n"

                elif elem_array:
                    elem_param_simple = elem_array.getElementType().asSimpleParameter()
                    elem_param_class = elem_array.getElementType().asClassParameter()
                    packing += f"\t\tReadHelper.writeArrayStatic(dg, {elem_name}, (arrData, arrVal) => {{\n"
                    if elem_param_class:
                        class_name = elem_param_class.getClass().getName()
                        packing += f"\t\t\tStructPacking.pack{class_name}(arrData, arrVal);\n"
                    else:
                        packing += f"\t\t\tarrData.add{get_formatted_subatomic_type(elem_param_simple.getType())}(arrVal);\n"
                    packing += "\t\t});\n"

                arg_index += 1

            fields += f"\tpublic {field.getName()}({params}) {{\n"
            fields += "\t\tconst dg = this.getPacker();\n"
            fields += "\t\tdg.addUint32(this.doId);\n"
            fields += f"\t\tdg.addUint16({field.getNumber()});\n"
            fields += packing
            fields += "\t\tthis.sendUpdate(dg);\n"
            fields += "\t}\n\n"

        if fields:
            # Chop off our last char (\n)
            fields = fields[:-1]

        self.outBuffer = template.format(
            header=GENERATED_FILE_HEADER,
            className=self.name,
            imports=imports,
            implements=name,
            fields=fields,
        )

    def write(self):
        if self.outName and self.outBuffer:
            write_generated_file(self.outPath, self.outName, self.outBuffer)
