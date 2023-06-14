

<script setup lang="ts">
    import FileRow from './FileRow.vue';
    import {useUIStateStore, useDataStore } from '../store';

    const uiState = useUIStateStore();
    const dataStore = useDataStore();

</script>

<template>
    <div class="panel scrollable">
        <FileRow v-for="uid in uiState.shownDataUIDs" :datapoint="dataStore.database.get(uid)"></FileRow>
    </div>
</template>

<style scoped> 
    div.panel {
        border-radius: 10px;
        padding: 15px;
    }
</style>