<script setup lang="ts">
import { DataPoint } from '../core/dataClass';

const props = defineProps<{
    datapoint: DataPoint
}>()

</script>

<template>
    <div id="moreMain">
        <hr>
        <div class="row" id="buttons">
            <a :href="props.datapoint.getOpenDocURL()" target="_blank" rel="noopener noreferrer">Open</a>
            <a :href="props.datapoint.getOpenNoteURL()" target="_blank" rel="noopener noreferrer">Note</a>
        </div>
    </div>
</template>

<style scoped>
    hr{
        margin: 10px;
        border: 1px solid var(--color-border);
    }
    div.row{
        display: flex;
        align-items: center;
        justify-content: center;
    }
    div#buttons{
        gap: 15px
    }
</style>