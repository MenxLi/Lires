
<script setup lang="ts">
    import { ref, computed, watch } from 'vue';
    import QueryDialog from '../common/QueryDialog.vue';
    import TagSelectorWithEntry from '../tags/TagSelectorWithEntry.vue';
    import { useUIStateStore } from '../store';
    import { DataTags } from '../../core/tag';
    import { ServerConn } from '../../api/serverConn';
    import type { DataPoint } from '../../core/dataClass';
    import type { TagStatus } from '../interface';
    import Toggle from '../common/Toggle.vue';
    import { getBibtexTemplate, type BibtexTypes } from './bibtexUtils';
    import { BibtexCollector } from './bibtexUtils';

    const props = defineProps<{
        datapoint: DataPoint | null,
        show: boolean,
    }>();

    const emits = defineEmits<{
        (e: "update:show", show: boolean): void
    }>();

    const show = computed({
        get: () => props.show,
        set: (newShow: boolean) => emits("update:show", newShow) 
    });

    const uiState = useUIStateStore();
    // data ref
    const bibtex = ref("");
    const url = ref("");
    const tagStatus = ref<TagStatus>({
        all: new DataTags(),
        checked: new DataTags(),
        unfolded: new DataTags(),
    });

    // methods
    function save(){
        let uuid = null;
        if (props.datapoint){
            uuid = props.datapoint.summary.uuid;
        }
        show.value = false;
        uiState.showPopup("Saving entry...", "info")
        new ServerConn().editData(uuid, bibtex.value, Array.from(tagStatus.value.checked), url.value).then(
            (_) => {
                uiState.showPopup("Saved", "success");
            },
            () => uiState.showPopup("Failed to save", "error")
        )
    }
    const newTagInput = ref("");

    watch(show, (newShow) => {
        // init data on every showup!
        if (newShow){
            if (props.datapoint){ bibtex.value = props.datapoint.summary.bibtex; }
            else { bibtex.value = "";}
            if (props.datapoint){ url.value = props.datapoint.summary.url; }
            else { url.value = "";}
            tagStatus.value = {
                all: new DataTags(uiState.tagStatus.all),
                checked: props.datapoint? new DataTags(props.datapoint.summary.tags) : new DataTags(uiState.tagStatus.checked),
                unfolded: props.datapoint? 
                        new DataTags(props.datapoint.summary.tags).allParents():
                        new DataTags(uiState.tagStatus.unfolded)
            };
            newTagInput.value = "";
            isInDrag.value = false;
        }
    })

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
                bibtex.value = res.bibtex;
                url.value = res.url
            },
            () => {
                uiState.showPopup("Failed to fetch from source", "error");
            }
        )
    }

    // Drag and drop to insert bibtex
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
        if (files && files.length > 0){
            const file = files[0];
            if (file.size < 64*1024){
                const reader = new FileReader();
                reader.onload = (e) => {
                    const content = e.target?.result as string;
                    bibtex.value = content;
                }
                reader.readAsText(file);
            }
            else{
                uiState.showPopup("File too large", "error");
            }
        }
        isInDrag.value = false;
    }
</script>

<template>
    <QueryDialog v-model:show="showBibtexTemplate" 
    @on-accept="()=>{bibtex=bibtexTemplate; showBibtexTemplate=false}" 
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
        v-model:show="show" :title="datapoint?datapoint.authorAbbr():'new'" :show-cancel="false"
        @on-accept="save" @on-cancel="() => show=false"
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
                            <textarea id="bibtex" v-model="bibtex" placeholder="bibtex / enw / nbib"></textarea>
                        </div>
                        <div id="urlArea">
                            <label for="url">URL: </label>
                            <input id="url" v-model="url" placeholder="url" type="text">
                        </div>
                    </div>
                    <div id="inputRight">
                        <TagSelectorWithEntry 
                            v-model:tag-status="tagStatus"
                            v-model:tag-input-value="newTagInput"
                        ></TagSelectorWithEntry>
                    </div>
                </div>
            </div>
            <div v-else>
                <div style="
                    display: flex; flex-direction: column; align-items: center; justify-content: center; 
                    /* height: 470px; width: 630px */
                    height: 430px; width: 590px; border: 5px dashed var(--color-border); border-radius: 10px; margin: 15px;
                ">
                    <div style="font-size: 20px; font-weight: bold; margin-bottom: 10px;">Drop to insert citation</div>
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
    textarea, input[type="text"]{
        border: 1px solid var(--color-border);
        border-radius: 5px;
        background-color: var(--color-background);
        color: var(--color-text);
        width: 100%
    }

    #inputLeft, #inputRight{
        display: flex;
        flex-direction: column;
        width: 100%;
        gap: 10px;
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
        padding: 5px
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

</style>../../api/serverConn