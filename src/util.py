from panda3d.direct import *


def get_formatted_subatomic_type(subatomic_type):
    if subatomic_type == STUint8:
        return "Uint8"
    elif subatomic_type == STInt8:
        return "Int8"
    elif subatomic_type == STUint16:
        return "Uint16"
    elif subatomic_type == STInt16:
        return "Int16"
    elif subatomic_type == STUint32:
        return "Uint32"
    elif subatomic_type == STInt32:
        return "Int32"
    elif subatomic_type == STUint64:
        return "Uint64"
    elif subatomic_type == STInt64:
        return "Int64"

    elif subatomic_type == STFloat64:
        return "Float64"

    elif (
        subatomic_type == STChar
    ):  # Equivalent to uint8, except that it suggests a pack_type of PT_string.
        return "Char"
    elif subatomic_type == STString:  # a human-printable string.
        return "String"
    elif subatomic_type == STBlob:  # any variable length message, stored as a string.
        return "Blob"
    elif subatomic_type == STBlob32:  # a blob with a 32-bit length, up to 4.2 GB long.
        return "Blob32"

    elif subatomic_type == STUint8array:
        return "Uint8Array"
    elif subatomic_type == STInt8array:
        return "Int8Array"
    elif subatomic_type == STUint16array:
        return "Uint16Array"
    elif subatomic_type == STInt16array:
        return "Int16Array"
    elif subatomic_type == STUint32array:
        return "Uint32Array"
    elif subatomic_type == STInt32array:
        return "Int32Array"

    elif subatomic_type == STUint32uint8array:
        return "Uint32Uint8Array"

    else:
        return "Invalid"


def is_server_field(field):
    if field.getNumKeywords():
        if (
            not field.isClsend()
            and not field.isOwnsend()
            and not field.isOwnrecv()
            and not field.isRequired()
            and not field.isBroadcast()
        ):
            return True

    return False
