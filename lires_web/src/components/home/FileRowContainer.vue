<!-- a container that governs the display of multiple FileRow components -->
<script setup lang="ts">
    import { computed, ref } from 'vue';
    import FileRow from './FileRow.vue';
    import { type DataPoint } from '../../core/dataClass';

    interface DataCardsStatus{
        datapoints: DataPoint[],
        unfoldedIds?: string[] | null,
        hoveredIds?: string[] | null,
        scores?: Record<string, number|string> | null,
        compact?: boolean,
    }

    // MUST USE V_MODEL TO PASS unfoldedIds !!
    const props = withDefaults(defineProps<DataCardsStatus>(), {
        unfoldedIds: null,
        hoveredIds: null,
        scores: null,
        compact: true,
    })

    const emits = defineEmits<{
        (e: "update:datapoints", v: DataPoint[]): void,
        (e: "update:unfoldedIds", v: string[]): void,
        (e: "update:hoveredIds", v: string[]): void,
    }>();

    // pass props
    const __default_unfoldedIds = ref([] as string[]);
    const unfoldedIds = computed({
        get: ()=>{
            if (props.unfoldedIds == null){ return __default_unfoldedIds.value; }
            else { return props.unfoldedIds }
        },
        set: (v)=>{
            if (props.unfoldedIds == null){ __default_unfoldedIds.value = v; }
            else { emits("update:unfoldedIds", v)}
        }
    });

    const __default_hoveredIds = ref([] as string[]);
    const hoveredIds = computed({
        get: ()=>{
            if (props.hoveredIds == null){ return __default_hoveredIds.value; }
            else { return props.hoveredIds }
        },
        set: (v)=>{
            if (props.hoveredIds == null){ __default_hoveredIds.value = v; }
            else { emits("update:hoveredIds", v)}
        }
    });

    const datapoints = computed({
        get: ()=>props.datapoints,
        set: (v)=>emits("update:datapoints", v)}
    )

</script>

<template>
    <div id="dataCardContainer" :style="{gap: compact?'0px':'5px'}">
        <FileRow v-for="dp, idx in datapoints" :datapoint="dp" 
                v-model:unfolded-ids="unfoldedIds" v-model:hovered-ids="hoveredIds"
                :line_number="idx" :compact="compact">
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
        overflow-x: hidden;
        width: 100%;
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