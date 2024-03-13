<script lang="ts">
// https://github.com/vuejs/rfcs/blob/master/active-rfcs/0040-script-setup.md#automatic-name-inference
export default {
    name: 'Home',
    inheritAttrs: false,
    customOptions: {}
}
</script>
<script setup lang="ts">
    import { ref } from "vue";
    import { useConnectionStore, useUIStateStore, useDataStore, useSettingsStore } from "./store";
    import { useRouter } from "vue-router";
    import { DataTags } from "../core/tag";
    import FileTags from "./home/FileTags.vue";
    import FileRowContainer from "./home/FileRowContainer.vue";
    import Toolbar from "./common/Toolbar.vue";
    import ToolbarIcon from "./common/ToolbarIcon.vue";
    import DataEditor from "./home/DataEditor.vue";
    import addCircleIcon from "../assets/icons/add_circle.svg";
    import refreshIcon from "../assets/icons/refresh.svg";
    import LoadingWidget from "./common/LoadingWidget.vue";
    import FilterVis from "./visfeat/FilterVis.vue";
    import Searchbar from "./home/Searchbar.vue";

    // get data
    const uiState = useUIStateStore();
    const dataStore = useDataStore();
    const settingsStore = useSettingsStore();
    // const shownDatapoints = ref([] as DataPoint[]);
    // watch(()=>uiState.shownDataUIDs, ()=>{
    //     dataStore.database.agetMany(uiState.shownDataUIDs).then((res)=>{
    //         shownDatapoints.value = res;
    //     })
    // })

    // not show fileTag panel on small screen, by default
    if (window.innerWidth < 768){
        settingsStore.setShowTagPanel(false);
    }

    const router = useRouter();
    const defaultTags = router.currentRoute.value.query.tags as string | undefined;
    if (defaultTags != undefined){
        uiState.tagStatus.checked = new DataTags(defaultTags.split("&&"));
        uiState.tagStatus.unfolded = uiState.tagStatus.checked.allParents()
    }


    // adding new data
    const dataEditor = ref(null as null | typeof DataEditor);

    function showBlankAddingDataWindow(){
        dataEditor.value!.show({
            datapoint : null,
        });
    }

    function onDropFiles(event: DragEvent){
        event.preventDefault();
        const files = event.dataTransfer?.files;
        if (files){
            showBlankAddingDataWindow();
            if (!dataEditor.value!.loadFiles(files)){
                dataEditor.value!.close()
            }
        }
    }

    function reloadProg(){
        uiState.reloadDatabase();
        useConnectionStore().wsConn.reset();
    }

</script>

<template>
    <DataEditor ref="dataEditor"></DataEditor>
    <Toolbar :return-home="false" :compact="true">
        <!-- <div id="toolbarAddons">
            <ToolbarIcon :iconSrc="addCircleIcon" labelText="New" title="Add new data to database"
                @click="showBlankAddingDataWindow" shortcut="ctrl+n"></ToolbarIcon>
            <ToolbarIcon :iconSrc="refreshIcon" labelText="Reload" title="Reload database"
                @click="reloadProg"></ToolbarIcon>
        </div> -->
    </Toolbar>
    <div id="main-home" class="gradIn">
        <div class="horizontal fullHeight">
            <Transition name="left-in">
                <div id="left-panel" v-if="settingsStore.showTagPanel">
                    <FileTags @onCheck="() => uiState.updateShownData()"></FileTags>
                </div>
            </Transition>
            <div id="right-panel" class="panel1">
                <div class="fullWidth">
                    <FilterVis></FilterVis>
                </div>
                <div class="scrollable" id="fileSelector" @dragover="(e: Event)=>e.preventDefault()" @drop="onDropFiles">
                    <div style="display: flex; justify-content: space-between;">
                        <div style="flex-grow: 1;">
                            <Searchbar></Searchbar>
                        </div>
                        <!-- vertical split -->
                        <!-- <div style="border: 1px solid var(--color-border);margin-right: 5px"></div> -->
                        <div style="display: flex; flex-grow: 0; margin-right: 5px; margin-block: 5px;">
                            <ToolbarIcon :iconSrc="addCircleIcon" labelText="New" title="Add new data to database"
                                @click="showBlankAddingDataWindow" shortcut="ctrl+n"></ToolbarIcon>
                            <ToolbarIcon :iconSrc="refreshIcon" labelText="Reload" title="Reload database"
                                @click="reloadProg"></ToolbarIcon>
                        </div>
                    </div>
                    <FileRowContainer :uids="uiState.shownDataUIDs" v-model:unfoldedIds="uiState.unfoldedDataUIDs"
                        v-if="uiState.shownDataUIDs.length > 0"
                    ></FileRowContainer>

                    <div id="blankPlaceholder" v-else>
                        <p v-if="dataStore.database.initialized" style="
                            font-size: xx-large;
                            font-weight: bold;
                            user-select: none;
                        ">
                            Nothing to show
                            <p style="font-size: medium">
                                Add your first enty by clicking the 
                                <b><a @click="showBlankAddingDataWindow" style="
                                    cursor:pointer;
                                    border-radius: 5px;
                                    padding-inline: 3px;
                                    /* border: 1px solid var(--color-border); */
                                    background-color: var(--color-background-soft);
                                    ">⊕ New</a></b> 
                                button above.<br>
                                <!-- Refer to the <a :href="manualURL_zh">documentation</a> for more information. -->
                            </p>
                        </p>
                        <LoadingWidget v-else></LoadingWidget>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
    body {
        height: 100vh;
    }
    #main-home{
        margin-top: 40px;
        height: calc(100vh - 40px - 10px);
        width: calc(100vw - 20px);
        display: flex;
        flex-direction: column;

        border: 1px solid var(--color-border);
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 0 5px var(--color-shadow);
    }
    .panel1{
        width: 100%;
        height: 100%;
        align-self: center;
        margin: 0em;
        border-radius: 12px;
    }
    #right-panel{
        display: flex;
        flex-direction: column;
        width: 100%;
        gap: 2px;
        overflow-x: hidden;
    }
    #blankPlaceholder{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
    }
    #blankPlaceholder p{
        color: var(--color-text-soft);
        text-align: center;
        margin: 10px;
    }
    .fullHeight{
        height: calc(100%);
        /* 15 to the bottom, not good for mobile safari though... */
    }
    .fullWidth{
        width: 100%;
    }
    div.horizontal{
        display: flex;
        /* gap: 10px; */
    }
    div#fileSelector{
        display: flex;
        flex-direction: column;
        height: 100%;
    }

    .left-in-enter-active, .left-in-leave-active {
        transition: all 0.075s ease-in-out;
    }

    .left-in-enter-from{
        opacity: 0;
        transform: translateX(-10%);
    }

    @media screen and (max-width: 767px) {
        #main-home{
            width: 100vw;
            margin-top: 30px;
            height: calc(100vh - 40px);
            border-radius: 0px;
            border-left: none;
            border-right: none;
        }
    }
</style>