<script setup lang="ts">
    import { ref, computed, onMounted } from "vue";
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

    function onSearchChanged(status: SearchStatus){
        uiState.searchState = status;
        uiState.updateShownData();
    }

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

</script>

<template>
    <div id="main" class="gradIn">
        <Banner :searchText="uiState.searchState['content']" @onSearchChange="onSearchChanged"></Banner>
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