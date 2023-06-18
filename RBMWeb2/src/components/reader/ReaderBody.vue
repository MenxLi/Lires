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

    function onStartMovingSplitter(){
        onMovingSplitter.value = true;
    }
    function onStopMovingSplitter(){
        onMovingSplitter.value = false;
    }
    function onMoveSplitter(event: MouseEvent | TouchEvent) {
        if (onMovingSplitter.value) {
            const clientX = 'touches' in event ? event.touches[0].clientX : event.clientX;
            const leftPaneWidth = clientX - leftPane.value!.getBoundingClientRect().left;
            leftPane.value!.style.width = `${leftPaneWidth}px`;
            rightPane.value!.style.width = `calc(100% - ${leftPaneWidth}px)`;
        }
    }

    // resize event handlers
    // Event listeners for both mouse and touch events
    window.addEventListener('mousedown', onStartMovingSplitter);
    window.addEventListener('touchstart', onStartMovingSplitter);

    window.addEventListener('mouseup', onStopMovingSplitter);
    window.addEventListener('touchend', onStopMovingSplitter);

    window.addEventListener('mousemove', onMoveSplitter);
    window.addEventListener('touchmove', onMoveSplitter);

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
    const pdfviewerURL = "https://mozilla.github.io/pdf.js/web/viewer.html"
    onMounted(() => {
        setLayout(props.layoutType);
        // // full screen iframe (leftPane)
        // const fullScreenStyle = {
        //     position: 'fixed',
        //     top: '0px',
        //     left: '0px',
        //     width: '100%',
        //     height: '100%',
        //     border: 'none',
        //     margin: '0px',
        //     padding: '0px',
        //     overflow: 'hidden',
        //     'z-index': '999999'
        // }
        // // set style
        // Object.assign(leftPane.value!.style, fullScreenStyle);
    })

</script>

<template>
    <div id="body">
        <div class="pane" id="leftPane" ref="leftPane">
            <!-- pointer event should be none when moving splitter, otherwise the iframe will capture the mouse event -->
            <div id="iframeWrapper">
                <!-- <iframe :src="datapoint.getOpenDocURL()" title="doc"
                    :style="{'pointer-events': onMovingSplitter ? 'none' : 'auto'}"
                > </iframe> -->
                <!-- <iframe :src="datapoint.getOpenDocURL()" title="doc" > </iframe> -->
                <!-- <iframe :src="datapoint.getOpenDocURL()" title="doc" > </iframe> -->
                <iframe :src="`${pdfviewerURL}?file=${datapoint.getOpenDocURL()}`"> </iframe>
            </div>
        </div>
        <div id="splitter" ref="splitter" @mousedown="onStartMovingSplitter" @touchstart="onStartMovingSplitter" v-if="layoutType==2"> </div>
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

/* https://blog.csdn.net/baidu_41828042/article/details/108984155 */
#iframeWrapper{
    width: 100%;
    height: 100%;
    padding: 10px;
    overflow: auto;
    -webkit-overflow-scrolling: touch;
    display: block;
}

iframe{
    display: block;
    width: 100%;
    height: 100%;
    border: 1px solid var(--color-border);
    border-radius: 10px;
    box-shadow: 0px 0px 5px var(--color-shadow);
    -webkit-overflow-scrolling: touch;
    /* overflow: scroll; */
}

#splitter{
    width: 5px;
    margin:4px;
    border-radius: 3px;
    height: 70%;
    align-self: center;
    background-color: var(--color-border);
    cursor: col-resize;
}
</style>