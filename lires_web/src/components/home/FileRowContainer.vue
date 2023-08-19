<!-- a container that governs the display of multiple FileRow components -->
<script setup lang="ts">
    import { computed } from 'vue';
    import FileRow from './FileRow.vue';
    import { type DataPoint } from '../../core/dataClass';

    interface DataCardsStatus{
        datapoints: DataPoint[],
        unfoldedIds?: string[],
        scores?: Record<string, number|string> | null,
        compact?: boolean,
    }

    // MUST USE V_MODEL TO PASS unfoldedIds !!
    const props = withDefaults(defineProps<DataCardsStatus>(), {
        unfoldedIds: ()=>[],
        scores: null,
        compact: true,
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
    <div id="dataCardContainer" :style="{gap: compact?'0px':'5px'}">
        <FileRow v-for="dp, idx in datapoints" :datapoint="dp" v-model:unfolded-ids="unfoldedIds" :line_number="idx" :compact="compact">
            <label class="relatedArticleScore" v-if="props.scores != null && props.scores[dp.summary.uuid] != null">
                {{ props.scores[dp.summary.uuid] }}
            </label>
        </FileRow>
    </div>
</template>

<style scoped>
    #dataCardContainer{
        display: flex;
        flex-direction: column;
        width: 100%;
        overflow-x: hidden;
    }
    label.relatedArticleScore{
        border-radius: 5px;
        padding-left: 5px;
        padding-right: 5px;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: var(--color-background-theme-highlight);
    }
</style>