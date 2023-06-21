<!-- a container that governs the display of multiple FileRow components -->
<script setup lang="ts">
    import { computed } from 'vue';
    import FileRow from './FileRow.vue';
    import { type DataCardsStatus } from '../interface';
    import { type DataPoint } from '../../core/dataClass';

    // v-model
    const props = withDefaults(defineProps<DataCardsStatus>(), {
        unfoldedIds: ()=>[],
    })

    const emits = defineEmits<{
        (e: "update:datapoints", v: DataPoint[]): void
        (e: "update:unfoldedIds", v: string[]): void
    }>();


    // pass props
    const unfoldedIds = computed({
        get: ()=>props.unfoldedIds,
        set: (v)=>emits("update:unfoldedIds", v)}
    );
    const datapoints = computed({
        get: ()=>props.datapoints,
        set: (v)=>emits("update:datapoints", v)}
    )

</script>

<template>
    <div id="dataCardContainer">
        <FileRow v-for="dp in datapoints" :datapoint="dp" v-model:unfolded-ids="unfoldedIds"></FileRow>
    </div>
</template>

<style scoped>
    #dataCardContainer{
        display: flex;
        flex-direction: column;
        gap: 5px;
    }
</style>