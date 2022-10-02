import DCInterface from "./DCInterface";
import OTPClientRepository from "./OTPClientRepository";

export default class DCObject implements DCInterface {
    public _doId: number = -1;
    public cr?: OTPClientRepository;
    public _parent: number = -1;
    public _zone: number = -1;
    public isOwner: boolean = false;

    protected remote: any;
    protected constructing: boolean = true;

    public isInGenerate() {
        return this.constructing;
    }

    public set doId(doId: number) {
        if (this.isInGenerate()) {
            this._doId = doId;
        }
    }

    public get doId() {
        return this._doId;
    }

    public set parent(parent: number) {
        if (this.isInGenerate()) {
            this._parent = parent;
        }
    }

    public get parent() {
        return this._parent;
    }

    public set zone(zone: number) {
        if (this.isInGenerate()) {
            this._zone = zone;
        }
    }

    public get zone() {
        return this._zone;
    }

    public setRemote(remote: any) {
        this.remote = remote;
    }

    public generateComplete() {
        this.constructing = false;
    }

    public setLocation(parentId: number, zoneId: number) {
        this._parent = parentId;
        this._zone = zoneId;

        if (!this.cr) {
            console.warn(`[DC] Attempted to set location with invalid client repository!`);
            return;
        }

        this.cr.setLocation(this._doId, parentId, zoneId);
    }

    public beforeGenerate() {
        /**
         * Inheritors to override.
         */
    }

    public afterGenerate() {
        /**
         * Inheritors to override.
         */
    }

    public beforeDelete() {
        /**
         * Inheritors to override.
         */
    }

    public afterDelete() {
        /**
         * Inheritors to override.
         */
    }
}
