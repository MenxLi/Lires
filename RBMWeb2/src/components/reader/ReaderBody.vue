<script setup lang="ts">
    import { DataPoint } from '../../core/dataClass';
    import NoteEditor from './NoteEditor.vue';

    defineProps<{
        datapoint: DataPoint,
        layoutType: number
    }>();
</script>

<template>
    <div id="body">
        <iframe :src="datapoint.getOpenDocURL()" title="doc" v-show="layoutType!=1"></iframe>
        <NoteEditor :datapoint="datapoint" v-show="layoutType!=0"></NoteEditor>
    </div>
</template>

<style scoped>
div#body{
    display: flex;
    flex-direction: row;
    width: 100%;
    height: 100%;
    gap: 10px;
}

iframe{
    width: 100%;
    height: 100%;
    border: 1px solid var(--color-border);
    border-radius: 10px;
}

div#body>*{
    height: 100%;
    width: 100%;
    border: 1px solid var(--color-border);
    border-radius: 10px;
}
</style>