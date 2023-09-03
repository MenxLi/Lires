import { open as tauriOpen } from '@tauri-apps/api/shell';
import { platformType } from '../config';

// not used for now, a backup for the future
export function resolveAbsoluteURL(url: string){
    const baseUrl = new URL(import.meta.url);
    baseUrl.pathname = baseUrl.pathname.replace(/\/[^/]*$/, '/');
    return new URL(url, baseUrl).href;
}

export function formatAuthorName(author: string): string{
    // the author name may be in the form of 
    // <Family Name>, <Given Name> <...>
    // <Given Name> <...> <Family Name> 
    // make sure formatted author is named as <Family Name>, <Given Name> in lower case

    author = author.trim().toLowerCase().replace(/-/g, "");

    let formattedAuthor = author.trim(); // Remove leading/trailing whitespace
    // Check if the author name contains a comma
    if (formattedAuthor.includes(',')) {
        const [familyName, givenName] = formattedAuthor.split(',', 2);
        formattedAuthor = `${familyName.trim()}, ${givenName.trim()}`;
    } else {
        // check if no space in the author name
        if (formattedAuthor.indexOf(' ') === -1){
            return formattedAuthor;
        }

        // If there is no comma, assume the last space separates the family name and given name
        const lastIndex = formattedAuthor.lastIndexOf(' ');
        const familyName = formattedAuthor.slice(lastIndex + 1);
        const givenName = formattedAuthor.slice(0, lastIndex);
        formattedAuthor = `${familyName.trim()}, ${givenName.trim()}`;
    }

    return formattedAuthor;
}

/* detect if an element is visible in the viewport */
export function isVisiable(el: HTMLElement): boolean{
    if (!el){
        // console.log("no element");
        return false;
    }
    if (el.style.display === "none"){
        // console.log("display none");
        return false;
    }
    if (el.style.visibility === "hidden"){
        // console.log("visibility hidden");
        return false;
    }
    if (el.style.opacity === "0"){
        // console.log("opacity 0");
        return false;
    }

    const rect = el.getBoundingClientRect();
    // console.log(rect.top, rect.bottom, window.innerHeight)
    if (rect.top < 0){
        return false;
    }
    if (rect.bottom > window.innerHeight){
        return false;
    }
    return true;
}

// from internet
export async function copyToClipboard(textToCopy: string): Promise<boolean> {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(textToCopy);
      return true;
    } else {
      const textarea = document.createElement('textarea');
      textarea.value = textToCopy;
  
      // Move the textarea outside the viewport to make it invisible
      textarea.style.position = 'absolute';
      textarea.style.left = '-99999999px';
  
      document.body.prepend(textarea);
  
      // highlight the content of the textarea element
      textarea.select();
  
      let _error = false;
      try {
        document.execCommand('copy');
      } catch (err) {
        console.log(err);
        _error = true;
      } finally {
        textarea.remove();
      }
      return !_error;
    }
  }

export function openURLExternal(url: string){
    if (platformType() == "tauri"){
        tauriOpen(url);
    }
    else{
        window.open(url, "_blank");
    }
}

// Execute a function after a delay,
// if the function is called again before the delay, the previous call will be canceled
// delay is in milliseconds
export function lazify(func: Function, delay: number): (...args: any[]) => void{
    let timerId: number | null = null;
    return function(...args: any[]){
        if (timerId){
            window.clearTimeout(timerId);
        }
        timerId = window.setTimeout(() => {
            func(...args);
            timerId = null;
        }, delay);
    }
}