import DCInterface from "./DCInterface";

export default class ObjectStore {
    private objStore: {[doId: number]: DCInterface} = {}

    public putObj(doId: number, distObj: DCInterface) {
        this.objStore[doId] = distObj;
    }

    public getObj(doId: number) {
        return this.objStore[doId];
    }

    public removeObj(doId: number) {
        delete this.objStore[doId]
    }
}
