<script setup lang="ts">
    import { FRONTENDURL } from "./config";
    import { ServerConn } from "./core/serverConn";
    import { getCookie } from "./libs/cookie";
    import { useUIStateStore, useDataStore } from "./components/store";
    import FileTags from "./components/FileTags.vue";
    import FileSelector from "./components/FileSelector.vue";
    import Banner from "./components/Banner.vue";

    import type { SearchStatus } from "./components/_interface";

    const conn = new ServerConn();
    conn.authUsr(getCookie("encKey") as string).then(
        ()=>{},
        ()=>{window.location.href = `${FRONTENDURL}/login.html`},
    )

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

</script>

<template>
    <div id="main" class="gradIn">
        <Banner :initSearchText="uiState.searchState['content']" @onSearchChange="onSearchChanged"></Banner>
        <div class="horizontal fullHeight">
            <FileTags @onCheck="(_) => uiState.updateShownData()"></FileTags>
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