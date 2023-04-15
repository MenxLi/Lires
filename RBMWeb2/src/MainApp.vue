<script setup lang="ts">
import { ref } from "vue";
import { DataBase } from "./core/dataClass";
import TagSelector from "@/components/TagSelector.vue"

const database = new DataBase();
const loaded = ref(false)

database.requestData().then(
    (_) => loaded.value = true
);

function onTagSelected(tag: string, selected: boolean){
    if (selected){
        console.log("TagSelected: ", tag);
    }
    else{
        console.log("TagUnSelected: ", tag);
    }
}

</script>

<template>
    <div id="main">
        <TagSelector v-if="loaded" :database="database" @onCheck="onTagSelected"></TagSelector>
    </div>
</template>

<style scoped>
    #main{
        height: 95vh;
    }
</style>