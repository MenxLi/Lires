
<script setup lang="ts">
    import { ref, computed } from 'vue';
    import QueryDialog from '../common/QueryDialog.vue';
    import TagSelectorWithEntry from '../tags/TagSelectorWithEntry.vue';
    import { useConnectionStore, useUIStateStore } from '@/state/store';
    import { DataTags } from '../../core/tag';
    import type { DataPoint } from '../../core/dataClass';
    import type { TagStatus } from '@/state/interface';
    import Toggle from '../common/Toggle.vue';
    import { getBibtexTemplate, type BibtexTypes } from './bibtexUtils';
    import { BibtexCollector } from './bibtexUtils';
    import { FileSelectButton } from '../common/fragments';
    import { classifyFiles } from '../../utils/file';


    const uiState = useUIStateStore();
    const conn = useConnectionStore().conn;
    // internal states that control the dialog
    const show_ = ref(false);
    const datapoint_ = ref<DataPoint | null>(null);
    const bibtex_ = ref("");
    const url_ = ref("");
    const file_ = ref<File | null>(null);
    const tagStatus_ = ref<TagStatus>({
        all: new DataTags(),
        checked: new DataTags(),
        unfolded: new DataTags(),
    });

    // methods
    function save(){
        const uploadState = {
            uuid: datapoint_.value? datapoint_.value.summary.uuid : null,
            bibtex: bibtex_.value,
            tags: Array.from(tagStatus_.value.checked),
            url: url_.value,
            file: file_.value,
        }           // create a capture of the current state
        close();    // close the dialog and clear the state
        uiState.showPopup("Saving entry...", "info")
        conn.updateDatapoint(uploadState.uuid, {
            bibtex: uploadState.bibtex, 
            tags: uploadState.tags, 
            url: uploadState.url
        }).then(
            (dSummary) => {
                if (!uploadState.file){ uiState.showPopup("Saved", "success"); }
                else{
                    uiState.showPopup("Uploading document...", "info");
                    conn.uploadDocument(dSummary.uuid, uploadState.file).then(
                        (_) => { uiState.showPopup("Saved", "success"); },
                        () => uiState.showPopup("Failed to upload document", "error")
                    )
                }
            },
            () => uiState.showPopup("Failed to save", "error")
        )
    }
    const newTagInput = ref("");

    function show({
        datapoint = null, 
        bibtex = null, 
        url = null, 
        tags = null,
    }: {
        datapoint: DataPoint | null,
        bibtex: string | null,
        url: string | null,
        tags: DataTags | null | string[]
    }){
        // only one instance of data editor is allowed
        if (uiState.dataEditorOpened){ return; }
        else { uiState.dataEditorOpened = true; }

        if (datapoint!==null){
            datapoint_.value = datapoint;
            bibtex_.value = datapoint.summary.bibtex;
            url_.value = datapoint.summary.url;
            if (tags === null) tags = new DataTags(datapoint.summary.tags);
        }
        if (bibtex!==null){ bibtex_.value = bibtex; }
        if (url!==null){ url_.value = url; }
        if (tags!==null){
            if (Array.isArray(tags)){ tags = new DataTags(tags); }
            tagStatus_.value = {
                all: new DataTags(uiState.tagStatus.all).union(tags),
                checked: tags,
                unfolded: tags.allParents()
            }}
        else{
            tagStatus_.value = {
                all: new DataTags(uiState.tagStatus.all),
                checked: new DataTags(uiState.tagStatus.checked),
                unfolded: new DataTags(uiState.tagStatus.unfolded)
            }
        }
        show_.value = true;
    }
    function close(){
        // clear all states
        show_.value = false;
        datapoint_.value = null;
        bibtex_.value = "";
        url_.value = "";
        tagStatus_.value = {
            all: new DataTags(uiState.tagStatus.all),
            checked: new DataTags(uiState.tagStatus.checked),
            unfolded: new DataTags(uiState.tagStatus.unfolded)
        }
        file_.value = null;
        newTagInput.value = "";
        isInDrag.value = false;
        uiState.dataEditorOpened = false;
    }
    function isShown(){
        return show_.value;
    }
    function setDocumentFile(f: File): boolean{
        if (datapoint_.value){
            uiState.showPopup("Document can only be added to new entry", "error");
            return false;
        }
        if (!classifyFiles([f]).document){
            uiState.showPopup("Unsupported file", "error");
            return false;
        }
        file_.value = f;
        // if bibtext is empty, try to extract from file
        console.log("file selected");
        if (bibtex_.value.trim().length === 0){
            console.log("try to extract bibtex from file");
            const fname = f.name;
            const ftime = f.lastModified;
            const bib = getBibtexTemplate(bibtexTemplateSelection.value, {
                title: fname,
                year: new Date(ftime).getFullYear(),
            });
            bibtex_.value = bib;
        }
        return true;
    }
    function loadFiles(files: FileList | File[]): boolean{
        // load the first file 
        let ret = false;
        if (!files || files.length === 0) return ret;

        const classified = classifyFiles(files);
        if (classified.citation.length > 1 || classified.document.length > 1){
            uiState.showPopup("Only one citation and one document are allowed", "error");
        }
        if (classified.citation.length == 0 && classified.document.length == 0){
            console.log("[Error] Got files: ", files);
            uiState.showPopup("Unsupported file type", "error");
        }
        if (classified.citation.length > 0){
            // load to bibtex
            const file = classified.citation[0];
                if (file.size < 64*1024){
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        const content = e.target?.result as string;
                        bibtex_.value = content;
                    }
                    reader.readAsText(file);
                    ret = true;
                }
                else{ uiState.showPopup("Text file too large", "error"); }
        }
        if (classified.document.length > 0){
            ret = setDocumentFile(classified.document[0]);
        }

        return ret;
    }
    defineExpose({ show, close, isShown, loadFiles })

    const showBibtexTemplate = ref(false);
    const bibtexTemplateSelection = ref("article" as BibtexTypes);
    const bibtexTemplate = computed(()=>getBibtexTemplate(bibtexTemplateSelection.value))

    type BibSourceT = 'arxiv' | 'doi' | 'webpage'
    const showBibSourceInput = ref(false);
    const bibSourceType = ref("arxiv" as BibSourceT);
    const __bibSourceMap: Record<BibSourceT, (src: string) => Promise<{bibtex: string, url: string}>> = {
        arxiv: (src: string) => BibtexCollector.fromArxiv(src),
        doi: (src: string) => BibtexCollector.fromDoi(src),
        webpage: (src: string) => BibtexCollector.fromWebpage(src),
    }
    const __bibSourceHintMap: Record<BibSourceT, string> = {
        arxiv: "e.g. 2106.00001",
        doi: "e.g. 10.1145/344779.344937",
        webpage: "e.g. https://news.mit.edu/2021/xxx",
    }
    const bibSourceInput = ref("");
    function insertBibtexFromSource(src: string){
        uiState.showPopup("Fetching from BibTeX source...", "info");
        showBibSourceInput.value = false;   // close input
        bibSourceInput.value = "";        // clear input
        __bibSourceMap[bibSourceType.value](src).then(
            (res) => {
                uiState.showPopup("Obtained bibtex from source", "success");
                bibtex_.value = res.bibtex;
                url_.value = res.url
            },
            () => {
                uiState.showPopup("Failed to fetch from source", "error");
            }
        )
    }

    // Drag and drop to insert bibtex or file
    const isInDrag = ref(false);
    const dataEditorComponent = ref<HTMLDivElement | null>(null);
    const __onDragover = (e: DragEvent) => {
        e.preventDefault();
        isInDrag.value = true;
    }
    const __onDragEnd = (e: DragEvent) => {
        e.preventDefault();
        isInDrag.value = false;
    }
    const __onDragDrop = (e: DragEvent) => {
        e.preventDefault();
        const files = e.dataTransfer?.files;
        if (files) loadFiles(files);
        isInDrag.value = false;
    }
</script>

<template>
    <QueryDialog v-model:show="showBibtexTemplate" 
    @on-accept="()=>{bibtex_=bibtexTemplate; showBibtexTemplate=false}" 
    @on-cancel="showBibtexTemplate=false" :z-index=102 title="Select template">
        <div :style="{
            display: 'flex',
            flexDirection: 'column',
            gap: '10px',
            padding: '10px',
            width: '100%',
            height: '100%',
        }">
            <Toggle @on-check="bibtexTemplateSelection='article'" :checked="bibtexTemplateSelection=='article'">Article</Toggle>
            <Toggle @on-check="bibtexTemplateSelection='inproceedings'" :checked="bibtexTemplateSelection=='inproceedings'">Inproceedings</Toggle>
            <Toggle @on-check="bibtexTemplateSelection='webpage'" :checked="bibtexTemplateSelection=='webpage'">Webpage</Toggle>
            <Toggle @on-check="bibtexTemplateSelection='misc'" :checked="bibtexTemplateSelection=='misc'">Misc</Toggle>
        </div>
    </QueryDialog>

    <QueryDialog v-model:show="showBibSourceInput" @on-cancel="showBibSourceInput=false" @on-accept="()=>{
        insertBibtexFromSource(bibSourceInput);
    }" :z-index=102 title="Source input">
        <div :style="{margin: '10px'}">
            <fieldset :style="{
                display: 'flex',
                flexDirection: 'row',
                gap: '10px',
                border: '1px solid var(--color-border)',
            }">
                <legend>Source</legend>
                <div class="bibsource-container">
                    <input type="radio" id="bibsource-arxiv" name="bibSource" value="arxiv" v-model="bibSourceType">
                    <legend for="bibsource-arxiv">arxiv</legend>
                </div>
                <div class="bibsource-container">
                    <input type="radio" id="bibsource-doi" name="bibSource" value="doi" v-model="bibSourceType">
                    <legend for="bibsource-doi">doi</legend>
                </div>
                <div class="bibsource-container">
                    <input type="radio" id="bibsource-webpage" name="bibSource" value="webpage" v-model="bibSourceType">
                    <legend for="bibsource-webpage">webpage</legend>
                </div>
            </fieldset>
            <input type="text" v-model="bibSourceInput" :placeholder="__bibSourceHintMap[bibSourceType]" :style="{
                width: '100%', marginTop: '10px'
            }"/>
        </div>
    </QueryDialog>

    <QueryDialog 
        v-model:show="show_" :title="datapoint_?datapoint_.authorAbbr():'new'" :show-cancel="false"
        @on-accept="save" @on-cance="close" @on-close="close"
    >
        <div 
            id="data-editor-main" ref="dataEditorComponent" 
            @dragover="__onDragover" @drop="__onDragDrop" @dragend="__onDragEnd"
        >
            <div v-if="!isInDrag">
                <div id="inputDiv">
                    <div id="inputLeft">
                        <div id="bibtexArea">
                            <div class="horizontal">
                                <label for="bibtex">Bibtex</label>
                                <div id="bibtexSource" class="horizontal">
                                    <div class="button" @click="showBibtexTemplate=true">template</div>
                                    <div class="button" @click="showBibSourceInput=true">from-source</div>
                                </div>
                            </div>
                            <textarea id="bibtex" v-model="bibtex_" placeholder="bibtex / enw / nbib" 
                                class="scrollable wrapword" style="resize: none"></textarea>
                        </div>
                        <div id="urlArea">
                            <label for="url">URL: </label>
                            <input id="url" v-model="url_" placeholder="url" type="text">
                        </div>
                    </div>
                    <div id="inputRight">
                        <TagSelectorWithEntry 
                            v-model:tag-status="tagStatus_"
                            v-model:tag-input-value="newTagInput"
                        ></TagSelectorWithEntry>
                    </div>
                </div>
                <div style="display: flex; justify-content: center; align-items: center; padding-inline: 15px;" v-if="datapoint_===null">
                    <div class="hr"></div>
                    <div style="margin-top: 5px; text-wrap: nowrap; white-space: nowrap; margin-inline: 5px;">
                        <!-- file selection -->
                        {{ file_?file_.name:"" }}
                        <FileSelectButton text="Select document" :action="setDocumentFile" :as-link="true" 
                            style="cursor:pointer; padding: 3px; border-radius: 5px" v-if="!file_"
                        />
                        <a @click="file_=null" style="cursor: pointer; padding: 3px; border-radius: 5px;" v-else> (Remove) </a>
                    </div>
                    <div class="hr"></div>
                </div>
            </div>
            <div v-else>
                <div style="
                    display: flex; flex-direction: column; align-items: center; justify-content: center; 
                    /* height: 470px; width: 630px */
                    height: 430px; width: 590px; border: 5px dashed var(--color-border); border-radius: 10px; margin: 15px;
                ">
                    <div style="font-size: 20px; font-weight: bold; margin-bottom: 10px;">Drop to insert citation or document</div>
                    <div style="font-size: 12px; opacity: 0.5;">(only support bibtex/enw/nbib)</div>
                </div>
            </div>
        </div>
    </QueryDialog>
</template>

<style scoped>
    #inputDiv {
        display: flex;
        flex-direction: row;
        width: 100%;
        gap: 10px;
        padding-left: 15px;
        padding-right: 15px;
    }

    div.hr{
        width: 100%;
        height: 1px;
        background-color: var(--color-border);
    }

    label {
        font-weight: bold;
    }
    div.horizontal{
        display: flex;
        flex-direction: row;
        align-items: center;
        gap: 10px;
        width: 100%;
    }
    div#bibtexSource{
        font-size: small;
        margin-left: 10px;
    }
    div#bibtexSource div.button{
        cursor: pointer;
        opacity: 0.2;
        transition: all 0.2s ease-in-out;
    }
    div#bibtexSource div.button:hover{
        cursor: pointer;
        opacity: 1;
        color: var(--color-theme);
        text-decoration: underline;
    }

    #inputLeft, #inputRight{
        display: flex;
        flex-direction: column;
        width: 100%;
        gap: 10px;
    }

    textarea, input[type="text"]{
        border: 1px solid var(--color-border);
        border-radius: 5px;
        background-color: var(--color-background);
        color: var(--color-text);
        width: 100%
    }
    div#bibtexArea{
        display: flex;
        flex-direction: column;
        align-items: flex-start;
    }
    div#bibtexArea textarea {
        min-width: 300px;
        width: 100%;
        height: 420px;
        padding: 5px;
        font-size: medium;
        font-family: monospace;
    }
    .wrapword {
        white-space: -moz-pre-wrap !important;  /* Mozilla, since 1999 */
        white-space: -webkit-pre-wrap;          /* Chrome & Safari */ 
        white-space: -pre-wrap;                 /* Opera 4-6 */
        white-space: -o-pre-wrap;               /* Opera 7 */
        white-space: pre-wrap;                  /* CSS3 */
        word-wrap: break-word;                  /* Internet Explorer 5.5+ */
        word-break: break-all;
        /* white-space: normal; */
    }

    div#urlArea {
        display: flex;
        flex-direction: row;
        align-items: center;
        gap: 5px
    }
    div#urlArea > input[type="text"]{
        width: 100%
    }

    div#tagSelector {
        width: 100%;
        min-width: 300px;
        height: 420px;
        overflow: scroll;
        padding: 5px;
    }
    button#addNewTag{
        width: 80px;
    }

    div.bibsource-container{
        display: flex;
        flex-direction: row;
        align-items: center;
        gap: 5px;
    }

</style>