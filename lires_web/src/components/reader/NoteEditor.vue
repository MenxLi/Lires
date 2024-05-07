

<script setup lang="ts">
    // https://github.com/imzbf/md-editor-v3
    import { computed, onActivated, onMounted, onUnmounted, ref, watch } from 'vue';
    import { DataPoint } from '../../core/dataClass';
    import { MdEditor, MdPreview } from 'md-editor-v3';
    import 'md-editor-v3/lib/style.css';
    import { useUIStateStore, useConnectionStore } from '../store';
    import { parseMarkdown, type FrontMatterData } from '../../core/markdownParse';
    import { useRouter } from 'vue-router';
    import { FileSelectButton } from '../common/fragments';
    import { copyToClipboard } from '../../utils/misc';
    import { registerServerEvenCallback_auto } from '../../api/serverWebsocketConn';
    import type { Event_Data } from '../../api/protocol';
    import { ThemeMode } from '../../core/misc';

    // requires vite-plugin-node-polyfills
    import matter from 'gray-matter';

    const props = defineProps<{
        datapoint: DataPoint | null
    }>();

    const router = useRouter();
    const mdText = ref<string>('');
    const mdFrontMatter = ref({} as FrontMatterData);
    const inactive = computed(()=>(!props.datapoint || props.datapoint?.isDummy()));

    const theme = ref(ThemeMode.isDarkMode()?'dark':'light' as 'dark'|'light')
    const __themeChangeFn = ()=>theme.value = ThemeMode.isDarkMode()?'dark' : 'light';
    onMounted( () => ThemeMode.registerThemeChangeCallback(__themeChangeFn))
    onUnmounted( () => ThemeMode.unregisterThemeChangeCallback(__themeChangeFn))


    watch(()=>mdText.value, (newVal)=>{
        try{
            const parse = matter(newVal);
            if (typeof parse.data !== 'object'){ return; }
            if (parse.data === mdFrontMatter.value){ return; }
            mdFrontMatter.value = parse.data;
            console.log("DEBUG: front matter", mdFrontMatter.value)
        }catch(e){}
    })
    const mdTextRender = computed(()=>parseMarkdown(mdText.value, {
        router: router,
        datapoint: props.datapoint,
    }))
    const mdEditor = ref<typeof MdEditor | null>(null);

    const uiState = useUIStateStore();
    const miscFiles = ref<Record<'fname'|'rpath'|'url', string>[]>([]);
    const noteRecord = ref<string>('');
    const saveHint = computed(()=>{
        // TODO: ... find the bug, to not use this function
        function formatForCompare(s: string){
            return s.replace(String.fromCharCode(10), String.fromCharCode(13)).replace(/\s/g, '');
        }
        // if (noteRecord.value.trim() === mdText.value.trim()){ return ''; }
        if (formatForCompare(noteRecord.value) === formatForCompare(mdText.value)){ return ''; }

        // debug:
        const a = formatForCompare(noteRecord.value).trim();
        const b = formatForCompare(mdText.value).trim();
        if (a.length !== b.length){
            console.log('length diff', a.length, b.length);
            return 'Unsaved';
        }

        // debug: find diff
        for (let i = 0; i < a.length; i++){
            if (a[i] !== b[i]){
                console.log('diff at', i, a[i], b[i]);
                console.log('char code', a.charCodeAt(i), b.charCodeAt(i));
                break;
            }
        }
        return 'Unsaved';
    })

    function resetState(){
        mdText.value = '';
        noteRecord.value = '';
        miscFiles.value = [];
    }

    async function fetchNote(){
        if (!props.datapoint || props.datapoint.isDummy()){return;}
        const note = await props.datapoint.fetchNote();
        noteRecord.value = note;
        mdText.value = note;
        // if (note.trim().length > 0){
        //     preview.value = true;
        // }
    }
    async function fetchMiscFileInfo(){
        if (!props.datapoint || props.datapoint.isDummy()){return;}
        miscFiles.value = await props.datapoint.listMiscFiles();
    }
    async function fetchAll(){ 
        if (!props.datapoint || props.datapoint.isDummy()){return;}
        await Promise.all([fetchNote(), fetchMiscFileInfo()]); 
    }

    onActivated(fetchAll);
    // fetchAll()
    watch(() => props.datapoint, () => {
        if (inactive.value){ resetState(); }
        else{
            fetchAll(); console.log('datapoint changed, fetching note and misc files...')
        }
    })

    // event handlers
    async function saveNote() {
        if (!props.datapoint || props.datapoint.isDummy()){return;}
        await props.datapoint.uploadNote(mdText.value);
        noteRecord.value = mdText.value;
    }

    const deleteMiscFile = async (fname: string)=>{
        if (!props.datapoint || props.datapoint.isDummy()){return;}
        await props.datapoint.deleteMiscFile(fname);
        miscFiles.value = miscFiles.value.filter((f)=>f.fname !== fname);
        useUIStateStore().showPopup('File deleted', 'info')
    }

    const renameMiscFile = async (oldName: string, newName: string)=>{
        if (!props.datapoint || props.datapoint.isDummy()){return;}
        // check if file extension is the same
        if (oldName.split('.').pop() !== newName.split('.').pop()){
            useUIStateStore().showPopup('File extension must be the same', 'error')
            return;
        }
        // do rename
        await props.datapoint.renameMiscFile(oldName, newName);
        // update note content
        mdText.value = mdText.value.replace(oldName, newName);
        fetchMiscFileInfo();
        useUIStateStore().showPopup('File renamed', 'info')
    }

    const uploadMiscFiles = async (files: File[]) => {
        if (!props.datapoint || props.datapoint.isDummy()){return;}
        uiState.showPopup('Upload', 'info');
        const unifiedURLs = await props.datapoint.uploadMisc(files);
        unifiedURLs.map( url => mdEditor.value!.insert(()=>{
                return {
                    targetValue: `![image](${url})`,
                    select: false,
                    deviationStart: 0,
                    deviationEnd: 0
                }
            })
        );
        saveNote();   // save note after uploading images, to avoid un-referenced images on server
        fetchMiscFileInfo();  // update misc files list
    }

    const preview = computed({
            get: ()=>uiState.showNotePreview === null? mdText.value.trim().length > 0 : false,
            set: (v: boolean)=>{ uiState.showNotePreview = v; }
        });
    function linkOnNote(content: string): boolean{
        return mdText.value.indexOf(content) >= 0;
    }
    function prompt(msg: string){
        const ret = window.prompt(msg);
        if (!ret){ throw new Error('User cancelled'); }
        return ret;
    }

    defineExpose({
        preview,
        fetchNote
    })

    registerServerEvenCallback_auto('update_note', (event)=>{
        if (!props.datapoint || props.datapoint.isDummy()){return;}
        if (event.session_id === useConnectionStore().wsConn.sessionID){return;}
        // update note content from other clients
        const d_summary = (event as Event_Data).datapoint_summary!
        if (d_summary.uuid === props.datapoint.uid){ fetchAll().then(()=>{
            useUIStateStore().showPopup('update note from other clients', 'info')
        }); }
    });

</script>

<template>
    <div id="noteEditor">
        <div class="editor" @dblclick="preview=false">
            <MdEditor v-if="!preview" ref="mdEditor"
                v-model="mdText" 
                :preview="false" 
                language="en-US"
                :theme=theme
                @on-save="saveNote"
                @on-upload-img="uploadMiscFiles"
                :disabled="inactive"
                :toolbars="[
                    'bold',
                    'underline',
                    'italic',
                    '-',
                    'strikeThrough',
                    'title',
                    'quote',
                    'unorderedList',
                    'orderedList',
                    'task', // ^2.4.0
                    '-',
                    'link',
                    // 'image',
                    // 'mermaid',
                    '-',
                    'revoke',
                    'next',
                    'save',
                    '=',
                    // 'preview',
                    'catalog',
                ]"
            />
            <MdPreview v-else :model-value="mdTextRender"
                :theme=theme 
                :preview-theme="'vuepress'"
            />
            <div id="save-hint" v-if="!preview && saveHint">{{ saveHint }}</div>
        </div>
        <div style="padding-inline: 5px; padding-block: 0.5rem">
            <template v-for="(v, k) in mdFrontMatter" :key="k">
                <div v-if="k=='links'" style="display: flex; gap: 5px">
                    <label class="frontmatter-label">LINKS</label>
                    <template v-for="(link, name) in v" :key="i">
                        <a class="frontmatter-link" :href="link" target="_blank" v-if="typeof(name)=='string'">{{name}}</a>
                    </template>
                </div>
                <div v-else style="display: flex;">
                    [unknown-entry]&nbsp;<b>{{k}}:&nbsp;</b>{{v}}
                </div>
            </template>
        </div>
        <div id="btn-container">
            <button @click="preview=!preview">{{preview?'Edit':'Preview'}}</button>
            <FileSelectButton :action="(file: File)=>{
                if (!props.datapoint || props.datapoint.isDummy()){return;}
                props.datapoint.uploadMisc([file]).then((fpath: string[])=>{
                    useUIStateStore().showPopup('File uploaded', 'success')
                    fetchMiscFileInfo();
                    mdEditor!.insert(()=>{
                        return {
                            targetValue: `[${file.name}](${fpath[0]})`,
                            select: false,
                            deviationStart: 0,
                            deviationEnd: 0
                        }
                    })
                }) 
            }"
            ></FileSelectButton>
        </div>
        <div id="misc-toggle" @click="()=>{uiState.showMiscPanel = !uiState.showMiscPanel}">
            <div :id="uiState.showMiscPanel?'triangle-down':'triangle'"></div>
        </div>
        <div id="misc-container" v-if="uiState.showMiscPanel" class="hover-scrollable">
            <div v-if="miscFiles.length === 0" style="font-weight: bold; color: var(--color-text-soft); top: 0.5rem">
                No attached files.
            </div>
            <div v-for="file in miscFiles" :key="file.fname" class="misc-file">
                <div>
                    <a :href="file.url" target="_blank">{{file.fname}}</a>
                    <label style="color: var(--color-text-soft);" v-if="!linkOnNote(file.fname)">
                        (no-ref)
                    </label>
                </div>

                <div class="misc-file-op-container">
                    <a style="color: var(--color-text-soft); cursor: pointer;" 
                        @click="copyToClipboard(file.fname); useUIStateStore().showPopup('Copied')">
                        copy
                    </a>
                    <a style="color: var(--color-text-soft); cursor: pointer;" 
                        @click="renameMiscFile(file.fname, prompt('New name'))">
                        rename
                    </a>
                    <a style="color: var(--color-danger); cursor: pointer;" 
                        v-if="!linkOnNote(file.fname)"
                        @click="deleteMiscFile(file.fname)">
                        delete
                    </a>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
div#noteEditor {
    display: flex;
    flex-direction: column;
    height: 100%;
    width: 100%;
}
div.editor {
    text-align: left;
    /* clip a rounded corner here */
    /* clip-path: inset(0 0 0 0 round 10px); */
    /* display: flex; */
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
    height: 100%;
}
div.editor > * {
    flex: 1;
    width: 100%;
    height: 100%;
}
div#save-hint {
    width: 100%;
    height: auto;
    position: absolute;
    bottom: 24px;
    right: 0;
    padding: 0.2rem;
    color: var(--color-text);
    padding-inline: 0.5rem;
    font-size: 0.8rem;
    font-weight: bold;
    background-color: rgba(200, 50, 80, 0.5);
    border-top-left-radius: 0.5rem;
    border-top-right-radius: 0.5rem;
}

div#btn-container {
    display: flex;
    flex-direction: row;
    gap: 0px;
    width: 100%;
    background-color: var(--color-background);
    border-top: 1px solid var(--color-border);
}
div#misc-toggle {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 1.2rem;
    width: 100%;
    background-color: var(--color-background-soft);
    border-top: 1px solid var(--color-border);
}
div#misc-toggle:hover{
    background-color: var(--color-background-theme);
}
div#triangle {
    width: 0;
    height: 0;
    border-left: 10px solid transparent;
    border-right: 10px solid transparent;
    border-bottom: 10px solid var(--color-theme);
}
div#triangle-down {
    width: 0;
    height: 0;
    border-left: 10px solid transparent;
    border-right: 10px solid transparent;
    border-top: 10px solid var(--color-theme);
}

div#misc-container {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    min-height: 5rem;
    height: fit-content;
    background-color: var(--color-background);
    border-top: 1px solid var(--color-border);
}
div.misc-file{
    padding-inline: 0.5rem;
    justify-content: space-between;
    border-bottom: 1px solid var(--color-border);
    background-color: var(--color-background);
    color: var(--color-text);
    font-size: 0.8rem;
    gap: 0.5rem;
    display: flex;
}
.misc-file-op-container{
    display: none;
    gap: 0.5rem;
}
div.misc-file:hover { background-color: var(--color-background-theme-highlight); }
div.misc-file:hover .misc-file-op-container { display: flex; }

button, :deep(button){
    background-color: var(--color-background);
    border-radius: 0%;
    width: 100%;
    margin: 0px;
    border: 0.1px solid var(--color-border);
    height: 2rem;
    color: var(--color-text);
    /* border: none; */
    cursor: pointer;
}
button:hover, :deep(button):hover{
    background-color: var(--color-background-theme-highlight);
}

label.frontmatter-label
{
    display: none;
}
a.frontmatter-link{
    background-color: var(--color-pure);
    box-shadow: 0px 2px 3px 0px var(--color-shadow);
    border-radius: 15px;
    padding-inline: 8px;
}
a.frontmatter-link:hover{
    background-color: var(--color-background-theme-highlight);
}
/* a.frontmatter-link{
    background-color: var(--color-background-soft);
    border-radius: 5px;
    padding-inline: 0.2rem;
} */
</style>