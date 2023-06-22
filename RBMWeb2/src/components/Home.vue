<script setup lang="ts">
    import { ref, computed, onMounted } from "vue";
    import type { Ref } from "vue";
    import { useUIStateStore, useDataStore } from "./store";
    import { useRouter } from "vue-router";
    import { DataTags } from "../core/dataClass";
    import FileTags from "./home/FileTags.vue";
    import FileRowContainer from "./home/FileRowContainer.vue";
    import Banner from "./common/Banner.vue";
    import BannerIcon from "./common/BannerIcon.vue";
    import DataEditor from "./home/DataEditor.vue";
    import addCircleIcon from "../assets/icons/add_circle.svg";

    import type { SearchStatus } from "./interface";

    // get data
    const uiState = useUIStateStore();
    const dataStore = useDataStore();

    // not show fileTag panel on small screen
    let windowWidth = ref(window.innerWidth);
    onMounted(() => {
        window.onresize = () => {
                windowWidth.value = window.innerWidth
            }
    });
    const showFileTags = computed(() => windowWidth.value > 600);

    const router = useRouter();
    const defaultTags = router.currentRoute.value.query.tags as string | undefined;
    if (defaultTags != undefined){
        uiState.tagStatus.checked = new DataTags(defaultTags.split("&&"));
        uiState.tagStatus.unfolded = uiState.tagStatus.checked.allParents()
    }

    // search refealated
    const searchTypesPool = ["general", "title", "feature"];
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

    // adding new data
    const showAddingDataWindow = ref(false);

</script>

<template>
    <DataEditor :datapoint="null" v-model:show="showAddingDataWindow"></DataEditor>
    <div id="main" class="gradIn">
        <Banner>
            <div id="bannerAddons">
                <BannerIcon :iconSrc="addCircleIcon" labelText="New" title="Add new data to database"
                    @click="showAddingDataWindow = true" shortcut="ctrl+a"></BannerIcon>
                |
                <div class="searchbar">
                    <select ref="searchSelector" name="search_type" id="searchType" @change="onSearchChanged">
                        <option v-for="v in searchTypesPool" :value="v">{{ v }}</option>
                    </select>
                    <input id="searchbar" type="text" v-model="searchInput" @input="onSearchChanged" placeholder="search">
                </div>
            </div>
        </Banner>
        <div class="horizontal fullHeight">
            <FileTags v-if="showFileTags" @onCheck="() => uiState.updateShownData()"></FileTags>
            <div class="panel scrollable" id="fileSelector">
                <FileRowContainer :datapoints="dataStore.database.getMany(uiState.shownDataUIDs)" v-model:unfoldedIds="uiState.unfoldedDataUIDs"></FileRowContainer>
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