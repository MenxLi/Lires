


<script setup lang="ts">
    import FileRow from './FileRow.vue';
    import type { DataBase, DataPoint } from '@/core/dataClass';
    const props = defineProps<{
        database: DataBase
        showUids: string[]
    }>()
</script>

<template>
    <div class="panel">
        <FileRow v-for="uid in showUids" :datapoint="database.data[uid]"></FileRow>
    </div>
</template>

<style scoped> 
    div.panel {
        border: 3px solid var(--color-border);
        border-radius: 10px;
        padding: 15px;
    }
</style>