
<script setup lang="ts">
    import { ref, nextTick } from 'vue';
    import { DataTags } from '@/core/dataClass';
    import TagSelector from './TagSelector.vue';
    import { useUIStateStore } from './store';
    import type { TagCheckStatus } from './_interface';

    const emit = defineEmits<{
        (e: "onCheck", status: TagCheckStatus) : void
    }>()

    const renderSelector = ref(true);
    function clearTagSelection(){
        const uiState = useUIStateStore();
        uiState.currentlySelectedTags = new DataTags();
        uiState.updateShownData();
        // re-render tagSelector
        renderSelector.value = false;
        nextTick(() => renderSelector.value = true);
    }
    
</script>
<template>
    <div class="main panel gradInFast">
        <TagSelector v-if="renderSelector" @onCheck="(status) => emit('onCheck', status)"></TagSelector>
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
