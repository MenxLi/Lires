<script setup lang="ts">
    import { ref } from "vue";
    import { DataBase } from "./core/dataClass";
    import TagSelector from "@/components/TagSelector.vue"

    import type { TagCheckStatus } from "./components/_interface";

    const database = new DataBase();
    const loaded = ref(false)

    database.requestData().then(
        (_) => loaded.value = true
    );

    function onTagSelected(status: TagCheckStatus){
        console.log(status);
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