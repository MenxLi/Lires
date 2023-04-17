
<script setup lang="ts">

    import type { DataPoint } from '@/core/dataClass';
    const props = defineProps<{
        datapoint: DataPoint
    }>()

    function openDataURL(){
        const url = props.datapoint.getOpenDocURL()
        if (url){
            window.open(url);
        }
    }
</script>

<template>
    <div class="row hoverMaxout101" @click="(ev) => openDataURL()">
        <div id="authorYear" class="text">{{ datapoint.authorYear() }}</div>
        <div class="text">{{ datapoint.info.title }}</div>
    </div>
</template>

<style scoped>
    div.row {
        display: flex;
        flex-wrap: wrap;
        border: 1px solid var(--color-border);
        border-radius: 5px;
        column-gap: 10px;
        align-items: center;
        padding-left: 3px;
        margin-top: 3px;
        margin-bottom: 3px;
    }
    div.row:hover{
        background-color: var(--theme-hover-hight-color);
    }
    #authorYear{
        width: 200px;
        background-color: transparent;
    }
    div.text{
        padding: 0px;
        margin: 0px;
    }
</style>