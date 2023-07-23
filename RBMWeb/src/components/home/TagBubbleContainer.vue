
<script setup lang="ts">
    import { DataTags } from '../../core/dataClass';
    import TagBubble from './TagBubble.vue';

    const props = withDefaults(defineProps<{
        tags: DataTags
        highlightTags?: DataTags | null
        maxWidth?: number | null
    }>(), {
        highlightTags: null,
        maxWidth: null
    })

</script>

<template>
    <div id="bubbleContainer" :style="{maxWidth: `${(props.maxWidth?props.maxWidth:999)-10}px`}">
        <TagBubble v-for="tag in props.tags" :tag="tag" :highlight="props.highlightTags? props.highlightTags.has(tag) : false"></TagBubble>
    </div>
</template>

<style scoped>
div#bubbleContainer{
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-start;
    align-items: center;
    overflow: hidden;
    gap: 5px;
    padding: 5px;
    border-radius: 5px;
    overflow-y: auto;
}
</style>