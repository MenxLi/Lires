<script setup lang="ts">
    import { onMounted, ref, watch } from 'vue';
    import { DataPoint } from '../../core/dataClass';
    import NoteEditor from './NoteEditor.vue';

    const props = defineProps<{
        datapoint: DataPoint,
        layoutType: number
    }>();

    const leftPane = ref<HTMLElement | null>(null);
    const rightPane = ref<HTMLElement | null>(null);
    const splitter = ref<HTMLElement | null>(null);
    const onMovingSplitter = ref<boolean>(false);

    // resize event handlers
    function onSplitterMouseDown(){
        onMovingSplitter.value = true;
    }
    window.addEventListener('mouseup', () => {
        onMovingSplitter.value = false;
    });
    window.addEventListener('mousemove', (e) => {
        if (onMovingSplitter.value){
            const leftPaneWidth = e.clientX - leftPane.value!.getBoundingClientRect().left;
            leftPane.value!.style.width = `${leftPaneWidth}px`;
            rightPane.value!.style.width = `calc(100% - ${leftPaneWidth}px)`;
        }
    })

    // watch layoutType, reset the width of leftPane and rightPane
    function setLayout(layoutType: number){
        if (layoutType == 0){
            leftPane.value!.style.width = '100%';
            rightPane.value!.style.width = '0%';
        }
        else if (layoutType == 1){
            leftPane.value!.style.width = '0%';
            rightPane.value!.style.width = '100%';
        }
        else if (layoutType == 2){
            leftPane.value!.style.width = '50%';
            rightPane.value!.style.width = '50%';
        }
    }
    watch(() => props.layoutType, (newLayoutType, oldLayoutType) => {
        console.log('layoutType changed:', oldLayoutType, "->", newLayoutType);
        setLayout(newLayoutType);
    });
    
    // auto set layout when mounted
    onMounted(() => {
        setLayout(props.layoutType);
    })

</script>

<template>
    <div id="body">
        <div class="pane" id="leftPane" ref="leftPane">
            <!-- pointer event should be none when moving splitter, otherwise the iframe will capture the mouse event -->
            <iframe :src="datapoint.getOpenDocURL()" title="doc"
                :style="{'pointer-events': onMovingSplitter ? 'none' : 'auto'}"
            > </iframe>
        </div>
        <div id="splitter" ref="splitter" @mousedown="onSplitterMouseDown" v-if="layoutType==2"> </div>
        <div class="pane" id="rightPane" ref="rightPane">
            <NoteEditor :datapoint="datapoint"> </NoteEditor>
        </div>
    </div>
</template>

<style scoped>
div#body{
    display: flex;
    flex-direction: row;
    width: 100%;
    height: 100%;
}

div.pane{
    width: 100%;
    height: 100%;
}

iframe{
    width: 100%;
    height: 100%;
    border: 1px solid var(--color-border);
    border-radius: 10px;
    box-shadow: 0px 0px 5px var(--color-shadow);
}

#splitter{
    width: 8px;
    border-radius: 3px;
    height: 80%;
    align-self: center;
    background-color: var(--color-border);
    cursor: col-resize;
}
</style>