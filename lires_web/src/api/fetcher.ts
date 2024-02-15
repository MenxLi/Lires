

class Fetcher {

    declare _baseUrlGetter: ()=>string;
    declare _tokenGetter: ()=>string;

    constructor() {
        this._baseUrlGetter = () => '';
        this._tokenGetter = () => '';
    }
    public get baseUrl(): string { return this._baseUrlGetter(); }
    public get token(): string { return this._tokenGetter(); }
    public setBaseUrlGetter(g: ()=>string) {
        this._baseUrlGetter = g;
    }
    public setCredentialGetter(g: ()=>string) {
        this._tokenGetter = g;
    }

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
            form.append(key, body[key]);
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

    public async delete(path: string): Promise<Response> {
        const form = new FormData();
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
            path += path.includes('?') ? '&' : '?';
            path += `key=${this._tokenGetter()}`;
        }

        if (options?.method === 'POST' || options?.method === 'PUT' || options?.method === 'DELETE') {
            if (options.body === undefined) {
                options.body = JSON.stringify({key: this._tokenGetter()});
            }
            else if (typeof options.body === 'string') {
                // assume it is JSON
                options.body = JSON.stringify({key: this._tokenGetter(), ...JSON.parse(options.body)});
            }
            else if (options.body instanceof FormData) {
                if (!options.body.has('key')) {
                    options.body.append('key', this._tokenGetter());
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
