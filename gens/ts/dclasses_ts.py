from gens.ts.constants_ts import GENERATED_FILE_HEADER
from gens.ts.util_ts import write_generated_file, get_ts_type_for_subatomic_type
from src.notifier import notify
from src.util import get_formatted_subatomic_type


class DClassesTS:
    """
    Generates per-class DC descriptors (DC<ClassName>.ts) and a dclasses.ts
    mapping file for server-side usage.
    """

    notify = notify.new_category("DClassesTS")

    def __init__(self, dc_loader, class_files_path, mapping_file_path):
        self.dcLoader = dc_loader
        self.classFilesPath = class_files_path
        self.mappingFilePath = mapping_file_path

        self._generate_class_files()
        self._generate_mapping_file()

    def write(self):
        """
        For compatibility with the other generators, which expect a `write()`
        method. All work is done in __init__, so this is a no-op.
        """
        return None

    def _generate_class_files(self):
        """
        For each non-struct distributed class, generate a DC<ClassName>.ts file
        that can decode a field datagram into an argument array and exposes
        metadata (keywords, id/name lookups) for each field.
        """
        for class_id in sorted(self.dcLoader.dclasses_by_number):
            dc_class = self.dcLoader.dclasses_by_number[class_id]
            if dc_class.isStruct():
                continue

            class_name = dc_class.getName()
            self.notify.debug(f"Generating DC descriptor for '{class_name}'")

            imports = ""
            imports += 'import type { DCFieldInfo } from "../../otp/dc/dclasses";\n'
            imports += 'import Datagram from "../../otp/net/Datagram";\n'
            imports += (
                'import DatagramIterator from "../../otp/net/DatagramIterator";\n'
            )
            imports += 'import ReadHelper from "../../otp/net/ReadHelper";\n'
            imports += 'import StructParsing from "../fn/StructParsing";\n'
            imports += 'import StructPacking from "../fn/StructPacking";\n'
            existing_imports = set()

            # Build field metadata maps.
            fields_by_id_lines = []
            fields_by_name_lines = []

            for i in range(dc_class.get_num_fields()):
                field = dc_class.get_field(i)
                field_id = field.getNumber()
                field_name = field.getName()

                keywords = []
                for k in range(field.getNumKeywords()):
                    keywords.append(f'"{field.getKeyword(k).getName()}"')
                keywords_str = ", ".join(keywords)

                fields_by_id_lines.append(
                    f'\t\t{field_id}: {{ id: {field_id}, name: "{field_name}", keywords: [{keywords_str}] }},'
                )
                # Point to the already-defined _fieldsById entry rather than duplicating.
                fields_by_name_lines.append(
                    f'\t\t"{field_name}": DC{class_name}._fieldsById[{field_id}],'
                )

            fields_by_id = "\n".join(fields_by_id_lines)
            fields_by_name = "\n".join(fields_by_name_lines)

            # Build decode switch cases.
            decode_cases_lines = []
            # Build encode switch cases.
            encode_cases_lines = []
            for i in range(dc_class.get_num_fields()):
                field = dc_class.get_field(i)
                field_id = field.getNumber()

                molecular_field = field.asMolecularField()
                atomic_field = field.asAtomicField()
                dc_parameter = field.asParameter()

                decode_cases_lines.append(f"\t\t\tcase {field_id}: {{")
                decode_cases_lines.append("\t\t\t\tconst args: any[] = [];")

                encode_cases_lines.append(f"\t\t\tcase {field_id}: {{")
                encode_arg_index = 0

                if molecular_field:
                    # TODO: Implement encoding for molecular fields if needed.
                    self.notify.warning(
                        f"Skipping encode for molecular field {class_name}.{field.getName()} (unimplemented)."
                    )

                    for k in range(molecular_field.getNumAtomics()):
                        atomic = molecular_field.getAtomic(k)
                        decode_cases_lines.append(
                            f"\t\t\t\targs.push(...DC{class_name}.decodeField({atomic.getNumber()}, di));"
                        )

                elif atomic_field:
                    # Atomic field: read each element from the datagram.
                    for k in range(atomic_field.getNumElements()):
                        elem = atomic_field.getElement(k)
                        elem_class = elem.asClassParameter()
                        elem_simple = elem.asSimpleParameter()
                        elem_array = elem.asArrayParameter()

                        if elem_class:
                            # Always a struct argument.
                            elem_dc_class = elem_class.getClass()
                            if not elem_dc_class.isStruct():
                                self.notify.warning(
                                    f"Got non-struct class as field param: {class_name} - {elem_dc_class.getName()}"
                                )
                                continue
                            struct_ts_name = elem_dc_class.getName()
                            if struct_ts_name not in existing_imports:
                                imports += f'import {struct_ts_name} from "../dc/{struct_ts_name}";\n'
                                existing_imports.add(struct_ts_name)
                            decode_cases_lines.append(
                                f"\t\t\t\targs.push(StructParsing.get{elem_dc_class.getName()}(di));"
                            )

                            # Encode: struct element.
                            encode_cases_lines.append(
                                f"\t\t\t\tStructPacking.pack{elem_dc_class.getName()}(dg, args[{encode_arg_index}] as {elem_dc_class.getName()});"
                            )
                            encode_arg_index += 1

                        if elem_simple:
                            elem_type = elem_simple.getType()
                            elem_type_formatted = get_formatted_subatomic_type(
                                elem_type
                            )
                            is_uint_array = "Array" in elem_type_formatted

                            # Decode simple element.
                            if is_uint_array:
                                elem_type_formatted = elem_type_formatted.replace(
                                    "Array", ""
                                )
                                decode_cases_lines.append(
                                    "\t\t\t\targs.push(ReadHelper.readArrayStatic(di, (arrayData) => {"
                                )
                                decode_cases_lines.append(
                                    f"\t\t\t\t\treturn arrayData.get{elem_type_formatted}();"
                                )
                                decode_cases_lines.append("\t\t\t\t}));")
                            else:
                                decode_cases_lines.append(
                                    f"\t\t\t\targs.push(di.get{elem_type_formatted}());"
                                )

                            # Encode simple element.
                            ts_type = get_ts_type_for_subatomic_type(elem_type)
                            elem_type_formatted_enc = get_formatted_subatomic_type(
                                elem_type
                            )
                            is_uint_array_enc = "Array" in elem_type_formatted_enc

                            if is_uint_array_enc:
                                base_type = elem_type_formatted_enc.replace("Array", "")
                                encode_cases_lines.append(
                                    f"\t\t\t\tReadHelper.writeArrayStatic(dg, args[{encode_arg_index}] as {ts_type}, (arrData, arrVal) => {{"
                                )
                                encode_cases_lines.append(
                                    f"\t\t\t\t\tarrData.add{base_type}(arrVal);"
                                )
                                encode_cases_lines.append("\t\t\t\t});")
                            else:
                                encode_cases_lines.append(
                                    f"\t\t\t\tdg.add{elem_type_formatted_enc}(args[{encode_arg_index}] as {ts_type});"
                                )

                            encode_arg_index += 1

                        elif elem_array:
                            elem_param_simple = (
                                elem_array.getElementType().asSimpleParameter()
                            )
                            elem_param_class = (
                                elem_array.getElementType().asClassParameter()
                            )

                            decode_cases_lines.append(
                                "\t\t\t\targs.push(ReadHelper.readArrayStatic(di, (arrayData) => {"
                            )

                            if elem_param_simple:
                                decode_cases_lines.append(
                                    f"\t\t\t\t\treturn arrayData.get{get_formatted_subatomic_type(elem_param_simple.getType())}();"
                                )
                            else:
                                decode_cases_lines.append(
                                    f"\t\t\t\t\treturn StructParsing.get{elem_param_class.getClass().getName()}(arrayData);"
                                )

                            decode_cases_lines.append("\t\t\t\t}));")

                            # Encode: array element.
                            encode_cases_lines.append(
                                f"\t\t\t\tReadHelper.writeArrayStatic(dg, args[{encode_arg_index}] as "
                                + (
                                    f"{get_ts_type_for_subatomic_type(elem_param_simple.getType())}[]"
                                    if elem_param_simple
                                    else f"{elem_param_class.getClass().getName()}[]"
                                )
                                + ", (arrData, arrVal) => {"
                            )

                            if elem_param_class:
                                class_name_arr = elem_param_class.getClass().getName()
                                if class_name_arr not in existing_imports:
                                    imports += f'import {class_name_arr} from "../dc/{class_name_arr}";\n'
                                    existing_imports.add(class_name_arr)
                                encode_cases_lines.append(
                                    f"\t\t\t\t\tStructPacking.pack{class_name_arr}(arrData, arrVal);"
                                )
                            elif elem_param_simple:
                                encode_cases_lines.append(
                                    f"\t\t\t\t\tarrData.add{get_formatted_subatomic_type(elem_param_simple.getType())}(arrVal);"
                                )

                            encode_cases_lines.append("\t\t\t\t});")
                            encode_arg_index += 1

                elif dc_parameter:
                    # Simple parameter field; currently not expected in typical OTP DC usage.
                    self.notify.warning(
                        f"Skipping simple-parameter field (unimplemented decode) {class_name} - {field.getName()}"
                    )

                else:
                    self.notify.error(
                        f"Failed to parse field {field.getName()} for decode generation!"
                    )

                decode_cases_lines.append("\t\t\t\treturn args;")
                decode_cases_lines.append("\t\t\t}")
                encode_cases_lines.append("\t\t\t\treturn;")
                encode_cases_lines.append("\t\t\t}")

            decode_cases = "\n".join(decode_cases_lines)
            encode_cases = "\n".join(encode_cases_lines)

            class_template = """{header}
{imports}
export default class DC{className} {{
    public static readonly CLASS_ID: number = {classId};
    public static readonly CLASS_NAME: string = "{className}";

    private static readonly _fieldsById: {{ [id: number]: DCFieldInfo }} = {{
{fieldsById}
    }};

    private static readonly _fieldsByName: {{ [name: string]: DCFieldInfo }} = {{
{fieldsByName}
    }};

    public static getFieldById(id: number): DCFieldInfo | undefined {{
        return this._fieldsById[id];
    }}

    public static getFieldByName(name: string): DCFieldInfo | undefined {{
        return this._fieldsByName[name];
    }}

    public static decodeField(id: number, di: DatagramIterator): any[] {{
        switch (id) {{
{decodeCases}
            default: {{
                throw new Error(`Unknown field id ${{id}} for class {className}`);
            }}
        }}
    }}
    
    public static encodeField(id: number, dg: Datagram, args: any[]): void {{
        switch (id) {{
{encodeCases}
            default: {{
                throw new Error(`Unknown field id ${{id}} for class {className}`);
            }}
        }}
    }}
}}
"""

            out_buffer = class_template.format(
                header=GENERATED_FILE_HEADER,
                imports=imports,
                className=class_name,
                classId=class_id,
                fieldsById=fields_by_id,
                fieldsByName=fields_by_name,
                decodeCases=decode_cases,
                encodeCases=encode_cases,
            )

            write_generated_file(self.classFilesPath, f"DC{class_name}.ts", out_buffer)

    def _generate_mapping_file(self):
        """
        Generate dclasses.ts mapping DC class id/name to their DC<ClassName>
        implementation and define the shared DCFieldInfo type.
        """
        imports_lines = []
        by_id_lines = []
        by_name_lines = []

        for class_id in sorted(self.dcLoader.dclasses_by_number):
            dc_class = self.dcLoader.dclasses_by_number[class_id]
            if dc_class.isStruct():
                continue

            class_name = dc_class.getName()
            imports_lines.append(
                f'import DC{class_name} from "../../generated/dclasses/DC{class_name}";'
            )
            by_id_lines.append(f"        {class_id}: DC{class_name},")
            by_name_lines.append(f'        "{class_name}": DC{class_name},')

        imports = "\n".join(imports_lines)
        by_id = "\n".join(by_id_lines)
        by_name = "\n".join(by_name_lines)

        mapping_template = """{header}
export interface DCFieldInfo {{
    id: number;
    name: string;
    keywords: string[];
}}

import Datagram from "../net/Datagram";
import DatagramIterator from "../net/DatagramIterator";

export interface DCClassDescriptor {{
    readonly CLASS_ID: number;
    readonly CLASS_NAME: string;
    getFieldById(id: number): DCFieldInfo | undefined;
    getFieldByName(name: string): DCFieldInfo | undefined;
    decodeField(id: number, di: DatagramIterator): any[];
    encodeField(id: number, dg: Datagram, args: any[]): void;
}}

{imports}

export default class DClasses {{
    private static readonly byId: {{ [id: number]: DCClassDescriptor }} = {{
{byId}
    }};

    private static readonly byName: {{ [name: string]: DCClassDescriptor }} = {{
{byName}
    }};

    public static getById(id: number): DCClassDescriptor | undefined {{
        return this.byId[id];
    }}

    public static getByName(name: string): DCClassDescriptor | undefined {{
        return this.byName[name];
    }}
}}
"""

        out_buffer = mapping_template.format(
            header=GENERATED_FILE_HEADER,
            imports=imports,
            byId=by_id,
            byName=by_name,
        )

        write_generated_file(self.mappingFilePath, "dclasses.ts", out_buffer)
