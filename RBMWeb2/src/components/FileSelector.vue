

<script setup lang="ts">
    import FileRow from './FileRow.vue';
    import {useUIStateStore } from './store';

    const uiState = useUIStateStore();

</script>

<template>
    <div class="panel scrollable">
        <FileRow v-for="uid in uiState.shownDataUIDs" :uid="uid"></FileRow>
    </div>
</template>

<style scoped> 
    div.panel {
        border-radius: 10px;
        padding: 15px;
    }
</style>