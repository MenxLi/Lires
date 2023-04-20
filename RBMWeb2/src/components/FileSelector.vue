

<script setup lang="ts">
    import { computed } from 'vue';
    import FileRow from './FileRow.vue';
    import { useDataStore, useUIStateStore } from './store';

    const uiState = useUIStateStore();
    const dataStore = useDataStore();

    const sortedUIDs = computed(() => uiState.shownDataUIDs.sort(
        function(a, b){
            // criterion
                const ca = dataStore.database.get(a).info["time_added"];
                const cb = dataStore.database.get(b).info["time_added"];
                if (ca === cb) { return 0};
                if (ca < cb){ return 1 } else{return -1}
            }
        ))

</script>

<template>
    <div class="panel scrollable">
        <FileRow v-for="uid in sortedUIDs" :datapoint="dataStore.database.get(uid)"></FileRow>
    </div>
</template>

<style scoped> 
    div.panel {
        border: 3px solid var(--color-border);
        border-radius: 10px;
        padding: 15px;
    }
</style>