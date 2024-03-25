import Fetcher from "./fetcher";
import { type DataInfoT } from "../../lires_web/src/api/protocol";

export default class LiresAPI {

    _fetcher: Fetcher;
    _endpointGetter: () => string;
    _credentialGetter: () => string;

    constructor() {
        this._fetcher = new Fetcher();
    }

    public init(endpointGetter: () => string, credentialGetter: () => string): LiresAPI {
        this._fetcher.setBaseUrlGetter(endpointGetter);
        this._fetcher.setCredentialGetter(credentialGetter);
        return this;
    }

    async reqDatapointSummary( uid: string ): Promise<DataInfoT>{
        return await this._fetcher.get(`/api/datainfo/${uid}`).then(res=>res.json());
    }

    async reqDatapointAbstract( uid: string ): Promise<string>{
        return await this._fetcher.get(`/api/datainfo-supp/abstract/${uid}`).then(res=>res.text());
    }

}