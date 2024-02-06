import Fetcher from "./fetcher";
import { type DataInfoT } from "../../lires_web/src/api/protocalT";

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
        console.log("requesting datapoint summary");
        return await this._fetcher.get(`/api/fileinfo/${uid}`).then(res=>res.json());
    }

}