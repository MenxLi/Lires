<script setup lang="ts">
    import { ref } from "vue";
    import { DataBase, DataSearcher } from "./core/dataClass";
    import { FRONTENDURL } from "./config";
    import { ServerConn } from "./core/serverConn";
    import { getCookie } from "./libs/cookie";
    import { useTagSelectionStore } from "./components/store";
    import FileTags from "./components/FileTags.vue";
    import FileSelector from "./components/FileSelector.vue";
    import Banner from "./components/Banner.vue";

    import type { Ref } from "vue";
    import type { SearchStatus } from "./components/_interface";
    import type { DataPoint } from "./core/dataClass";

    const conn = new ServerConn();
    conn.authUsr(getCookie("encKey") as string).then(
        ()=>{},
        ()=>{window.location.href = `${FRONTENDURL}/login.html`},
    )

    const database = ref(new DataBase());
    database.value.requestData().then(
        (_) => {
            updateShownData();
        }
    );

    const searchStatus: Ref<SearchStatus> = ref({
        "content":""
    })
    function onSearchChanged(status: SearchStatus){
        searchStatus.value = status;
        updateShownData();
    }

    const tagStore = useTagSelectionStore();
    const showUids: Ref<string[]> = ref([]);
    function updateShownData(){
        const tagFilteredDataPoints = database.value.getDataByTags(tagStore.currentlySelected);
        DataSearcher.filter(tagFilteredDataPoints, searchStatus.value).then(
            (datapoints: DataPoint[]) => showUids.value = datapoints.map((dp) => dp.info.uuid)
        )
    }

</script>

<template>
    <div id="main" class="gradIn">
        <Banner :initSearchText="searchStatus['content']" @onSearchChange="onSearchChanged"></Banner>
        <div class="horizontal fullHeight">
            <FileTags :database="database" @onCheck="(_) => updateShownData()"></FileTags>
            <FileSelector :database="database" :showUids="showUids"></FileSelector>
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