

class Fetcher {

    declare _baseUrlGetter: ()=>string;
    declare _tokenGetter: ()=>string;
    declare _sessionIDGetter: ()=>string;

    constructor({
        baseUrlGetter = ()=>'', 
        tokenGetter = ()=>'', 
        sessionIDGetter = ()=>'' 
    }: {
        baseUrlGetter?: ()=>string,
        tokenGetter?: ()=>string,
        sessionIDGetter?: ()=>string
    }) {
        this._baseUrlGetter = baseUrlGetter;
        this._tokenGetter = tokenGetter;
        this._sessionIDGetter = sessionIDGetter;
    }
    public get baseUrl(): string { return this._baseUrlGetter(); }
    public get token(): string { return this._tokenGetter(); }
    public get sessionID(): string { return this._sessionIDGetter(); }

    public async get(path: string, params: Record<string, string> = {}): Promise<Response> {
        const urlWithParams = new URL(`${this._baseUrlGetter()}${path}`);
        Object.keys(params).forEach(key => urlWithParams.searchParams.append(key, params[key]));
        return await this._fetch(urlWithParams.toString(), 
        {
            method: 'GET',
        });
    }

    public async post(path: string, body: Record<string, any> = {}): Promise<Response> {
        const form = new FormData();
        for (const key in body) {
            let value = body[key];
            if (value instanceof Array) {
                value = JSON.stringify(value);
            }
            form.append(key, value);
        }
        return await this._fetch(`${this._baseUrlGetter()}${path}`, 
        {
            method: 'POST',
            body: form
        });
    }

    public async put(path: string, file: File): Promise<Response> {
        const form = new FormData();
        form.append('key', this._tokenGetter());
        form.append('file', file);
        return await this._fetch(`${this._baseUrlGetter()}${path}`, 
        {
            method: 'PUT',
            body: form
        });
    }

    public async delete(path: string, body: Record<string, any> = {}): Promise<Response> {
        const form = new FormData();
        for (const key in body) {
            let value = body[key];
            if (value instanceof Array) {
                value = JSON.stringify(value);
            }
            form.append(key, value);
        }
        form.append('key', this._tokenGetter());
        return await this._fetch(`${this._baseUrlGetter()}${path}`, 
        {
            method: 'DELETE',
            body: form
        });
    }

    private async _fetch(path: string, options?: RequestInit): Promise<Response> {

        // inject token
        if (options?.method === 'GET') {
            const url = new URL(path);
            url.searchParams.append('key', this._tokenGetter());
            url.searchParams.append('session_id', this._sessionIDGetter());
            path = url.toString();
        }

        if (options?.method === 'POST' || options?.method === 'PUT' || options?.method === 'DELETE') {
            if (options.body === undefined) {
                options.body = JSON.stringify({key: this._tokenGetter()});
            }
            else if (typeof options.body === 'string') {
                // assume it is JSON
                options.body = JSON.stringify({
                    key: this._tokenGetter(), 
                    session_id: this._sessionIDGetter(),
                    ...JSON.parse(options.body)});
            }
            else if (options.body instanceof FormData) {
                if (!options.body.has('key')) {
                    options.body.append('key', this._tokenGetter());
                }
                if (!options.body.has('session_id')) {
                    options.body.append('session_id', this._sessionIDGetter());
                }
            }
            else {
                throw new Error('Not implemented body type');
            }
        }

        const response = await fetch(path, options);
        if (!response.ok) {
            throw new Error(`Request failed with status ${response.status}`);
        }
        return response;
    }
}

export default Fetcher;
