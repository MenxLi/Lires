
<script setup lang="ts">
    import { DataTags } from '../core/dataClass';
    import TagSelector from './TagSelector.vue';
    import { useUIStateStore } from './store';
    import type { TagCheckStatus } from './_interface';

    const emit = defineEmits<{
        (e: "onCheck", status: TagCheckStatus) : void
    }>()

    function clearTagSelection(){
        const uiState = useUIStateStore();
        uiState.currentlySelectedTags = new DataTags();
        uiState.updateShownData();
    }
    
</script>
<template>
    <div class="main panel gradInFast">
        <TagSelector @onCheck="(status: TagCheckStatus) => emit('onCheck', status)"></TagSelector>
        <div class="buttons">
            <button id="btnClear" @click="clearTagSelection">Clear tags</button>
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
