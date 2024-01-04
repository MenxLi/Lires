<!-- a container that governs the display of multiple FileRow components -->
<script setup lang="ts">
    import { computed, ref } from 'vue';
    import FileRow from './FileRow.vue';
    import { type DataPoint } from '../../core/dataClass';
    import { EditableParagraph } from '../common/fragments';

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

    const datacardContainer = ref(null as HTMLDivElement | null);
    const pageIndicatorEditableParagrah = ref(null as any | null);
    const shownPage = ref(0);
    const shownNumPerPage = ref(100);
    const shownDatapoints = computed(()=>{
        const startIdx = shownPage.value * shownNumPerPage.value;
        const endIdx = Math.min(startIdx + shownNumPerPage.value, datapoints.value.length);
        return datapoints.value.slice(startIdx, endIdx);
    })
    const onNextPage = ()=>{
        if (shownPage.value >= Math.ceil(datapoints.value.length / shownNumPerPage.value) - 1){ return; }
        shownPage.value++;
        pageIndicatorEditableParagrah.value!.setText("" + (shownPage.value + 1));
        datacardContainer.value?.scrollTo({top: 0, behavior: 'auto'});  // auto, smooth, instant
    }
    const onPrevPage = ()=>{
        if (shownPage.value == 0){ return; }
        shownPage.value--;
        pageIndicatorEditableParagrah.value!.setText("" + (shownPage.value + 1));
        datacardContainer.value?.scrollTo({top: 0, behavior: 'auto'});
    }
    const onScroll = (e: Event)=>{
        const target = e.target as HTMLDivElement;
        if (target.scrollTop == 0){
            // to add more in the future...
            // console.log("scroll to top");
        }else if (target.scrollTop + target.clientHeight >= target.scrollHeight){
            // to add more in the future...
            // console.log("scroll to bottom");
        }
    }

</script>

<template>
    <div id="datacard-container-main">
        <div id="datacard-container" :style="{gap: compact?'0px':'5px'}" ref="datacardContainer" @scroll="onScroll">
            <FileRow v-for="dp, idx in shownDatapoints" :datapoint="dp" 
                    v-model:unfolded-ids="unfoldedIds" v-model:hovered-ids="hoveredIds"
                    :line_number="idx" :compact="compact">
                <label class="relatedArticleScore" v-if="props.scores != null && props.scores[dp.summary.uuid] != null">
                    {{ props.scores[dp.summary.uuid] }}
                </label>
            </FileRow>
        </div>
        <div id="datacard-container-footer" v-if="datapoints.length > shownNumPerPage">
            <button @click="onPrevPage" :disabled="shownPage == 0">Prev</button>
            <span style="margin-left: 10px; margin-right: 10px; display: flex; gap: 5px">
                <EditableParagraph ref="pageIndicatorEditableParagrah" @finish="(val: any) => {
                    if(/^\d+$/.test((val as string)) && parseInt(val) > 0 && parseInt(val) <= Math.ceil(datapoints.length / shownNumPerPage)){
                        shownPage = parseInt(val) - 1;
                    }}">
                    {{shownPage + 1}}
                </EditableParagraph> / <p>{{ Math.ceil(datapoints.length / shownNumPerPage) }}</p>
            </span>

            <button @click="onNextPage" :disabled="shownPage >= Math.ceil(datapoints.length / shownNumPerPage) - 1">Next</button>
        </div>
    </div>
</template>

<style scoped>
    #datacard-container-main{
        display: flex;
        flex-direction: column;
        align-items:center;
        justify-content: space-between;
        width: 100%;
        height: 100%;
        overflow-y: auto;
        overflow-x: hidden;
    }
    #datacard-container{
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

    #datacard-container-footer{
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: center;
        width: 100%;
        margin-top: 5px;
        margin-bottom: 5px;
    }
    #datacard-container-footer button{
        border-radius: 5px;
        padding-inline: 20px;
        padding-block: 5px;
        font-weight: bold;
        color: var(--color-text);
        border: none;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.15s ease-in-out;
    }
    #datacard-container-footer button:hover{
        background-color: var(--color-background-theme-highlight);
        transform: scale(1.05);
    }
    #datacard-container-footer button:active{
        transform: scale(0.95);
    }
    #datacard-container-footer button:disabled{
        color: var(--color-text-soft);
    }
    #datacard-container-footer button:disabled:hover{
        background-color: transparent;
    }
</style>