
<script setup lang="ts">
    import { watch } from 'vue';
    import { DataTags } from '../../core/dataClass';
    import TagSelector from './TagSelector.vue';
    import { useUIStateStore } from '../store';
    import type { TagStatus } from '../interface';

    const emit = defineEmits<{
        (e: "onCheck", status: TagStatus) : void
    }>()

    const uiState = useUIStateStore();
    function clearTagSelection(){
        uiState.tagStatus.checked = new DataTags();
        uiState.updateShownData();
    }
    watch(uiState.tagStatus, () => emit('onCheck', uiState.tagStatus), {deep: true});
    
</script>
<template>
    <div class="main panel gradInFast">
        <TagSelector @onCheck="(status: TagStatus) => emit('onCheck', status)" v-model:tagStatus="uiState.tagStatus"></TagSelector>
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
