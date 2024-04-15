<script setup lang="ts">
    import { onMounted, ref, watch, computed } from 'vue';
    import { useRouter } from 'vue-router';
    import NoteEditor from './NoteEditor.vue';
    import { useUIStateStore, useSettingsStore } from '../store';
    import { DataPoint } from '../../core/dataClass';
    import { ThemeMode } from '../../core/misc';
    import { FileSelectButton } from '../common/fragments';

    const props = defineProps<{
        datapoint: DataPoint,
        layoutType: number,
    }>()

    const router = useRouter();
    const urlHashMarkParam = computed(()=>{
        const query = router.currentRoute.value.query;
        const docHashMark = query['docHashMark'] as string | undefined;
        if (docHashMark){ return docHashMark; }
        return '';
    });

    const leftPane = ref<HTMLElement | null>(null);
    const rightPane = ref<HTMLElement | null>(null);
    const splitter = ref<HTMLElement | null>(null);
    const onMovingSplitter = ref<boolean>(false);
    const noteEditor = ref<typeof NoteEditor | null>(null);
    // const togglePreview = (state: boolean)=>{ noteEditor.value!.togglePreview(state);}
    defineExpose({
        noteEditor,
    });

    function onStartMovingSplitter(event: MouseEvent | TouchEvent){
        if (splitter.value && splitter.value.contains(event.target as Node)){
            onMovingSplitter.value = true;
        }
    }
    function onStopMovingSplitter(){
        onMovingSplitter.value = false;
    }
    const leftPaneWidthRatio = computed({
        // a proxy to uiState.preferedReaderLeftPanelWidthPerc, for convenience
        get: () => useUIStateStore().preferredReaderLeftPanelWidthPerc,
        set: (val) => {useUIStateStore().preferredReaderLeftPanelWidthPerc = val}
    });
    function onMoveSplitter(event: MouseEvent | TouchEvent) {
        if (onMovingSplitter.value && leftPane.value && rightPane.value && splitter.value) {
            const clientX = 'touches' in event ? event.touches[0].clientX : event.clientX;
            const leftPaneWidth = clientX - leftPane.value!.getBoundingClientRect().left;
            leftPane.value!.style.width = `${leftPaneWidth}px`;
            rightPane.value!.style.width = `calc(100% - ${leftPaneWidth}px)`;
            // record the width ratio for next time switching layout
            leftPaneWidthRatio.value = leftPaneWidth / (leftPaneWidth + rightPane.value!.getBoundingClientRect().width);
            leftPaneWidthRatio.value = Math.max(0.1, Math.min(0.9, leftPaneWidthRatio.value));
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
    const showLeftPane = computed(()=>props.layoutType == 0 || props.layoutType == 2);
    const showRightPane = computed(()=>props.layoutType == 1 || props.layoutType == 2);
    function setLayout(layoutType: number){
        if (layoutType == 2){
            leftPane.value!.style.width = `${leftPaneWidthRatio.value * 100}%`;
            rightPane.value!.style.width = `${(1 - leftPaneWidthRatio.value) * 100}%`;
        }
        useSettingsStore().setReaderLayoutType(layoutType);
    }
    watch(() => props.layoutType, (newLayoutType, oldLayoutType) => {
        console.log('layoutType changed:', oldLayoutType, "->", newLayoutType);
        setLayout(newLayoutType);
    });

    const theme = ref(ThemeMode.isDarkMode()?'dark':'light' as 'dark'|'light')
    ThemeMode.registerThemeChangeCallback(()=>theme.value = ThemeMode.isDarkMode()?'dark' : 'light')
    const openDocURL = computed(()=>`${props.datapoint.getOpenDocURL({
            extraPDFViewerParams: { "color-mode": theme.value, },
            urlHashMark: urlHashMarkParam.value,
        })}`)
    
    // auto set layout when mounted
    onMounted(() => {
        setLayout(props.layoutType);
    })

</script>

<template>
    <div id="body">
        <div class="pane" id="left-pane" ref="leftPane" v-show="showLeftPane">
            <!-- pointer event should be none when moving splitter, otherwise the iframe will capture the mouse event -->
            <iframe :src="openDocURL" title="doc" frameborder="0" v-if="datapoint.summary.has_file"
                :style="{'pointer-events': onMovingSplitter ? 'none' : 'auto'}"
            > </iframe>

            <div style="display: flex; justify-content: center; align-items: center; height: 100%; width: 100%" v-else
                @dragover="($event)=>$event.preventDefault()"
                @drop="($ev: DragEvent)=>{
                    $ev.preventDefault();
                    const files = $ev.dataTransfer?.files;
                    useUIStateStore().showPopup('Upload file', 'info');
                    if (files && files.length == 1){
                        datapoint.uploadDocument(files[0]).then(()=>{
                            useUIStateStore().showPopup(
                                'File uploaded', 'success'
                            )
                        })
                    }
                }"
            >
                <div style="color: var(--color-text-soft); font-weight: bold; font-size: large;">No file, 
                    drag and drop to&nbsp;
                </div>
                <FileSelectButton :action="(f: File)=>datapoint.uploadDocument(f)" text="upload" :as-link="true" 
                style="font-weight: bold; font-size: large; cursor: pointer;">
                </FileSelectButton>
            </div>
            
        </div>
        <div id="splitter" ref="splitter" @mousedown="onStartMovingSplitter" @touchstart="onStartMovingSplitter" v-if="layoutType==2"> </div>
        <div class="pane" id="right-pane" ref="rightPane" v-show="showRightPane">
            <NoteEditor :datapoint="datapoint" :theme="theme" ref="noteEditor"> </NoteEditor>
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
    flex-grow: 1;
}

iframe{
    width: 100%;
    height: 100%;
    border: 1px solid var(--color-border);
    /* border-radius: 10px; */
    box-shadow: 0px 0px 5px var(--color-shadow);
    /* -webkit-overflow-scrolling: touch; */
    /* overflow: scroll; */
}
@media only screen and (max-width: 767px) {
    iframe{
        border-radius: 0px;
    }
}

#splitter{
    width: 0.2rem;
    margin: 0rem;
    border-radius: 3px;
    /* height: 70%; */
    height: 100%;
    align-self: center;
    background-color: var(--color-border);
    cursor: col-resize;
}
#splitter:hover{
    background-color: var(--color-theme);
}
</style>