
<script setup lang="ts">
    import TagSelector from './TagSelector.vue';
    import type { DataBase } from '@/core/dataClass';
    import type { TagCheckStatus } from './_interface';

    const props = defineProps<{
        database: DataBase
    }>()

    const emit = defineEmits<{
        (e: "onCheck", status: TagCheckStatus) : void
    }>()
</script>
<template>
    <div class="main panel">
        <TagSelector :database="database" @onCheck="(status) => emit('onCheck', status)"></TagSelector>
    </div>
</template>

<style scoped>
    div.main{
        padding: 20px;
        min-width: 280px;
        width: fit-content;
    }
</style>
