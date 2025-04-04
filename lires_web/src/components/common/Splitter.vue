<script setup lang="ts">

    import { ref, onMounted, watch, nextTick } from 'vue';

    const props = withDefaults(defineProps<{
        direction?: 'horizontal' | 'vertical',
        movable?: boolean,
        minSplitRatio?: number,
        maxSplitRatio?: number,
        mode?: 'ab' | 'a' | 'b'
        splitterWidth?: string,
        overflow?: 'hidden' | 'auto' | 'scroll' | 'visible' | 'inherit' | 'initial' | 'unset',
    }>(), {
        movable: true,
        minSplitRatio: 0,
        maxSplitRatio: 1,
        mode: 'ab', 
        splitterWidth: '3px',
        overflow: 'auto',
    });

    const splitRatio = defineModel(
        'splitRatio', 
        { default: 0.5 }
    );

    const emits = defineEmits<{
        (e: 'moveStart', event: MouseEvent | TouchEvent): void,
        (e: 'moveStop'): void,
    }>();

    const container = ref<HTMLElement | null>(null);
    const aPane = ref<HTMLElement | null>(null);
    const bPane = ref<HTMLElement | null>(null);
    const splitter = ref<HTMLElement | null>(null);

    const isMovingSplitter = ref<boolean>(false);

    function updatePaneWidths(){
        if (props.mode == 'ab' && aPane.value && bPane.value){
            if (props.direction === 'vertical') {
                aPane.value!.style.width = `calc(${splitRatio.value * 100}%)`;
                bPane.value!.style.width = `calc(${(1 - splitRatio.value) * 100}%)`;
            } else {
                aPane.value!.style.height = `calc(${splitRatio.value * 100}%)`;
                bPane.value!.style.height = `calc(${(1 - splitRatio.value) * 100}%)`;
            }
        }
        if (props.mode == 'a' && aPane.value){
            if (props.direction === 'vertical') {
                aPane.value!.style.width = `100%`;
            } else {
                aPane.value!.style.height = `100%`;
            }
        }
        if (props.mode == 'b' && bPane.value){
            if (props.direction === 'vertical') {
                bPane.value!.style.width = `100%`;
            } else {
                bPane.value!.style.height = `100%`;
            }
        }
    }

    function onStartMovingSplitter(event: MouseEvent | TouchEvent){
        if (splitter.value && splitter.value.contains(event.target as Node)){
            isMovingSplitter.value = true;
        }
        emits('moveStart', event);
    }
    function onStopMovingSplitter(){
        isMovingSplitter.value = false;
        emits('moveStop');
    }
    function onMovingSplitter(event: MouseEvent | TouchEvent) {
        if (isMovingSplitter.value && aPane.value && bPane.value && splitter.value) {
            const clientX = 'touches' in event ? event.touches[0].clientX : event.clientX;
            const clientY = 'touches' in event ? event.touches[0].clientY : event.clientY;
            const arect = aPane.value.getBoundingClientRect();
            const allrect = container.value!.getBoundingClientRect();
            const splitRatioValue = props.direction === 'vertical' ?
                (clientX - arect.left) / allrect.width :
                (clientY - arect.top) / allrect.height;
            splitRatio.value = Math.max(props.minSplitRatio!, Math.min(props.maxSplitRatio!, splitRatioValue));
            event.preventDefault();
        }
    }

    // Event listeners for both mouse and touch events
    window.addEventListener('mousedown', onStartMovingSplitter);
    window.addEventListener('touchstart', onStartMovingSplitter);

    window.addEventListener('mouseup', onStopMovingSplitter);
    window.addEventListener('touchend', onStopMovingSplitter);

    window.addEventListener('mousemove', onMovingSplitter);
    window.addEventListener('touchmove', onMovingSplitter);

    watch(
        ()=>[props.direction, props.mode, splitRatio.value],
        ()=>{
            // it's a trick to make it work with v-if
            nextTick(updatePaneWidths);
        },
    )
    onMounted(()=>{
        updatePaneWidths();
    });
</script>

<template>
    <div id="sp-container" ref="container" :style="
        props.direction === 'vertical' ? 
        { flexDirection: 'row' } : 
        { flexDirection: 'column' }
    ">
        <div ref="aPane" class="splitter-pane panel" 
            :style="{ overflow: props.overflow }"
            v-if="props.mode == 'ab' || props.mode == 'a'">
            <slot name="a"></slot>
        </div>
        <div ref="splitter" class="splitter" v-if="props.mode == 'ab' && props.movable"
            :style="
                props.direction === 'vertical' ? 
                { cursor: 'col-resize', height: '100%', width: splitterWidth } : 
                { cursor: 'row-resize', width: '100%', height: splitterWidth }
                "
        ></div>
        <div ref="bPane" class="splitter-pane panel" 
            :style="{ overflow: props.overflow }"
            v-if="props.mode == 'ab' || props.mode == 'b'">
            <slot name="b"></slot>
        </div>
    </div>
</template>

<style scoped>
    #sp-container {
        display: flex;
        height: 100%;
        width: 100%;
        padding: 0;
        margin: 0;
    }
    .splitter-pane {
        position: relative;
        flex-grow: 1;
        padding: 0px;
        margin: 0px;
    }
    .splitter {
        display: block;
        background-color: var(--color-border);
        transition-delay: 0s;
    }
    .splitter:hover, .splitter:active {
        background-color: var(--color-theme);
        transition-delay: 0.5s;
    }
</style>