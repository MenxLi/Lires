<script setup lang="ts">
    import { onMounted, ref, watch, computed } from 'vue';
    import { useRouter } from 'vue-router';
    import NoteEditor from './NoteEditor.vue';
    import { useUIStateStore, useSettingsStore } from '../store';
    import { DataPoint } from '../../core/dataClass';
    import { ThemeMode } from '../../core/misc';
    import { FileSelectButton } from '../common/fragments';
    import Splitter from '../common/Splitter.vue';

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

    const isMovingSplitter = ref<boolean>(false);
    const noteEditor = ref<typeof NoteEditor | null>(null);
    // const togglePreview = (state: boolean)=>{ noteEditor.value!.togglePreview(state);}
    defineExpose({
        noteEditor,
    });

    function setLayout(layoutType: number){
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
        <!-- <div class="pane" id="left-pane" ref="leftPane" v-show="showLeftPane"> -->
        <Splitter direction="vertical" 
        v-model:split-ratio="useUIStateStore().preferredReaderLeftPanelWidthPerc"
        :mode="({
            0: 'a',
            1: 'b',
            2: 'ab',
        }[layoutType] as 'a'|'b'|'ab')"
        @move-start="()=>isMovingSplitter=true" 
        @move-stop="()=>isMovingSplitter=false"
        >
            <template v-slot:a>
                <!-- pointer event should be none when moving splitter, otherwise the iframe will capture the mouse event -->
                <iframe :src="openDocURL" title="doc" frameborder="0" v-if="datapoint.summary.has_file"
                    :style="{'pointer-events': isMovingSplitter ? 'none' : 'auto'}"
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
            </template>
            <template v-slot:b>
                <NoteEditor :datapoint="datapoint" :theme="theme" ref="noteEditor"> </NoteEditor>
            </template>
        </Splitter>
    </div>
</template>

<style scoped>
div#body{
    display: flex;
    flex-direction: row;
    width: 100%;
    height: 100%;
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