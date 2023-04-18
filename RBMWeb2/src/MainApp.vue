<script setup lang="ts">
    import { ref } from "vue";
    import { DataBase, DataSearcher } from "./core/dataClass";
    import { FRONTENDURL } from "./config";
    import { ServerConn } from "./core/serverConn";
    import { getCookie } from "./libs/cookie";
    import FileTags from "./components/FileTags.vue";
    import FileSelector from "./components/FileSelector.vue";
    import Banner from "./components/Banner.vue";

    import type { Ref } from "vue";
    import type { TagCheckStatus } from "./components/_interface";
    import type { SearchStatus } from "./components/_interface";
import type { DataPoint } from "./core/dataClass";

    const conn = new ServerConn();
    conn.authUsr(getCookie("encKey") as string).then(
        ()=>{},
        ()=>{window.location.href = `${FRONTENDURL}/login.html`},
    )

    const database = new DataBase();
    const loaded = ref(false);
    database.requestData().then(
        (_) => {
            loaded.value = true;
            updateShownData();
        }
    );

    const selectedTags: Ref<string[]> = ref([]);
    function onTagSelected(status: TagCheckStatus){
        selectedTags.value = status["currentlySelected"];
        updateShownData();
    }

    const searchStatus: Ref<SearchStatus> = ref({
        "content":""
    })
    function onSearchChanged(status: SearchStatus){
        searchStatus.value = status;
        updateShownData();
    }

    const showUids: Ref<string[]> = ref([]);
    function updateShownData(){
        const tagFilteredDataPoints = database.getDataByTags(selectedTags.value);
        DataSearcher.filter(tagFilteredDataPoints, searchStatus.value).then(
            (datapoints: DataPoint[]) => showUids.value = datapoints.map((dp) => dp.info.uuid)
        )
    }

</script>

<template>
    <div id="main" class="gradIn2">
        <Banner :initSearchText="searchStatus['content']" @onSearchChange="onSearchChanged"></Banner>
        <div class="horizontal fullHeight">
            <FileTags v-if="loaded" :database="database" @onCheck="onTagSelected"></FileTags>
            <FileSelector v-if="loaded" :database="database" :showUids="showUids"></FileSelector>
        </div>
    </div>
</template>

<style scoped>
    #main{
        height: 95vh;
        width: 95vw;
        display: flex;
        flex-direction: column;
    }
    .fullHeight{
        height: 100%;
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