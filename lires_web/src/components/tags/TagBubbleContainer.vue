
<script setup lang="ts">
    import { DataTags } from '../../core/tag';
    import TagBubble from './TagBubble.vue';
    import { computed } from 'vue';

    const props = withDefaults(defineProps<{
        tags: DataTags | string[]
        highlightTags?: DataTags | null
        mutedTags?: DataTags | null
        maxWidth?: number | null
        middleAlign?: boolean
    }>(), {
        highlightTags: null,
        mutedTags: null,
        maxWidth: null,
        middleAlign: false,
    })

    const emit = defineEmits<{
        (e: "clickOnBubble", tag: string): void
    }>()

    const tagStyles = computed(() => {
        const style = {} as Record<string, "highlight" | "muted" | "">;
        for (const tag of props.tags){
            if (props.highlightTags && props.highlightTags.has(tag)){
                style[tag] = "highlight";
            }else if (props.mutedTags && props.mutedTags.has(tag)){
                style[tag] = "muted";
            }else{
                style[tag] = "";
            }
        }
        return style;
    })

</script>

<template>
    <div id="bubbleContainer" class="scrollable" 
        :style="{
            maxWidth: `${(props.maxWidth?props.maxWidth:999)-10}px`,
            justifyContent: props.middleAlign?'center':'flex-start',
            }">
        <TagBubble v-for="tag in props.tags" 
            @click="()=>emit('clickOnBubble', tag)"
            :tag="tag" 
            :t-style="tagStyles[tag]">
        </TagBubble>
    </div>
</template>

<style scoped>
div#bubbleContainer{
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 5px;
    padding: 5px;
    border-radius: 5px;
    overflow-y: auto;
}
</style>