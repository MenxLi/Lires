
<script setup lang="ts">
    import { watch, ref } from 'vue';
    import { DataTags } from '../../core/dataClass';
    import { computed } from 'vue';
    import TagSelector from './TagSelector.vue';
    import TagBubbleContainer from './TagBubbleContainer.vue';
    import { useUIStateStore, useDataStore } from '../store';
    import type { TagStatus } from '../interface';

    const emit = defineEmits<{
        (e: "onCheck", status: TagStatus) : void
    }>()
    const uiState = useUIStateStore();

    const ftPanel = ref<HTMLElement | null>(null);

    const currentSelectedDatapoint = computed(() => {
        if (useUIStateStore().unfoldedDataUIDs.length == 0){
            return null;
        }
        else{
            if (uiState.shownDataUIDs.includes(uiState.unfoldedDataUIDs[0])){
                // make sure the unfolded datapoint is showed
                return useDataStore().database.get(useUIStateStore().unfoldedDataUIDs[0]);
            }
            return null;
        }
    });

    const highlightTags = computed(() => {
        if (currentSelectedDatapoint.value == null){
            return null;
        }
        else{
            const ret = uiState.tagStatus.checked.withChildsFrom(currentSelectedDatapoint.value.tags)
            return ret
        }
    });

    function clearTagSelection(){
        uiState.tagStatus.checked = new DataTags();
        uiState.updateShownData();
    }
    watch(uiState.tagStatus, () => emit('onCheck', uiState.tagStatus), {deep: true});
    
</script>
<template>
    <div class="main panel slideInFast" ref="ftPanel">
        <TagSelector @onCheck="(status: TagStatus) => emit('onCheck', status)" v-model:tagStatus="uiState.tagStatus"></TagSelector>
        <TagBubbleContainer v-if="currentSelectedDatapoint" 
            :tags="currentSelectedDatapoint.tags" 
            :highlightTags="highlightTags" 
            :maxWidth="ftPanel? ftPanel.clientWidth : null">
        </TagBubbleContainer>
        <div class="buttons">
            <button id="btnClear" class="green" @click="clearTagSelection">CLEAR TAGS</button>
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
        box-shadow: 0 0 10px var(--color-shadow);

        gap: 10px;
    }
    #btnClear{
        padding: 5px;
        width: 100%;
        border: 0px solid var(--color-border);
        font-weight: bold;
        /* color: var(--color-theme) */
    }
    .panel1{
        width: 100%;
        height: 100%;
        align-self: center;
        margin: 0em;
        border-radius: 12px;
    }
</style>
