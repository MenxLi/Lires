
export class ThemeMode{
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
    const sessionStorageThemeMode = sessionStorage.getItem("themeMode");
    if (sessionStorageThemeMode === "dark"){ ThemeMode.setDarkMode(true); }
    else if(sessionStorageThemeMode == "light"){ ThemeMode.setDarkMode(false);}
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
    sessionStorage.setItem("themeMode", mode?"dark":"light");
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