
<script setup lang="ts">
    import TagSelector from './TagSelector.vue';
    import { useTagSelectionStore } from './store';
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
    <div class="main panel gradInFast">
        <TagSelector :database="database" @onCheck="(status) => emit('onCheck', status)"></TagSelector>
        <div class="buttons">
            <button id="btnClear">Clear tags</button>
        </div>
    </div>
</template>

<style scoped>
    div.main{
        padding: 20px;
        min-width: 280px;
        width: fit-content;
        height: 100%;

        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    #btnClear{
        padding: 5px;
        width: 100%;
    }
</style>
