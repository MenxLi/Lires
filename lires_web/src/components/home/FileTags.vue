
<script setup lang="ts">
    import { watch, ref } from 'vue';
    import { DataTags } from '../../core/tag';
    import type { DataPoint } from '../../core/dataClass';
    import { computed } from 'vue';
    import TagSelector from '../tags/TagSelector.vue';
    import TagBubbleContainer from '../tags/TagBubbleContainer.vue';
    import { useConnectionStore, useUIStateStore, useDataStore } from '../store';
    import type { TagStatus } from '../interface';

    const emit = defineEmits<{
        (e: "onCheck", status: TagStatus) : void
    }>()
    const uiState = useUIStateStore();
    const dataStore = useDataStore();

    const ftPanel = ref<HTMLElement | null>(null);

    const currentSelectedDatapoint = ref(null as DataPoint | null)
    watch(() => uiState.unfoldedDataUIDs, ()=>{
        if (uiState.unfoldedDataUIDs.length == 0){ currentSelectedDatapoint.value = null; }
        else{
            if (uiState.shownDataUIDs.includes(uiState.unfoldedDataUIDs[0])){
                // make sure the unfolded datapoint is showed
                dataStore.database.aget(uiState.unfoldedDataUIDs[0]).then((dp)=>{
                    currentSelectedDatapoint.value = dp;
                })
            }
        }
    })

    const highlightTags = computed(() => {
        if (currentSelectedDatapoint.value == null){
            return null;
        }
        else{
            const ret = uiState.tagStatus.checked.withChildsFrom(currentSelectedDatapoint.value.tags)
            return ret
        }
    });
    const mutedTags = computed(() => {
        const ret = uiState.tagStatus.checked.copy();
        if (currentSelectedDatapoint.value !== null){
            ret.pop_ifcontains_(currentSelectedDatapoint.value.tags);
        }
        return ret
    });

    function clearTagSelection(){
        uiState.tagStatus.checked = new DataTags();
        uiState.updateShownData();
    }
    watch(uiState.tagStatus, () => emit('onCheck', uiState.tagStatus), {deep: true});

    // rename and delete tags
    function queryRenameTag(){
        const oldTag = prompt("Old tag");
        // check if oldTag is valid
        if (oldTag && dataStore.database.allTags().has(oldTag)){
            const newTag = prompt("New tag");
            if (newTag){
                useConnectionStore().conn.renameTag(oldTag, newTag).then(
                    () => { uiState.showPopup("Tag renamed", "success"); },
                    () => { uiState.showPopup("Failed to rename tag", "error") },
                )
            }
        }
        else{
            uiState.showPopup("Invalid tag", "warning");
        }
    }
    function queryDeleteTag(){
        const tag = prompt("Tag to delete");
        if (tag && dataStore.database.allTags().has(tag)){
            if (!confirm(`Are you sure to delete tag "${tag}"?`)){
                return;
            }
            useConnectionStore().conn.deleteTag(tag).then(
                () => { uiState.showPopup("Tag deleted", "success"); },
                () => { uiState.showPopup("Failed to delete tag", "error") },
            )
        }
        else{
            uiState.showPopup("Invalid tag", "warning");
        }
    }

    
</script>
<template>
    <div id='file-tags-main' ref="ftPanel">
        <div class="title">
            <div id="title-title">
                <h3 class="green">Tags</h3>
                <div id="title-buttons">
                    <div class="button" @click="queryRenameTag">rename</div>
                    <div class="button" @click="queryDeleteTag">delete</div>
                </div>
            </div>
            <hr>
        </div>
        <TagSelector @onCheck="(status: TagStatus) => emit('onCheck', status)" v-model:tagStatus="uiState.tagStatus"></TagSelector>
        <hr>
        <TagBubbleContainer 
            @click-on-bubble="(tag: string) => {
                if (uiState.tagStatus.checked.has(tag)){ uiState.tagStatus.checked.delete(tag); }
                else{ uiState.tagStatus.checked.add(tag); }
                uiState.updateShownData();
            }"
            :tags="currentSelectedDatapoint? currentSelectedDatapoint.tags : uiState.tagStatus.checked"
            :highlight-tags="highlightTags" 
            :muted-tags="mutedTags"
            :max-width="ftPanel? ftPanel.clientWidth : null">
        </TagBubbleContainer>
        <div class="buttons">
            <button id="btnClear" class="green" @click="clearTagSelection">CLEAR SELECTION</button>
        </div>
    </div>
</template>

<style scoped>
    div#title-title{
        margin-left: 5px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    div#title-title h3{
        text-align: left;
        font-weight: bold;
        color: var(--color-theme);
    }
    div#title-buttons{
        display: flex;
        gap: 5px;
        opacity: 0.15;
        transition: opacity 0.5s;
        transition-delay: opacity 0.2s;
    }
    div#title-buttons div.button:hover{
        text-decoration: underline;
        text-underline-offset: 2px;
    }
    div#title-buttons div.button{
        /* border: 1px solid var(--color-border); */
        transition: all 0.2s;
        padding-left: 5px;
        padding-right: 5px;
        font-size: smaller;
        border-radius: 5px;
        cursor: pointer;
    }
    div#title-title:hover div#title-buttons{
        opacity: 1;
    }

    hr{
        /* display: none; */
        margin-top: 5px;
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
        /* box-shadow: 0 0 5px var(--color-shadow); */
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