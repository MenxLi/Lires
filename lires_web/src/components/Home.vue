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
    import { ServerConn } from "../core/serverConn";
    import FileTags from "./home/FileTags.vue";
    import FileRowContainer from "./home/FileRowContainer.vue";
    import Banner from "./common/Banner.vue";
    import LoadingWidget from "./common/LoadingWidget.vue";
    import BannerIcon from "./common/BannerIcon.vue";
    import DataEditor from "./home/DataEditor.vue";
    import addCircleIcon from "../assets/icons/add_circle.svg";
    import { MenuAttached } from "./common/fragments";
    import sellIcon from "../assets/icons/sell.svg";
    import refreshIcon from "../assets/icons/refresh.svg";

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
    const searchTypesPool = ["general", "title", "publication", "feature"];
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

    // refresh database
    function reloadDatabase(){
        dataStore.reload(
            true,
            () => { uiState.updateShownData(); },
            (_) => {
                uiState.showPopup(`Failed to load database from: ${new ServerConn().apiURL()}`, "alert")
            },
            () => uiState.updateShownData()
        );
    }

    // rename and delete tags
    function queryRenameTag(){
        const oldTag = prompt("Old tag");
        // check if oldTag is valid
        if (oldTag && dataStore.database.getAllTags().has(oldTag)){
            const newTag = prompt("New tag");
            if (newTag){
                dataStore.database.renameTag(oldTag, newTag).then(
                    () => {
                        uiState.showPopup("Tag renamed", "success");
                        uiState.updateShownData()
                    },
                    () => {
                        uiState.showPopup("Failed to rename tag", "error")
                        uiState.updateShownData()
                    },
                )
            }
        }
        else{
            uiState.showPopup("Invalid tag", "warning");
        }
    }
    function queryDeleteTag(){
        const tag = prompt("Tag to delete");
        if (tag && dataStore.database.getAllTags().has(tag)){
            dataStore.database.deleteTag(tag).then(
                () => {
                    uiState.showPopup("Tag deleted", "success");
                    uiState.updateShownData()
                },
                () => {
                    uiState.showPopup("Failed to delete tag", "error")
                    uiState.updateShownData()
                },
            )
        }
        else{
            uiState.showPopup("Invalid tag", "warning");
        }
    }

</script>

<template>
    <DataEditor :datapoint="null" v-model:show="showAddingDataWindow"></DataEditor>
    <div id="main" class="gradIn">
        <Banner>
            <div id="bannerAddons">
                <BannerIcon :iconSrc="addCircleIcon" labelText="New" title="Add new data to database"
                    @click="showAddingDataWindow = true" shortcut="ctrl+n"></BannerIcon>
                <MenuAttached :menu-items="[
                    {name: `Display: ${settingsStore.showTagPanel?'hide':'show'}`, action: () => settingsStore.setShowTagPanel(!settingsStore.showTagPanel)},
                    {name: 'Rename' , action: queryRenameTag},
                    {name: 'Delete' , action: queryDeleteTag},
                ]">
                    <BannerIcon :icon-src="sellIcon" label-text="Tags" title="Tag utilities"></BannerIcon>
                </MenuAttached>
                <BannerIcon :iconSrc="refreshIcon" labelText="Reload" title="Reload database"
                    @click="reloadDatabase"></BannerIcon>
                |
                <div class="searchbar">
                    <select ref="searchSelector" name="search_type" id="searchType" @change="onSearchChanged">
                        <option v-for="v in searchTypesPool" :value="v">{{ v }}</option>
                    </select>
                    <input id="searchbar" type="text" v-model="searchInput" @input="lazyOnSearchChanged" placeholder="search">
                </div>
            </div>
        </Banner>
        <div class="horizontal fullHeight">
            <FileTags v-if="settingsStore.showTagPanel" @onCheck="() => uiState.updateShownData()"></FileTags>
            <div class="panel scrollable" id="fileSelector">
                <FileRowContainer :datapoints="dataStore.database.getMany(uiState.shownDataUIDs)" v-model:unfoldedIds="uiState.unfoldedDataUIDs"
                    v-if="uiState.shownDataUIDs.length > 0"
                ></FileRowContainer>
                <div id="blankPlaceholder" v-else>
                    <div v-if="!dataStore.database.initialized">
                        <b>Loading...</b>
                        <LoadingWidget></LoadingWidget>
                    </div>
                    <p v-else>Nothing to show</p>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
    #main{
        height: 98vh;
        width: 98vw;
        display: flex;
        flex-direction: column;
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
        height: calc(100% - 30px);
    }
    .fullWidth{
        width: 100%;
    }
    div.horizontal{
        display: flex;
        padding-top: 10px;
        gap: 10px;
    }
    div#bannerAddons{
        display: flex;
        align-items: center;
        justify-self: center;
        gap: 10px;
    }
    #fileSelector{
        padding: 5px;
    }
</style>