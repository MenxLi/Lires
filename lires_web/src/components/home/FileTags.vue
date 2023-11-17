
<script setup lang="ts">
    import { watch, ref } from 'vue';
    import { DataTags } from '../../core/dataClass';
    import { computed } from 'vue';
    import TagSelector from '../tags/TagSelector.vue';
    import TagBubbleContainer from '../tags/TagBubbleContainer.vue';
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
    <div id='file-tags-main' ref="ftPanel">
        <div class="title">
            <h3>Tags</h3>
            <hr>
        </div>
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
    div.title h3{
        margin-left: 5px;
    }
    div.title h3{
        text-align: left;
        font-weight: bold;
        color: var(--color-theme);
    }
    hr{
        /* display: none; */
        border: 1px solid var(--color-border);
        border-top: none;
        /* margin-right: -10px;
        margin-left: -15px; */
    }
    div#file-tags-main{
        padding: 15px;
        padding-left: 10px;
        padding-right: 10px;
        min-width: 260px;
        width: fit-content;
        height: 100%;

        display: flex;
        flex-direction: column;
        justify-content: space-between;
        /* box-shadow: 0 0 10px var(--color-shadow); */
        border-radius: 10px 0 0 10px;
        border: 1px solid var(--color-border);
        border-top: none;
        border-left: none;
        border-bottom: none;

        background-color: var(--color-background-tagpanel);

        gap: 10px;
    }
    div.buttons{
        padding-left: 5px;
        padding-right: 5px;
    }
    #btnClear{
        padding: 5px;
        width: 100%;
        border: 0px solid var(--color-border);
        font-weight: bold;
        /* color: var(--color-theme) */
    }
</style>
