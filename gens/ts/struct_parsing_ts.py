from src.notifier import notify
from src.util import get_formatted_subatomic_type
from gens.ts.constants_ts import GENERATED_FILE_HEADER
from gens.ts.util_ts import write_generated_file

template = """{header}
import DatagramIterator from "../../otp/net/DatagramIterator";
import ReadHelper from "../../otp/net/ReadHelper";
{imports}

export default class StructParsing {{
"""


class StructParsingTS:
    notify = notify.new_category("StructParsingTS")

    def __init__(self, dc_loader, out_path):
        self.dcLoader = dc_loader
        self.outPath = out_path
        self.outBuffer = ""

        self._gen_buffer()

    def _gen_buffer(self):
        imports = ""
        static_out = ""

        for name, dc_class in self.dcLoader.dclasses_by_name.items():
            if not dc_class.isStruct():
                continue

            imports += f'import {name} from "../dc/{name}";\n'
            static_out += (
                f"\tpublic static get{name}(di: DatagramIterator): {name} {{\n"
            )
            ctor_args = []

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
                    elem_dc_class = dc_param_class.getClass()
                    if not elem_dc_class.isStruct():
                        self.notify.warning(
                            f"Got non-struct class as field param: {name} - {elem_dc_class.getName()}"
                        )
                        continue
                    ctor_args.append(f"StructParsing.get{elem_dc_class.getName()}(di)")

                elif dc_param_simple:
                    ctor_args.append(
                        f"di.get{get_formatted_subatomic_type(dc_param_simple.getType())}()"
                    )

                elif dc_param_array:
                    elem_param_simple = (
                        dc_param_array.getElementType().asSimpleParameter()
                    )
                    elem_param_class = (
                        dc_param_array.getElementType().asClassParameter()
                    )
                    arr_inner = (
                        f"arrayData.get{get_formatted_subatomic_type(elem_param_simple.getType())}()"
                        if elem_param_simple
                        else f"StructParsing.get{elem_param_class.getClass().getName()}(arrayData)"
                    )
                    ctor_args.append(
                        f"ReadHelper.readArrayStatic(di, (arrayData) => {{\n\t\t\t\treturn {arr_inner};\n\t\t\t}})"
                    )

            static_out += "\t\treturn new " + name + "(\n\t\t\t"
            static_out += ",\n\t\t\t".join(ctor_args)
            static_out += "\n\t\t);\n"
            static_out += "\t}\n\n"

        if imports:
            # Trim off newline.
            imports = imports[:-1]

        self.outBuffer = template.format(header=GENERATED_FILE_HEADER, imports=imports)
        self.outBuffer += static_out
        self.outBuffer += "\n}"

    def write(self):
        write_generated_file(self.outPath, "StructParsing.ts", self.outBuffer)
