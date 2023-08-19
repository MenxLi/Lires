
<script setup lang="ts">
    import { ref, computed, watch } from 'vue';
    import FloatingWindow from '../common/FloatingWindow.vue';
    import TagSelector from './TagSelector.vue';
    import { useUIStateStore, useDataStore } from '../store';
    import { DataTags, TagRule } from '../../core/dataClass';
    import { ServerConn } from '../../core/serverConn';
    import type { DataPoint } from '../../core/dataClass';
    import type { TagStatus } from '../interface';

    const props = defineProps<{
        datapoint: DataPoint | null,
        show: boolean,
    }>();

    const emits = defineEmits<{
        (e: "update:show", show: boolean): void
    }>();

    const show = computed({
        get: () => props.show,
        set: (newShow: boolean) => emits("update:show", newShow)
    });

    const uiState = useUIStateStore();
    // data ref
    const bibtex = ref("");
    const url = ref("");
    const tagStatus = ref<TagStatus>({
        all: new DataTags(),
        checked: new DataTags(),
        unfolded: new DataTags(),
    });

    // methods
    function save(){
        let uuid = null;
        if (props.datapoint){
            uuid = props.datapoint.summary.uuid;
        }
        new ServerConn().editData(uuid, bibtex.value, Array.from(tagStatus.value.checked), url.value).then(
            (summary) => {
                if (props.datapoint){
                    props.datapoint.update(summary);
                } else {
                    useDataStore().database.add(summary);
                }
                uiState.updateShownData();
                uiState.showPopup("Saved", "success");
                show.value = false;
            },
            () => uiState.showPopup("Failed to save", "error")
        )
    }
    const newTagInput = ref("");
    function addNewTag(){
        const tag = newTagInput.value.trim();
        if (tag === ""){ return; }
        tagStatus.value.checked.add(tag);
        tagStatus.value.all.add(tag);
        tagStatus.value.unfolded.union_(TagRule.allParentsOf(tag));
    }

    watch(show, (newShow) => {
        // init data on every showup!
        if (newShow){
            if (props.datapoint){ bibtex.value = props.datapoint.summary.bibtex; }
            else { bibtex.value = "";}
            if (props.datapoint){ url.value = props.datapoint.summary.url; }
            else { url.value = "";}
            tagStatus.value = {
                all: new DataTags(uiState.tagStatus.all),
                checked: props.datapoint? new DataTags(props.datapoint.summary.tags) : new DataTags(uiState.tagStatus.checked),
                unfolded: props.datapoint? 
                        new DataTags(props.datapoint.summary.tags).allParents():
                        new DataTags(uiState.tagStatus.unfolded)
            };
            newTagInput.value = "";
        }
    })

</script>

<template>
    <FloatingWindow v-model:show="show" :title="datapoint?datapoint.authorAbbr():'new'">
        <div id="inputDiv">
            <div id="inputLeft">
                <div id="bibtexArea">
                    <label for="bibtex">Bibtex</label>
                    <textarea id="bibtex" v-model="bibtex" placeholder="bibtex"></textarea>
                </div>
                <div id="urlArea">
                    <label for="url">URL: </label>
                    <input id="url" v-model="url" placeholder="url" type="text">
                </div>
            </div>
            <div id="inputRight">
                <div id="tagArea">
                    <label for="tagSelector">Tags</label>
                    <div id="tagSelector" class="scrollable">
                        <TagSelector v-model:tag-status="tagStatus"></TagSelector>
                    </div>
                </div>
                <div id="newTagArea">
                    <label for="newTag">Add: </label>
                    <input id="newTag" placeholder="new tag" type="text" v-model="newTagInput">
                    <button id="addNewTag" @click="addNewTag">Add</button>
                </div>
            </div>
        </div>
        <div id="buttons">
            <button @click="save">Save</button>
        </div>
    </FloatingWindow>
</template>

<style scoped>
    #inputDiv {
        display: flex;
        flex-direction: row;
        width: 100%;
        gap: 10px;
    }

    label {
        font-weight: bold;
    }
    textarea, input[type="text"], div#tagSelector {
        border: 1px solid var(--color-border);
        border-radius: 5px;
        background-color: var(--color-background);
        color: var(--color-text);
        width: 100%
    }

    #inputLeft, #inputRight{
        display: flex;
        flex-direction: column;
        width: 100%;
        gap: 10px;
    }
    div#bibtexArea, div#tagArea{
        display: flex;
        flex-direction: column;
        align-items: flex-start;
    }
    div#bibtexArea textarea {
        min-width: 300px;
        width: 100%;
        height: 420px;
        padding: 5px
    }
    div#urlArea, div#newTagArea {
        display: flex;
        flex-direction: row;
        align-items: center;
        gap: 5px
    }
    div#urlArea > input[type="text"]{
        width: 100%
    }

    div#tagSelector {
        width: 100%;
        min-width: 300px;
        height: 420px;
        overflow: scroll;
        padding: 5px;
    }
    button#addNewTag{
        width: 80px;
    }


</style>