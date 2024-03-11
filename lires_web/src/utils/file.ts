
interface ExtractFileTypes {
    citation: File[];
    document: File[];
    unknown: File[];
}
export function classifyFiles(files: FileList | File[]): ExtractFileTypes {
    function extensionIn(fName: string, extList: string[]): boolean {
        const fExt = fName.split('.').pop()?.toLowerCase();
        for (const ext of extList){
            if (fExt === ext) return true;
        }
        return false;
    }

    function _isImageFile(file: File): boolean {
        if (file.type.startsWith("image/") || extensionIn(file.name, ["jpg", "jpeg", "png", "gif", "bmp", "svg", "webp"])) {
            return true;
        }
        return false;
    }
    function _isPDFFile(file: File): boolean {
        if (file.type === "application/pdf" || extensionIn(file.name, ["pdf"])) { return true; }
        return false;
    }

    function _isHTMLFile(file: File): boolean {
        if (file.type === "text/html" || extensionIn(file.name, ["html"])) { return true; }
        return false;
    }

    function isCitationFile(file: File): boolean {
        if (file.type === "text/plain" || extensionIn(file.name, ["txt", "bib", "bibtex", "nbib", "enw", "ris"])) {
            return true;
        }
        return false;
    }
    function isDocumentFile(file: File): boolean {
        if (_isPDFFile(file) || _isHTMLFile(file) || _isImageFile(file)) {
            return true;
        }
        return false;
    }

    const citation: File[] = [];
    const document: File[] = [];
    const unknown: File[] = [];
    for (let i = 0; i < files.length; i++) {
        if (isCitationFile(files[i])) {
            citation.push(files[i]);
        } else if (isDocumentFile(files[i])) {
            document.push(files[i]);
        }
        else {
            unknown.push(files[i]);
        }
    }
    return {
        citation,
        document,
        unknown
    }
}