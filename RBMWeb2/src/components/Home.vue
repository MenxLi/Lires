<script setup lang="ts">
    import { ref, computed, onMounted } from "vue";
    import type { Ref } from "vue";
    import { FRONTENDURL } from "../config";
    import { ServerConn } from "../core/serverConn";
    import { getCookie } from "../libs/cookie";
    import { useUIStateStore, useDataStore } from "./store";
    import { DataTags } from "../core/dataClass";
    import FileTags from "./home/FileTags.vue";
    import FileSelector from "./home/FileSelector.vue";
    import Banner from "./common/Banner.vue";

    import type { SearchStatus } from "./home/_interface";

    // check login
    const conn = new ServerConn();
    conn.authUsr(getCookie("encKey") as string).then(
        ()=>{},
        function(){
            const loginSearchParams = new URLSearchParams();
            loginSearchParams.append("from", window.location.href);
            window.location.href = `${FRONTENDURL}/login.html?${loginSearchParams.toString()}`
        },
    )

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

    // maybe change tag from url search params
    const urlSearchParams = new URLSearchParams(window.location.search);
    const defaultTags = urlSearchParams.get("tags")?.split("&&");
    if (defaultTags != undefined){
        uiState.currentlySelectedTags = new DataTags(defaultTags);
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