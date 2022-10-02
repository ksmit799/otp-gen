import ObjectStore from "./ObjectStore";
import DatagramIterator from "../net/DatagramIterator";
import Datagram from "../net/Datagram";
import MessageTypes from "../net/MessageTypes";
import DCMapping from "../../generated/fn/DCMapping";
import DCInterface from "./DCInterface";

/**
 * OTPClientRepository implements all the required functionality for generating,
 * storing, updating, and deleting distributed objects.
 * It is up to the developer to handle network connectivity.
 */
export default class OTPClientRepository {
    public objStore: ObjectStore;
    protected wantDClassStore: boolean;
    protected name2class: {[name: string]: DCInterface} = {};

    constructor(wantDClassStore = true) {
        this.objStore = new ObjectStore();

        // TODO: Figure out this reflection stuff.
        this.wantDClassStore = wantDClassStore;
        if (!typeof window && !wantDClassStore) {
            // We don't have a window object to use for "reflection"
            // and the developer hasn't explicitly requested a dclass store.
            console.error(`[DC] Window object does not exist. DClasses must be explicit set in this environment.`);
            console.error(`[DC] See otp-gen readme for more information.`);
            this.wantDClassStore = true;
        }
    }

    public setDClass(name: string, dclass: DCInterface) {
        this.name2class[name] = dclass;
    }

    public getDClass(name: string) {
        // Do we want to use reflection or do we have explicitly set dclasses?
        if (this.wantDClassStore) {
            return this.name2class[name];
        }

        // This is kind of a "hacky" runtime reflection.
        // If class names are obfuscated or the window object is undefined, this won't work.
        // DCLasses will need to be manually set in that case.
        // @ts-ignore
        return window[name].prototype;
    }

    public handleDatagram(di: DatagramIterator) {
        const msgType = di.getUint16();

        switch (msgType) {
            case MessageTypes.CLIENT_LOGIN_RESP:
                // We've successfully authed with the server.
                this.handleLogin(di);
                break;
            case MessageTypes.CLIENT_GO_GET_LOST_RESP:
                // We've been booted by the server!
                this.handleGoGetLost(di);
                break;
            case MessageTypes.CLIENT_OBJECT_SET_FIELD:
                // We have a field update for an object in our interest.
                this.handleSetField(di);
                break;
            case MessageTypes.CLIENT_OBJECT_DISABLE_RESP:
            case MessageTypes.CLIENT_OBJECT_DISABLE_OWNER_RESP:
            case MessageTypes.CLIENT_OBJECT_DELETE_RESP:
                this.handleDeleteObject(di);
                break;
            case MessageTypes.CLIENT_CREATE_OBJECT_REQUIRED:
            case MessageTypes.CLIENT_CREATE_OBJECT_REQUIRED_OTHER:
                this.handleObjectEnter(di);
                break;
            case MessageTypes.CLIENT_CREATE_OBJECT_REQUIRED_OTHER_OWNER:
                this.handleObjectEnterOwner(di);
                break;
            case MessageTypes.CLIENT_DONE_SET_ZONE_RESP:
                break;
            case MessageTypes.CLIENT_GET_STATE_RESP:
                // TODO: Ehh do we need to implement this?
                break;
            case MessageTypes.CLIENT_OBJECT_LOCATION:
                this.handleObjectLocation(di);
                break;
            default:
                console.error(`[DC] Received unknown message type: ${msgType}`);
        }
    }

    public sendDatagram(dg: Datagram) {
        /**
         * Inheritors to override.
         */
    }

    public handleLogin(di: DatagramIterator) {
        /**
         * Inheritors to override.
         */
    }

    public handleGoGetLost(di: DatagramIterator) {
        /**
         * Inheritors to override.
         */
    }

    public setLocation(doId: number, parentId: number, zoneId: number) {
        /**
         * A distributed object is attempting to update its location...
         */
        const dg = new Datagram();
        dg.addUint16(MessageTypes.CLIENT_OBJECT_LOCATION);
        dg.addUint32(doId);
        dg.addUint32(parentId);
        dg.addUint32(zoneId);
        this.sendDatagram(dg);
    }

    protected handleSetField(di: DatagramIterator) {
        const doId = di.getUint32();
        const fieldId = di.getUint16();

        const distObj = this.objStore.getObj(doId);
        if (distObj) {
            this.callFunction(distObj, fieldId, di);
        } else {
            console.error(`[DC] Failed to handle set field for missing object ${doId}`);
        }
    }

    protected callFunction(distObj: any, fieldId: number, di: DatagramIterator) {
        const mappedFunc = DCMapping.getFunctionForId(fieldId);
        if (!mappedFunc) {
            console.error(`[DC] Missing mapping for field id: ${fieldId}`);
            return;
        }

        try {
            mappedFunc(distObj, di);
        } catch (e) {
            console.error(`[DC] Error thrown from field dispatch. fieldId: ${fieldId}, doId: ${distObj.doId}`);
            throw e;
        }
    }

    protected createObjectInstance(doId: number, clsName: string, parentId: number, zoneId: number, owner: boolean) {
        const classObj = this.getDClass(clsName);
        if (!classObj) {
            throw new Error(`[DC] Missing dclass mapping for '${clsName}'`);
        }

        const obj = new classObj() as DCInterface;
        obj.beforeGenerate();
        obj.doId = doId;
        obj.parent = parentId;
        obj.zone = zoneId;
        obj.cr = this;
        obj.isOwner = owner;
        obj.setRemote(this.getRemoteInterface(clsName, doId));

        return obj;
    }

    protected finalizeObjectCreation(doId: number, distObj: DCInterface) {
        this.objStore.putObj(doId, distObj);
        distObj.generateComplete();
        distObj.afterGenerate();
    }

    protected createObjectPreparsed(
        doId: number,
        classId: number,
        parentId: number,
        zoneId: number,
        owner: boolean,
        di: DatagramIterator
    ) {
        console.log(`[DC] Creating distObj... DoId: ${doId}, Parent: ${parentId}, Zone: ${zoneId}, Class: ${classId}`);

        const clsName = DCMapping.getClassForId(classId);
        if (!clsName) {
            console.error(`[DC] Unable to create distObj! Class undefined: ${classId}`);
            return;
        }

        try {
            const distObj = this.createObjectInstance(doId, clsName, parentId, zoneId, owner) as DCInterface;
            console.log(`[DC] Created object instance.`);

            const initFunc = owner ? DCMapping.getOwnerInitFunction(clsName) : DCMapping.getInitFunction(clsName);
            initFunc(distObj, doId, di);
            console.log(`[DC] Finished initializing object.`);

            if (di.getRemainingSize()) {
                // We have optional fields...
                const fieldCount = di.getUint16();
                for (let i = 0; i < fieldCount; i++) {
                    const fieldId = di.getUint16();
                    this.callFunction(distObj, fieldId, di);
                }
            }

            this.finalizeObjectCreation(doId, distObj);
            console.log(`[DC] Finished generating object.`);
        } catch (e) {
            console.error(`[DC] Failed to create object with DoId: ${doId}`);
            throw e;
        }
    }

    protected handleDeleteObject(di: DatagramIterator) {
        const doId = di.getUint32();
        console.log(`[DC] Processing delete object for doId: ${doId}`);

        const distObj = this.objStore.getObj(doId);
        if (!distObj) {
            console.warn(`[DC] Received delete object for unknown doId: ${doId}`);
            return;
        }

        distObj.beforeDelete();
        this.objStore.removeObj(doId);
        distObj.afterDelete();

        console.log(`[DC] Deleted object with doId: ${doId}`);
    }

    protected handleObjectEnter(di: DatagramIterator) {
        const parentId = di.getUint32();
        const zoneId = di.getUint32();
        const fieldId = di.getUint16();
        const doId = di.getUint32();

        this.createObjectPreparsed(doId, fieldId, parentId, zoneId, false, di);
    }

    protected handleObjectEnterOwner(di: DatagramIterator) {
        const fieldId = di.getUint16();
        const doId = di.getUint32();
        const parentId = di.getUint32();
        const zoneId = di.getUint32();

        this.createObjectPreparsed(doId, fieldId, parentId, zoneId, true, di);
    }

    protected handleObjectLocation(di: DatagramIterator) {
        const doId = di.getUint32();
        console.log(`[DC] Handling object location for doId: ${doId}`);

        const distObj = this.objStore.getObj(doId);
        if (!distObj) {
            console.warn(`[DC] Update location received for null object: ${doId}`);
            return;
        }

        distObj.parent = di.getUint32();
        distObj.zone = di.getUint32();

        console.log(`[DC] Updated object location - doId: ${doId}, parent: ${distObj.parent}, zone: ${distObj.zone}`);
    }

    protected getRemoteInterface(clsName: string, doId: number) {
        const remoteInterface = DCMapping.getRemoteInterface(clsName);
        if (!remoteInterface) {
            console.warn(`[DC] Missing remote interface for class: ${clsName}`);
            return null;
        }

        return new remoteInterface(doId, this);
    }
}
