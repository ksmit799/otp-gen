from gens.ts.util_ts import get_ts_type_for_subatomic_type
from src.notifier import notify
from src.util import get_formatted_subatomic_type
from gens.ts.constants_ts import GENERATED_FILE_HEADER
from gens.ts.util_ts import write_generated_file

template = """{header}
import Datagram from "../../otp/net/Datagram";
import ReadHelper from "../../otp/net/ReadHelper";
{imports}

export default class StructPacking {{
{fields}
}}
"""


class StructPackingTS:
    notify = notify.new_category("StructPackingTS")

    def __init__(self, dc_loader, out_path):
        self.dcLoader = dc_loader
        self.outPath = out_path
        self.outBuffer = ""

        self._gen_buffer()

    def _gen_buffer(self):
        imports = ""

        fields = ""
        for name, dc_class in self.dcLoader.dclasses_by_name.items():
            if not dc_class.isStruct():
                continue

            imports += f'import {name} from "../dc/{name}";\n'

            packing = ""
            arg_index = 1
            for i in range(dc_class.get_num_fields()):
                field = dc_class.get_field(i)
                dc_parameter = field.asParameter()
                if not dc_parameter:
                    self.notify.warning(
                        f"Got non parameter field in struct: {name} - {field.getName()}"
                    )
                    continue

                dc_param_class = dc_parameter.asClassParameter()
                dc_param_simple = dc_parameter.asSimpleParameter()
                dc_param_array = dc_parameter.asArrayParameter()

                if dc_param_class:
                    # This is (always?) a struct arg.
                    elem_dc_class = dc_param_class.getClass()
                    if not elem_dc_class.isStruct():
                        self.notify.warning(
                            f"Got non-struct class as field param: {name} - {elem_dc_class.getName()}"
                        )
                        continue

                    class_name = elem_dc_class.getName()
                    packing += f"\t\tStructPacking.pack{class_name}(dg, arg.{dc_param_class.getName()});\n"

                elif dc_param_simple:
                    elem_type = dc_param_simple.getType()
                    packing += f"\t\tdg.add{get_formatted_subatomic_type(elem_type)}(arg.{dc_param_simple.getName()});\n"

                elif dc_param_array:
                    elem_param_simple = (
                        dc_param_array.getElementType().asSimpleParameter()
                    )
                    elem_param_class = (
                        dc_param_array.getElementType().asClassParameter()
                    )

                    packing += f"\t\tReadHelper.writeArrayStatic(dg, arg.{dc_param_array.getName()}, (arrData, arrVal) => {{\n"

                    if elem_param_class:
                        # We have an array of classes.
                        class_name = elem_param_class.getClass().getName()
                        packing += (
                            f"\t\t\tStructPacking.pack{class_name}(arrData, arrVal);\n"
                        )

                    elif elem_param_simple:
                        # We have an array of generic types.
                        packing += f"\t\t\tarrData.add{get_formatted_subatomic_type(elem_param_simple.getType())}(arrVal);\n"

                    packing += "\t\t});\n"

                arg_index += 1

            fields += f"\tpublic static pack{name}(dg: Datagram, arg: {name}) {{\n"
            fields += packing
            fields += "\t}\n\n"

        if fields:
            # Chop off our last char (\n)
            fields = fields[:-1]

        self.outBuffer = template.format(
            header=GENERATED_FILE_HEADER, imports=imports, fields=fields
        )

    def write(self):
        write_generated_file(self.outPath, "StructPacking.ts", self.outBuffer)
