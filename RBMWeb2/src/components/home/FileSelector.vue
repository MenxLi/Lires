

<script setup lang="ts">
    import {useUIStateStore, useDataStore } from '../store';
    import FileRowContainer from './FileRowContainer.vue';

    const uiState = useUIStateStore();
    const dataStore = useDataStore();

</script>

<template>
    <div class="panel scrollable">
        <FileRowContainer :datapoints="dataStore.database.getMany(uiState.shownDataUIDs)" v-model:unfoldedIds="uiState.unfoldedDataUIDs"></FileRowContainer>
    </div>
</template>

<style scoped> 
    div.panel {
        border-radius: 10px;
        padding: 15px;
    }
</style>