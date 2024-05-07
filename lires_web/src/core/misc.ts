
const __themeChangeCallbacks: Array<Function> = [];

export class ThemeMode{

  static registerThemeChangeCallback(callback: Function){
    if (__themeChangeCallbacks.indexOf(callback) !== -1){
      return;
    }
    __themeChangeCallbacks.push(callback);
  }

  static unregisterThemeChangeCallback(callback: Function){
    const idx = __themeChangeCallbacks.indexOf(callback);
    if (idx !== -1){
      __themeChangeCallbacks.splice(idx, 1);
    }
  }

  /*
  https://stackoverflow.com/a/68824350
  toggle to switch classes between .light and .dark
  if no class is present (initial state), then assume current state based on system color scheme
  if system color scheme is not supported, then assume current state is light
  */
  static toggleDarkMode() {
    if (document.documentElement.classList.contains("light")) {
      ThemeMode.setDarkMode(true);
    } else if (document.documentElement.classList.contains("dark")) {
      ThemeMode.setDarkMode(false);
    }
    else {
      if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        ThemeMode.setDarkMode(true);
      } else {
        ThemeMode.setDarkMode(true);
      }
    }
  }

  // return true if default color scheme is dark
  static isDefaultDarkMode(){
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return true;
    }
    else{
      return false;
    }
  }

  // return true if current color scheme is dark
  static isDarkMode(){
    if (document.documentElement.classList.contains("light")){
      return false;
    }
    else if (document.documentElement.classList.contains("dark")){
      return true;
    }
    else{
      return false;   // default to light mode
    }
  }

  // set default color scheme to be in according to session storage or system color scheme
  static setDefaultDarkMode(){
    const localStorageThemeMode = localStorage.getItem("themeMode");
    if (localStorageThemeMode === "dark"){ ThemeMode.setDarkMode(true); }
    else if(localStorageThemeMode == "light"){ ThemeMode.setDarkMode(false);}
    else{ // null
      if (ThemeMode.isDefaultDarkMode() && !ThemeMode.isDarkMode()){
        this.setDarkMode(true, false);
      }
    }
  }

  // set color scheme
  static setDarkMode(mode: boolean, save: boolean = true){
    if (mode){
      document.documentElement.classList.remove("light")
      document.documentElement.classList.add("dark")
    }
    else{
      document.documentElement.classList.remove("dark")
      document.documentElement.classList.add("light")
    }
    for (let callback of __themeChangeCallbacks){
      callback(mode);
    }  
    if (save){
      const _newMode = mode?"dark":"light";
      if (localStorage.getItem("themeMode") !== _newMode){
        localStorage.setItem("themeMode", mode?"dark":"light");
      }
    }
  }

  static getThemeMode(): 'light' | 'dark' | 'auto'{
    const _settings = localStorage.getItem("themeMode");
    if (_settings === "dark"){
      return "dark";
    }
    else if (_settings === "light"){
      return "light";
    }
    else{
      return "auto";
    }
  }

  static clear(){
    document.documentElement.classList.remove("dark")
    document.documentElement.classList.remove("light")
    this.setDefaultDarkMode();
    localStorage.removeItem("themeMode");
  }
}

export function inPlacePopByValue(arr: Array<any>, toPop: any){
  let continuePop = true;
  let idx;
  while(continuePop){
    idx = arr.indexOf(toPop)
    if (idx === -1){
      continuePop = false;
    }
    else{
      arr.splice(idx, 1);
    }
  }
}

export function isChildDOMElement(child: HTMLElement, parent: HTMLElement){
  let node = child.parentNode;
  while (node != null){
    if (node == parent){
      return true;
    }
    node = node.parentNode;
  }
  return false;
}

export function deepCopy(obj: any) {
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }

  let copy: any = Array.isArray(obj) ? [] : {};

  for (let key in obj) {
    copy[key] = deepCopy(obj[key]);
  }

  return copy;
}

// return a list of datapoints that are sorted by scores, and sorted scores
// - reverse: if false, sort in descending order
export function sortByScore<T>(arr: T[], scores: number[], reverse = false): [T[], number[]]{
    if (arr.length !== scores.length){
        throw new Error("arr.length !== scores.length");
    }

    const arr_score = new Array();
    for (let i = 0; i < arr.length; i++){
        arr_score.push([arr[i], scores[i]]);
    }

    let arr_score_sorted;
    if (reverse){
        arr_score_sorted = arr_score.sort((a, b) => a[1] - b[1]);
    }
    else{
        arr_score_sorted = arr_score.sort((a, b) => b[1] - a[1]);
    }

    const ret = new Array();
    const ret2 = new Array();
    for (const item of arr_score_sorted){
        ret.push(item[0]);
        ret2.push(item[1]);
    }

    return [ret, ret2];
}