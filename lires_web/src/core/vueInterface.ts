import type { Router } from "vue-router";

export class URLRouter{
    router: Router;
    constructor(router: Router){
        this.router = router;
    }
    getURLParams() : Record<string, string>{
        const params = {} as Record<string, string>;
        const query = this.router.currentRoute.value.query;
        for(const key in query){
            params[key] = query[key] as string;
        }
        return params;
    }
    setURLParam(k: string, v: string){
        const params = this.getURLParams();
        params[k] = v;
        this.router.push({ query: params });
    }
    updateURLWithParam(k: string, v: string) : string{
        const params = this.getURLParams();
        params[k] = v;
        return this.router.resolve({ query: params }).href;
    }
}