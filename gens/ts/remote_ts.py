template = """/**
 * THIS FILE WAS AUTOMATICALLY GENERATED BY OTP GEN
 * DO NOT MODIFY
 */
import RemoteBase from "../../otp/dc/RemoteBase";
{imports}
export default class R{className} extends RemoteBase implements {implements} {{
{fields}
}}
"""


class RemoteTS:
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
        implements = name

        fields = ""
        for i in range(self.dclass.get_num_inherited_fields()):
            # We implement parent fields here as well.
            field = self.dclass.get_inherited_field(i)
            if not field.isClsend() and not field.isOwnsend():
                # Skip fields that aren't sendable.
                continue

            # TODO: Field packing.
            fields += f"\tpublic {field.getName()}() {{}}\n"

        if fields:
            # Chop off our last char (\n)
            fields = fields[:-1]

        self.outBuffer = template.format(
            className=self.name, imports=imports, implements=implements, fields=fields
        )

    def write(self):
        if not self.outName or not self.outBuffer:
            return

        with open(self.outPath / self.outName, "w") as out_file:
            out_file.write(self.outBuffer)
