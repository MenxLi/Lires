
type logLevel_t =  "debug" | "info" | "warn" | "error";

interface Logger_t{
    DEFAULT_LOGLEVEL: logLevel_t;
    LOGLEVEL_ORDER: logLevel_t[];
    name: string;
    info(s: string): void;
    warn(s: string): void;
    debug(s: string): void;
    error(s: string): void;
}

abstract class LoggerAbstract implements Logger_t{

    readonly DEFAULT_LOGLEVEL: logLevel_t = "info";
    readonly LOGLEVEL_ORDER: logLevel_t[] = [
        "debug", "info", "warn", "error"
    ]
    
    name: string;

    constructor(name: string){
        this.name = name;
    }

    info(s: string): void { 
        this.log(this.formatString(s, "info"), "info") ;
    };

    warn(s: string): void {
        this.log(this.formatString(s, "warn"), "warn") ;
    };
    
    debug(s: string): void {
        this.log(this.formatString(s, "debug"), "debug") ;
    };

    error(s: string): void {
        this.log(this.formatString(s, "error"), "error") ;
    }

    protected formatString(s: string, level: logLevel_t): string{
        return `[${this.name}/${level.toUpperCase()}] [${this.timeString}]: ${s}`
    }

    protected get timeString(): string{
        return new Date().toISOString();
    }

    /* Main method to print log */
    protected abstract log(s: string, level: logLevel_t): void;

    /* designation loglevel at current context */
    protected abstract get dstLevel(): logLevel_t;
}


export class Logger extends LoggerAbstract {
    protected log(s: string, level: logLevel_t){
        const dstLevelIdx = this.LOGLEVEL_ORDER.indexOf(this.dstLevel);
        const levelIdx = this.LOGLEVEL_ORDER.indexOf(level);
        if (levelIdx >= dstLevelIdx){
            console.log(s);
        }
    }

    protected get dstLevel(): logLevel_t {
        const url = new URL(window.location.href);
        
        // get loglevel at url
        // key set to "loglevel" or "ll"
        // e.g. a valid url: some.arbitrary.url?loglevel=info
        let ll = url.searchParams.get("loglevel");
        if (!ll){ ll = url.searchParams.get("ll") }

        if (!ll) {return this.DEFAULT_LOGLEVEL};

        if (["info", "warn", "debug", "error"].includes(ll)){
            // type assersion
            return <logLevel_t>ll;
        }

        else{ return this.DEFAULT_LOGLEVEL };
    }
}

export function getLogger(name: string): Logger_t{
    // Maybe initialize globalVar
    // Use as any to avoid typechecking failure
    const globalVar = (globalThis as any);
    const loggerKey = Symbol.for("Logger");
    let loggerStorage: any;
    let logger: Logger;

    if (!globalVar[loggerKey]){
        loggerStorage = new Object();
        globalVar[loggerKey] = loggerStorage;
    }
    else {
        loggerStorage = globalVar[loggerKey];
    }

    if (!loggerStorage[name]){
        logger = new Logger(name);
        loggerStorage[name] = logger;
    }
    else{
        logger = loggerStorage[name];
    }
    return logger;
}
