

<script setup lang="ts">
    // https://github.com/imzbf/md-editor-v3
    import { ref } from 'vue';
    import type { DataPoint } from '../../core/dataClass';
    import { MdEditor } from 'md-editor-v3';
    import { ThemeMode } from '../../core/misc';
    import 'md-editor-v3/lib/style.css';

    defineProps<{
        datapoint: DataPoint
    }>();

    const mdText = ref<string>('');
    const mdEditor = ref<typeof MdEditor | null>(null);

</script>

<template>
    <div id="noteEditor">
        <div class="editor">
            <MdEditor ref="mdEditor"
                v-model="mdText" 
                :preview="false" 
                language="en-US"
                :theme="ThemeMode.isDarkMode() ? 'dark' : 'light'"
            />
        </div>
    </div>
</template>

<style scoped>
div#noteEditor {
    display: flex;
    flex-direction: column;
    height: 100%;
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