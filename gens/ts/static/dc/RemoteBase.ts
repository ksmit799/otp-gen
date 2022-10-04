/**
 * THIS FILE WAS AUTOMATICALLY GENERATED BY OTP GEN
 * DO NOT MODIFY
 */
import OTPClientRepository from "./OTPClientRepository";
import Datagram from "../net/Datagram";
import MessageTypes from "../net/MessageTypes";

export default class RemoteBase {
    private readonly _doId: number;
    private readonly cr: OTPClientRepository;

    constructor(doId: number, cr: OTPClientRepository) {
        this._doId = doId;
        this.cr = cr;
    }

    public get doId(): number {
        return this._doId;
    }

    protected sendUpdate(dg: Datagram) {
        this.cr.sendDatagram(dg);
    }

    protected getPacker(): Datagram {
        const dg = new Datagram();
        dg.addUint16(MessageTypes.CLIENT_OBJECT_SET_FIELD)
        return dg;
    }
}
