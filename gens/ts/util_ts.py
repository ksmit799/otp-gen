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
        return "ArrayBuffer"

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
