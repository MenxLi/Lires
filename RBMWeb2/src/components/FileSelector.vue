


<script setup lang="ts">
    import { computed } from 'vue';
    import FileRow from './FileRow.vue';
    import type { DataBase, DataPoint } from '@/core/dataClass';
    const props = defineProps<{
        database: DataBase
        showUids: string[]
    }>()

    const sortedUIDs = computed(() => props.showUids.sort(
        function(a, b){
            // criterion
                const ca = props.database.get(a).info["time_added"];
                const cb = props.database.get(b).info["time_added"];
                if (ca === cb) { return 0};
                if (ca < cb){ return 1 } else{return -1}
            }
        ))

</script>

<template>
    <div class="panel">
        <FileRow v-for="uid in sortedUIDs" :datapoint="database.data[uid]"></FileRow>
    </div>
</template>

<style scoped> 
    div.panel {
        border: 3px solid var(--color-border);
        border-radius: 10px;
        padding: 15px;
    }
</style>