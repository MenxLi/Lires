import { getLogger } from "./logging.js";

export function setValueChangeOnHover<elem_t extends Element, val_t>(
    elem: elem_t, 
    getMethod: (elem: elem_t) => val_t, 
    setMethod: (elem: elem_t, val: val_t) => void, 
    getNewValMethod: ()=>val_t
) {
    let logger = getLogger("memo");
    let oldVal: val_t;
    elem.addEventListener("mouseenter", () => {
        oldVal = getMethod(elem);
        setMethod(elem, getNewValMethod());

        // debug
        logger.debug("Stored old val: " + String(oldVal));
    });
    elem.addEventListener("mouseout", () => {
        setMethod(elem, oldVal);

        // debug
        logger.debug("Restored to old val.");
    })
    
}


export function removeChilds(parent: HTMLElement){
    while (parent.lastChild){
        parent.removeChild(parent.lastChild);
    }
}
