

<script setup lang="ts">
    // https://github.com/imzbf/md-editor-v3
    import { computed, ref, watch } from 'vue';
    import { DataPoint } from '../../core/dataClass';
    import { MdEditor, MdPreview } from 'md-editor-v3';
    import 'md-editor-v3/lib/style.css';
    import { useUIStateStore, useDataStore, useSettingsStore } from '../store';
    import { parseMarkdown } from '../../core/markdownParse';
    import { useRouter } from 'vue-router';
    import { FileSelectButton } from '../common/fragments';
    import { copyToClipboard } from '../../utils/misc';

    const props = withDefaults(defineProps<{
        datapoint: DataPoint
        theme?: 'dark' | 'light'
    }>(), {
        theme: 'light'
    });

    const router = useRouter();
    const mdText = ref<string>('');
    const mdTextRender = computed(()=>parseMarkdown(mdText.value, {
        router: router,
        datapoint: props.datapoint,
    }))
    const mdEditor = ref<typeof MdEditor | null>(null);

    const showMiscFiles = ref<boolean>(false);
    const miscFileNames = ref<string[]>([]);
    const miscFiles = computed(()=>miscFileNames.value.map((name)=>({
        name: name,
        url: `${useSettingsStore().backend()}/misc/${props.datapoint.uid}` + 
        `?_u=${useDataStore().user.id}&fname=${name}`
    })))

    async function fetchNote(){
        if (props.datapoint.isDummy()){return;}
        const note = await props.datapoint.fetchNote();
        mdText.value = note;
        if (note.trim().length > 0){
            preview.value = true;
        }
    }
    fetchNote();

    async function fetchMiscFNames(){
        const fNames = await props.datapoint.listMiscFiles();
        miscFileNames.value = fNames;
    }
    watch(() => props.datapoint, () => {
        fetchNote(); 
        fetchMiscFNames();
        console.log('datapoint changed, fetching note')
    })

    // event handlers
    async function saveNote() {
        await props.datapoint.uploadNote(mdText.value);
        useUIStateStore().showPopup('Note saved', 'success')
    }

    const deleteMiscFile = async (fname: string)=>{
        await props.datapoint.deleteMiscFile(fname);
        miscFileNames.value = miscFileNames.value.filter((name)=>name !== fname);
        useUIStateStore().showPopup('File deleted', 'info')
    }

    const uploadMiscFiles = async (files: File[]) => {
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
        fetchMiscFNames();  // update misc files list
    }

    const preview = ref<boolean>(false);

    defineExpose({
        preview,
        fetchNote
    })

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
        </div>
        <div id="btn-container">
            <button @click="preview=!preview" 
                style="width: 100%; height: 30px; margin-top: 0px; border-radius: 0; font-weight: bold;"
            >{{preview?'Edit':'Preview'}}</button>
            <FileSelectButton :action="(file: File)=>{
                props.datapoint.uploadMisc([file]).then((fpath: string[])=>{
                    useUIStateStore().showPopup('File uploaded', 'success')
                    fetchMiscFNames();
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
            style="width: 100%; height: 30px; margin-top: 0px; border-radius: 0; font-weight: bold;"
            ></FileSelectButton>
        </div>
        <div id="misc-toggle" @click="()=>{showMiscFiles = !showMiscFiles}">
            <div :id="showMiscFiles?'triangle-down':'triangle'"></div>
        </div>
        <div id="misc-container" v-if="showMiscFiles">
            <div v-for="file in miscFiles" :key="file.name" class="misc-file">
                <div>
                    <a :href="file.url" target="_blank">{{file.name}}</a>
                    <label style="color: var(--color-text-soft);" v-if="mdText.indexOf(file.name) < 0">
                        (no-ref)
                    </label>
                </div>

                <div class="misc-file-op-container">
                    <a style="color: var(--color-text-soft); cursor: pointer;" 
                        @click="copyToClipboard(file.name); useUIStateStore().showPopup('Copied')">
                        copy_name
                    </a>
                    <a style="color: var(--color-danger); cursor: pointer;" 
                        v-if="mdText.indexOf(file.name) < 0"
                        @click="deleteMiscFile(file.name)">
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
    display: flex;
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
    height: 20px;
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
    /* min-height: 100px; */
    background-color: var(--color-background);
    border-top: 1px solid var(--color-border);
}
div.misc-file{
    padding-inline: 0.5rem;
    justify-content: space-between;
    border-bottom: 1px solid var(--color-border);
    background-color: var(--color-background);
    color: var(--color-text);
    font-size: 0.8em;
    gap: 0.5rem;
    display: flex;
}
.misc-file-op-container{
    display: none;
    gap: 0.5rem;
}
div.misc-file:hover { background-color: var(--color-background-theme); }
div.misc-file:hover .misc-file-op-container { display: flex; }
</style>