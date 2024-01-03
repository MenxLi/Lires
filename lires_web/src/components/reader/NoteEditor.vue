

<script setup lang="ts">
    // https://github.com/imzbf/md-editor-v3
    import { computed, ref, watch } from 'vue';
    import { DataPoint } from '../../core/dataClass';
    import { MdEditor, MdPreview } from 'md-editor-v3';
    import 'md-editor-v3/lib/style.css';
    import { useUIStateStore } from '../store';
    import { parseMarkdown } from '../../core/markdownParse';
    import { useRouter } from 'vue-router';

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

    function fetchNote(){
        props.datapoint.fetchNote().then(
            (note) => {
                console.log('Note fetched')
                mdText.value = note;
                // toggle preview if note is not empty
                if (note.trim().length > 0){
                    preview.value = true;
                }
            },
            (reason) => {
                console.error(reason);
            }
        )
    }
    fetchNote();
    watch(() => props.datapoint, () => {fetchNote(); console.log('datapoint changed, fetching note')})

    // event handlers
    function saveNote() {
        props.datapoint.uploadNote(mdText.value).then(
            () => {
                console.log('Note saved');
                useUIStateStore().showPopup('Note saved', 'success')
            },
            (reason) => {
                console.error(reason);
                useUIStateStore().showPopup('Failed to save', 'warning')
            }
        )
    }
    const uploadImages = async (files: File[]) => {
        props.datapoint.uploadImages(files).then(
            (urls) => {
                console.log('Images uploaded');
                urls.map( url => mdEditor.value!.insert(()=>{
                        return {
                            targetValue: `![image](${url})`,
                            select: false,
                            deviationStart: 0,
                            deviationEnd: 0
                        }
                    })
                );
                saveNote();   // save note after uploading images, to avoid un-referenced images on server
            },
            (reason) => {
                console.error(reason);
            }
        )
    }

    const preview = ref<boolean>(false);
    // function togglePreview(state: boolean){
    //     preview.value = state;
    // }

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
                @on-upload-img="uploadImages"
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
            />
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
    clip-path: inset(0 0 0 0 round 10px);
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

</style>