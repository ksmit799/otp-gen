/**
 * THIS FILE WAS AUTOMATICALLY GENERATED BY OTP GEN
 * DO NOT MODIFY
 */

export default interface DCMapping {
    getDCVersion(): number;
    getOwnerInitFunction(clsName: string): any;
    getFunctionNameForId(id: number): string;
    getInitFunction(clsName: string): any;
    getClassNameForFunctionId(id: number): string;
    getClasses(): any[];
    getFunctionForId(id: number): any;
    getClassForId(id: number): string;
    getRemoteInterface(clsName: string): any;
}
