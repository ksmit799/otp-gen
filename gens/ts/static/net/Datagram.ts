/**
 * THIS FILE WAS AUTOMATICALLY GENERATED BY OTP GEN
 * DO NOT MODIFY
 */

// Max amount of data we can have is an uint16 (65k bytes)
const MAX_DG_SIZE = 0xffff;
// 128 bytes seems like a good minimum datagram size.
const MIN_DG_SIZE = 0x80;

export default class Datagram {
    private buffer: ArrayBuffer;
    private bufferIndex: number;

    constructor() {
        // Array buffers require a fixed length on creation.
        // We *could* just pass in MAX_DG_SIZE here. However,
        // for every new datagram we create, we would be creating
        // a 65k 0 padded buffer eating up memory.
        // Instead, we automatically grow the buffer as we add data.
        this.buffer = new ArrayBuffer(MIN_DG_SIZE);
        this.bufferIndex = 0;
    }

    private ensureLength(size: number) {
        if (this.bufferIndex + size > MAX_DG_SIZE) {
            throw new Error("[DC] DG write exceeds max length!");
        }

        if (this.buffer.byteLength < this.bufferIndex + size) {
            // We need to resize our buffer...
            const newLength = this.buffer.byteLength + MIN_DG_SIZE + size;
            const oldBuffer = new Uint8Array(this.buffer);

            this.buffer = new ArrayBuffer(newLength);
            new Uint8Array(this.buffer).set(oldBuffer);
        }
    }

    public addUint8(arg: number) {
        this.ensureLength(1);
        new DataView(this.buffer).setUint8(this.bufferIndex, arg);
        this.bufferIndex += 1;
    }

    public addInt8(arg: number) {
        this.ensureLength(1);
        new DataView(this.buffer).setInt8(this.bufferIndex, arg);
        this.bufferIndex += 1;
    }

    public addUint16(arg: number) {
        this.ensureLength(2);
        new DataView(this.buffer).setUint16(this.bufferIndex, arg, true);
        this.bufferIndex += 2;
    }

    public addInt16(arg: number) {
        this.ensureLength(2);
        new DataView(this.buffer).setInt16(this.bufferIndex, arg, true);
        this.bufferIndex += 2;
    }

    public addUint32(arg: number) {
        this.ensureLength(4);
        new DataView(this.buffer).setUint32(this.bufferIndex, arg, true);
        this.bufferIndex += 4;
    }

    public addInt32(arg: number) {
        this.ensureLength(4);
        new DataView(this.buffer).setInt32(this.bufferIndex, arg, true);
        this.bufferIndex += 4;
    }

    public addUint64(arg: bigint) {
        this.ensureLength(8);
        new DataView(this.buffer).setBigUint64(this.bufferIndex, arg, true);
        this.bufferIndex += 8;
    }

    public addInt64(arg: bigint) {
        this.ensureLength(8);
        new DataView(this.buffer).setBigInt64(this.bufferIndex, arg, true);
        this.bufferIndex += 8;
    }

    public addFloat64(arg: number) {
        this.ensureLength(8);
        new DataView(this.buffer).setFloat64(this.bufferIndex, arg, true);
        this.bufferIndex += 8;
    }

    public addString(arg: string) {
        this.ensureLength(arg.length + 2); // Plus 2 for the uint16.
        this.addUint16(arg.length);
        for (let i = 0; i < arg.length; i++) {
            this.addUint8(arg.charCodeAt(i));
        }
    }

    public addBlob(arg: ArrayBuffer) {
        // TODO: Add this.
    }

    public getMessage(): ArrayBufferView {
        // Converting to a Uint8Array here *might* wipe out any endianness we've done above.
        // From what I can tell, this is a limitation of the platform itself.
        return new Uint8Array(this.buffer.slice(0, this.bufferIndex));
    }
}
