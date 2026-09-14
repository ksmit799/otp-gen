from pathlib import Path

from panda3d.direct import *


def get_ts_type_for_subatomic_type(subatomic_type):
    if subatomic_type in (
        STUint8,
        STInt8,
        STUint16,
        STInt16,
        STUint32,
        STInt32,
        STFloat64,
    ):
        return "number"

    elif subatomic_type in (STUint64, STInt64):
        return "bigint"

    elif subatomic_type in (STChar, STString):
        return "string"

    elif subatomic_type in (STBlob, STBlob32):
        return "ArrayBufferView"

    elif subatomic_type in (
        STUint8array,
        STInt8array,
        STUint16array,
        STInt16array,
        STUint32array,
        STInt32array,
    ):
        return "number[]"

    else:
        return "unknown"


def write_generated_file(out_path: Path, filename: str, content: str) -> None:
    """Write content to out_path / filename if content is non-empty."""
    if not content:
        return
    path = out_path / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def format_ts_params_for_atomic_field(
    atomic_field, import_prefix: str, existing_imports: set, notify=None
):
    """
    Build TypeScript parameter list and import lines for an atomic field's elements.
    Mutates existing_imports. Returns (params_string, imports_string).
    """
    params_parts = []
    imports_lines = []
    for k in range(atomic_field.getNumElements()):
        elem = atomic_field.getElement(k)
        elem_class = elem.asClassParameter()
        elem_simple = elem.asSimpleParameter()
        elem_array = elem.asArrayParameter()
        elem_name = elem.getName() or f"arg{k + 1}"

        if elem_class:
            elem_dc_class = elem_class.getClass()
            if not elem_dc_class.isStruct() and notify:
                notify.warning(
                    f"Got non-struct class as field param - {elem_dc_class.getName()}"
                )
                continue
            class_name = elem_dc_class.getName()
            if class_name not in existing_imports:
                existing_imports.add(class_name)
                imports_lines.append(
                    f'import {class_name} from "{import_prefix}{class_name}";\n'
                )
            params_parts.append(f"{elem_name}: {class_name}")

        elif elem_simple:
            params_parts.append(
                f"{elem_name}: {get_ts_type_for_subatomic_type(elem_simple.getType())}"
            )

        elif elem_array:
            elem_param_simple = elem_array.getElementType().asSimpleParameter()
            elem_param_class = elem_array.getElementType().asClassParameter()
            if elem_param_class:
                class_name = elem_param_class.getClass().getName()
                if class_name not in existing_imports:
                    existing_imports.add(class_name)
                    imports_lines.append(
                        f'import {class_name} from "{import_prefix}{class_name}";\n'
                    )
                params_parts.append(f"{elem_name}: {class_name}[]")
            else:
                params_parts.append(
                    f"{elem_name}: {get_ts_type_for_subatomic_type(elem_param_simple.getType())}[]"
                )

    params_str = ", ".join(params_parts) if params_parts else ""
    imports_str = "".join(imports_lines)
    return params_str, imports_str
