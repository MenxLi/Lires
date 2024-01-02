
const __themeChangeCallbacks: Array<Function> = [];

export class ThemeMode{

  static registerThemeChangeCallback(callback: Function){
    __themeChangeCallbacks.push(callback);
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
        ThemeMode.toggleDarkMode();
      }
    }
  }

  // set color scheme
  static setDarkMode(mode: boolean){
    if (mode){
      document.documentElement.classList.remove("light")
      document.documentElement.classList.add("dark")
    }
    else{
      document.documentElement.classList.remove("dark")
      document.documentElement.classList.add("light")
    }
    const _newMode = mode?"dark":"light";
    if (localStorage.getItem("themeMode") !== _newMode){
      localStorage.setItem("themeMode", mode?"dark":"light");
      for (let callback of __themeChangeCallbacks){
        callback(mode);
      }  
    }
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
