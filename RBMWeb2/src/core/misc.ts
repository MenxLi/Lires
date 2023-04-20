
// https://stackoverflow.com/a/68824350
// toggle to switch classes between .light and .dark
// if no class is present (initial state), then assume current state based on system color scheme
// if system color scheme is not supported, then assume current state is light
export function toggleDarkMode() {
  if (document.documentElement.classList.contains("light")) {
    document.documentElement.classList.remove("light")
    document.documentElement.classList.add("dark")
  } else if (document.documentElement.classList.contains("dark")) {
    document.documentElement.classList.remove("dark")
    document.documentElement.classList.add("light")
  } else {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      document.documentElement.classList.add("dark")
    } else {
      document.documentElement.classList.add("light")
    }
  }
}

export function isDefaultDarkMode(){
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return true;
  }
  else{
    return false;
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