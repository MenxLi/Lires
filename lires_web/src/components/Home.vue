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
    import type { Ref } from "vue";
    import { useUIStateStore, useDataStore, useSettingsStore } from "./store";
    import { useRouter } from "vue-router";
    import { DataTags } from "../core/dataClass";
    import { getSessionConnection } from "../core/serverWebsocketConn";
    import FileTags from "./home/FileTags.vue";
    import FileRowContainer from "./home/FileRowContainer.vue";
    import Banner from "./common/Banner.vue";
    import BannerIcon from "./common/BannerIcon.vue";
    import DataEditor from "./home/DataEditor.vue";
    import addCircleIcon from "../assets/icons/add_circle.svg";
    import sellIcon from "../assets/icons/sell.svg";
    import refreshIcon from "../assets/icons/refresh.svg";
    import LoadingProgressPopout from "./common/LoadingProgressPopout.vue";
    import LoadingWidget from "./common/LoadingWidget.vue";
    import FilterVis from "./visfeat/FilterVis.vue";

    import type { SearchStatus } from "./interface";
    import { lazify } from "../libs/misc";

    // get data
    const uiState = useUIStateStore();
    const dataStore = useDataStore();
    const settingsStore = useSettingsStore();

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

    // search refealated
    const searchTypesPool = ["general", "title", "author", "note", "publication", "feature", "uuid"];
    const searchInput = ref("")
    const searchSelector: Ref<HTMLSelectElement | null> = ref(null)
    function onSearchChanged(){
        const status: SearchStatus = {
            searchBy: searchSelector.value!.value,
            content: searchInput.value
        }
        uiState.searchState = status;
        console.log(status);
        uiState.updateShownData();
    }
    const lazyOnSearchChanged = lazify(onSearchChanged, 200);

    // adding new data
    const showAddingDataWindow = ref(false);

    function reloadProg(){
        uiState.reloadDatabase();
        getSessionConnection().reset();
    }

</script>

<template>
    <DataEditor :datapoint="null" v-model:show="showAddingDataWindow"></DataEditor>
    <Banner :return-home="false">
        <div id="bannerAddons">
            <BannerIcon :iconSrc="addCircleIcon" labelText="New" title="Add new data to database"
                @click="showAddingDataWindow = true" shortcut="ctrl+n"></BannerIcon>
            <BannerIcon :icon-src="sellIcon" label-text="Tags" title="Tag utilities"
                @click="()=>settingsStore.setShowTagPanel(!settingsStore.showTagPanel)"></BannerIcon>
            <BannerIcon :iconSrc="refreshIcon" labelText="Reload" title="Reload database"
                @click="reloadProg"></BannerIcon>
            |
            <div class="searchbar">
                <select ref="searchSelector" name="search_type" id="searchType" @change="onSearchChanged">
                    <option v-for="v in searchTypesPool" :value="v">{{ v }}</option>
                </select>
                <input id="searchbar" type="text" v-model="searchInput" @input="lazyOnSearchChanged" placeholder="search">
            </div>
        </div>
    </Banner>
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
                <div class="scrollable" id="fileSelector">
                    <FileRowContainer :datapoints="dataStore.database.getMany(uiState.shownDataUIDs)" v-model:unfoldedIds="uiState.unfoldedDataUIDs"
                        v-if="uiState.shownDataUIDs.length > 0"
                    ></FileRowContainer>

                    <div id="blankPlaceholder" v-else>
                        <p v-if="dataStore.database.initialized">Nothing to show</p>
                        <LoadingWidget v-else></LoadingWidget>
                    </div>

                    <Transition name="fade">
                        <LoadingProgressPopout v-if="!dataStore.database.initialized" :perc="uiState.databaseLoadingProgress" 
                                :text="uiState.databaseLoadingStatus.nTotal >= 0?`${uiState.databaseLoadingStatus.nCurrent} / ${uiState.databaseLoadingStatus.nTotal}`:'_'"/>
                    </Transition>
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
        margin-top: 50px;
        height: calc(100vh - 50px - 10px);
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
        height: 100%;
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
        color: var(--color-border);
        font-size: xx-large;
        font-weight: bold;
        text-align: center;
        margin: 10px;
        user-select: none;
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
    div#bannerAddons{
        display: flex;
        align-items: center;
        justify-self: center;
    }
    div#fileSelector{
        /* padding: 5px; */
        flex-grow: 999;
    }

    div.searchbar{
        display: flex;
        margin-left: 5px;
        gap: 5px;
    }
    div.searchbar select {
        width: 75px;
    }
    div.searchbar input {
        width: calc(100% - 80px);
    }

    .fade-leave-active {
        transition: opacity 0.5s;
    }

    .fade-enter-from, .fade-leave-to {
        opacity: 0;
    }

    .left-in-enter-active, .left-in-leave-active {
        transition: all 0.15s ease-in-out;
    }

    .left-in-enter-from{
        opacity: 0;
        transform: translateX(-10%);
    }

    @media screen and (max-width: 767px) {
        #main-home{
            width: 100vw;
            height: calc(100vh - 50px);
            border-radius: 0px;
            border-left: none;
            border-right: none;
        }
    }
</style>