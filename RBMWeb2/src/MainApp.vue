<script setup lang="ts">
    import { ref } from "vue";
    import { DataBase, TagRule } from "./core/dataClass";
    import TagSelector from "@/components/TagSelector.vue"
    import FileSelector from "./components/FileSelector.vue";

    import type { Ref } from "vue";
    import type { TagCheckStatus } from "./components/_interface";

    const database = new DataBase();
    const loaded = ref(false);
    const selectedTags: Ref<string[]> = ref([]);
    const showUids: Ref<string[]> = ref([]);

    database.requestData().then(
        (_) => {
            loaded.value = true;
            updateShownData();
        }
    );

    function updateShownData(){
        showUids.value = database.getUidByTags(selectedTags.value);
    }

    function onTagSelected(status: TagCheckStatus){
        selectedTags.value = status["currentlySelected"];
        updateShownData();
    }
</script>

<template>
    <div id="main">
        <table class="fullHeight">
            <tr>
                <td id="fileTags">
                    <TagSelector v-if="loaded" :database="database" @onCheck="onTagSelected"></TagSelector>
                </td>
                <td id="fileSelector" class="fullWidth">
                    <FileSelector v-if="loaded" :database="database" :showUids="showUids"></FileSelector>
                </td>
            </tr>
        </table>
    </div>
</template>

<style scoped>
    #main{
        height: 95vh;
        width: 95vw;
    }
    .fullHeight{
        height: 100%;
    }
    .fullWidth{
        width: 100%;
    }
</style>