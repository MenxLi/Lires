
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
        <div id="authorYear" class="text">{{ datapoint.yearAuthor(" :: ")}}</div>
        <div id="title" class="text">{{ datapoint.info.title }}</div>
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
        justify-content: flex-start;
        padding-left: 3px;
        margin-top: 3px;
        margin-bottom: 3px;
    }
    div.row:hover{
        background-color: var(--theme-hover-hight-color);
    }
    #authorYear{
        width: 250px;
        white-space: nowrap;
        background-color: var(--color-background-soft);
        border-radius: 10px;
        margin: 5px;
        margin-top: 3px;
        margin-bottom: 3px;
        padding: 5px;
        padding-top: 3px;
        padding-bottom: 3px;
    }
    div.text{
        padding: 0px;
        margin: 0px;
        text-align: left;
        text-overflow: ellipsis;
        overflow: hidden;
    }

    @media (max-width: 1500px){
        div.row{
            flex-direction: column;
            align-items:flex-start;
        }
    }
    @media (max-width: 750px){
        #authorYear{
            width: 180px;
        }
    }
</style>