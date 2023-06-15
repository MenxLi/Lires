<script setup lang="ts">
    import { ref, computed, onMounted } from "vue";
    import type { Ref } from "vue";
    import { useUIStateStore, useDataStore } from "./store";
    import { useRouter } from "vue-router";
    import { DataTags } from "../core/dataClass";
    import FileTags from "./home/FileTags.vue";
    import FileSelector from "./home/FileSelector.vue";
    import Banner from "./common/Banner.vue";

    import type { SearchStatus } from "./home/_interface";

    // get data
    const dataStore = useDataStore()
    const uiState = useUIStateStore();
    dataStore.database.requestData().then(
        (_) => {
            uiState.updateShownData();
        }
    );

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
        uiState.currentlySelectedTags = new DataTags(defaultTags.split("&&"));
        uiState.unfoldedTags = uiState.currentlySelectedTags.withParents().pop(uiState.currentlySelectedTags)
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


</script>

<template>
    <div id="main" class="gradIn">
        <Banner>
            <div class="searchbar">
                <label for="searchbar"> Search: </label>
                <select ref="searchSelector" name="search_type" id="searchType" @change="onSearchChanged">
                    <option v-for="v in searchTypesPool" :value="v">{{ v }}</option>
                </select>
                <input id="searchbar" type="text" v-model="searchInput" @input="onSearchChanged">
            </div>
        </Banner>
        <div class="horizontal fullHeight">
            <FileTags v-if="showFileTags" @onCheck="() => uiState.updateShownData()"></FileTags>
            <FileSelector></FileSelector>
        </div>
    </div>
</template>

<style scoped>
    #main{
        height: 96vh;
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
</style>