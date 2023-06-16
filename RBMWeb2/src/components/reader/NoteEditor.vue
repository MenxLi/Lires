

<script setup lang="ts">
    // https://github.com/imzbf/md-editor-v3
    import { ref } from 'vue';
    import type { DataPoint } from '../../core/dataClass';
    import { MdEditor } from 'md-editor-v3';
    import { ThemeMode } from '../../core/misc';
    import 'md-editor-v3/lib/style.css';

    const props = defineProps<{
        datapoint: DataPoint
    }>();

    const mdText = ref<string>('');
    const mdEditor = ref<typeof MdEditor | null>(null);

    props.datapoint.fetchNote().then(
        (note) => {
            console.log('Note fetched')
            mdText.value = note;
        },
        (reason) => {
            console.error(reason);
        }
    )

    // event handlers
    function onSaveNote() {
        props.datapoint.uploadNote(mdText.value).then(
            () => {
                console.log('Note saved');
            },
            (reason) => {
                console.error(reason);
            }
        )
    }

    const onUploadImg = async (files: File[]) => {
        props.datapoint.uploadImages(files).then(
            (urls) => {
                console.log('Images uploaded');
                mdText.value! += urls.map(url => `![image](${url})`).join('\n');
                onSaveNote();   // save note after uploading images, to avoid un-referenced images on server
            },
            (reason) => {
                console.error(reason);
            }
        )
    }

</script>

<template>
    <div id="noteEditor">
        <div class="editor">
            <MdEditor ref="mdEditor"
                v-model="mdText" 
                :preview="false" 
                language="en-US"
                :theme="ThemeMode.isDarkMode() ? 'dark' : 'light'"
                @on-save="onSaveNote"
                @on-upload-img="onUploadImg"
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
                    'preview',
                    'catalog',
                ]"
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