/**
 * THIS FILE WAS AUTOMATICALLY GENERATED BY OTP GEN
 * DO NOT MODIFY
 */

export default class DatagramIterator {
    private buffer: ArrayBuffer;
    private bufferIndex: number;

    constructor(data: ArrayBuffer) {
        this.buffer = data;
        this.bufferIndex = 0;
    }

    private ensureLength(size: number) {
        if (this.bufferIndex + size > this.buffer.byteLength) {
            throw new Error("[DC] DG read exceeds max length!");
        }
    }

    public getUint8(): number {
        this.ensureLength(1);
        const data = new DataView(this.buffer).getUint8(this.bufferIndex);
        this.bufferIndex += 1;

        return data;
    }

    public getInt8(): number {
        this.ensureLength(1);
        const data = new DataView(this.buffer).getInt8(this.bufferIndex);
        this.bufferIndex += 1;

        return data;
    }

    public getUint16(): number {
        this.ensureLength(2);
        const data = new DataView(this.buffer).getUint16(this.bufferIndex, true);
        this.bufferIndex += 2;

        return data;
    }

    public getInt16(): number {
        this.ensureLength(2);
        const data = new DataView(this.buffer).getInt16(this.bufferIndex, true);
        this.bufferIndex += 2;

        return data;
    }

    public getUint32(): number {
        this.ensureLength(4);
        const data = new DataView(this.buffer).getUint32(this.bufferIndex, true);
        this.bufferIndex += 4;

        return data;
    }

    public getInt32(): number {
        this.ensureLength(4);
        const data = new DataView(this.buffer).getInt32(this.bufferIndex, true);
        this.bufferIndex += 4;

        return data;
    }

    public getUint64(): bigint {
        this.ensureLength(8);
        const data = new DataView(this.buffer).getBigUint64(this.bufferIndex, true);
        this.bufferIndex += 8;

        return data;
    }

    public getInt64(): bigint {
        this.ensureLength(8);
        const data = new DataView(this.buffer).getBigInt64(this.bufferIndex, true);
        this.bufferIndex += 8;

        return data;
    }

    public getChar(): string {
        return String.fromCharCode(this.getUint8());
    }

    public getString(): string {
        const len = this.getUint16();
        const str = [];
        for (let i = 0; i < len; i++) {
            str.push(this.getChar());
        }

        return str.join("");
    }

    public getBlob(): ArrayBuffer {
        const len = this.getUint16();
        const data = this.buffer.slice(this.bufferIndex, this.bufferIndex + len);
        this.bufferIndex += len;

        return data;
    }

    public getUint32Array(): number[] {
        const len = this.getUint16();
        const arr = [];
        for (let i = 0; i < len; i++) {
            arr.push(this.getUint32());
        }

        return arr;
    }

    public getRemainingSize(): number {
        return this.buffer.byteLength - this.bufferIndex;
    }
}
