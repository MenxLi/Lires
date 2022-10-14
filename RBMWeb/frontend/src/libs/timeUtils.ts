import {getLogger} from "./logging.js";

/*
 * return locale time in format: yyyy-mm-dd hh:mm:ss
* */
export function utcStamp2LocaleStr(stamp: number, isSecond = false): string{
    if (isSecond) stamp *= 1000;
    const d = new Date(stamp);

    let year = d.getFullYear().toString();
    if (year.length !== 4){
        year = "0".repeat(4-year.length) + year;
    }
    let month = (d.getMonth() + 1).toString();
    if (month.length === 1){
        month = "0" + month;
    }
    let date = (d.getDate()).toString();
    if (date.length === 1){
        date = "0" + date;
    }

    let ret = `${year}-${month}-${date} `
    const options = {
        // hour12: false as const,
        hourCycle: 'h23' as const,      // force display midnight hour as 00
        hour:  "2-digit" as const,
        minute: "2-digit" as const,
        second: "2-digit" as const
    };
    ret += d.toLocaleTimeString([], options);
 
    return ret;
}


/*
 * set a time stamp to a datetime-local input field
* */
export function stamp2Input(stamp: number, inputElem: HTMLInputElement, isSecond = false): void {
    const logger = getLogger("memo");
    const localeTimeStr = utcStamp2LocaleStr(stamp, isSecond).replace(" ", "T");
    logger.debug(`Setting time to datetime-local input - ${localeTimeStr} (${stamp2Input.name})`)
    inputElem.value = localeTimeStr;
}

/*
 * read from a datetime-local input field and return stamp
* */
export function input2Stamp(inputElem: HTMLInputElement, returnSecond = false): number{
    const rawStr = inputElem.value;
    if (!rawStr){
        // Empty...
        throw new Error("Empty time string");
    }
    const dt = new Date(rawStr);
    let stamp = dt.getTime();
    if (returnSecond){
        stamp /= 1000;
    }
    return stamp;
}
