

<script setup lang="ts">

    import {ref, computed, onMounted, onUnmounted} from "vue";
    import Toggle from "../common/Toggle.vue";
    import TagCollapsibleToggle from "./TagCollapsibleToggle.vue"
    import { TAG_SEP } from '../../core/dataClass';
    import type { TagHierarchy } from "../../core/dataClass";
    import type { TagStatus } from "../interface";

    const props = withDefaults(defineProps<{
        tagStatus: TagStatus,
        identifier: string,
        children: TagHierarchy,
    }>(), {
        identifier: ""
    })

    // emit from both itself and the following children
    const emit = defineEmits<{
        (e: "update:tagStatus", status: TagStatus): void
    }>()

    const mutableTagStatus = computed({
        get: () => props.tagStatus,
        set: (newStatus: TagStatus) => emit("update:tagStatus", newStatus)
    })

    const buttonClass = computed(() => {
        let buttonClass = "collapseButton"
        if (Object.keys(props.children).length !== 0) {
            buttonClass += " collapsible"
        }
        return buttonClass
    })

    const button = ref(null);
    const collapsed = computed(() => !props.tagStatus.unfolded.has(props.identifier))
    const triangleClass = computed(() => collapsed.value?"triangle-right":"triangle-down rotate90in")
    function onClickButton(_: Event){
        let unfoldedTags = mutableTagStatus.value.unfolded;
        if (unfoldedTags.has(props.identifier)){
            unfoldedTags.delete(props.identifier);
        }
        else{
            unfoldedTags.add(props.identifier);
        }
    }

    // change tag store and emit
    const isChecked = computed(() => props.tagStatus.checked.has(props.identifier))
    function _onCheck(identifier: string|undefined){
        // change global state
        if (identifier === undefined){ return;}
        let currentlySelectedTags = mutableTagStatus.value.checked;
        if (!currentlySelectedTags.has(identifier)){
            currentlySelectedTags.add(identifier);
        }
        else{
            currentlySelectedTags.delete(identifier)
        }
    }

    // right click to unfold
    const rowDiv = ref(null as null | HTMLDivElement);
    const onRightClick = (e: MouseEvent) => {
        if (e.button === 2){
            onClickButton(e);
            e.preventDefault()
        }
    }
    onMounted(() => {
        rowDiv.value?.addEventListener("contextmenu", onRightClick)
    })
    onUnmounted(() => {
        rowDiv.value?.removeEventListener("contextmenu", onRightClick)
    })

</script>

<template>
    <div class="row" ref="rowDiv">
        <div id="button" :class="buttonClass" ref="button" @click="onClickButton">
            <div v-if="Object.keys(props.children).length !== 0" :class="triangleClass"></div>
        </div>
        <div class="toggleText">
            <Toggle 
                :checked="isChecked" 
                :identifier="props.identifier"
                @onCheck="_onCheck">
                <slot></slot>
            </Toggle>
        </div>
    </div>
    <div v-show="!collapsed" class="children gradInDown">
        <TagCollapsibleToggle v-for="(v, k) in children" 
            :identifier="String(k)" 
            :children="v" 
            v-model:tag-status="mutableTagStatus">
            {{ String(k).split(TAG_SEP).slice(-1)[0] }}
        </TagCollapsibleToggle>
    </div>
</template>

<style scoped>
    div{
        --button-dim: 16px;
        --triangle-dim: 8px;
    }
    div.row{
        display: flex;
        align-items: center;
        gap: 2px;
    }
    div.collapseButton{
        width: var(--button-dim);
        height: var(--button-dim);
        min-width: var(--button-dim);
        min-height: var(--button-dim);
        /* border: 1px solid var(--color-border); */
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .toggleText{
        flex-grow: 1;
        margin-top: 2px;
        margin-bottom: 2px;
        border-radius: 5px;
        transition: all 0.1s ease;
    }
    .toggleText:hover{
        background-color: var(--color-background-theme-highlight);
    }
    .triangle-right {
		width: var(--triangle-dim);
        height: var(--triangle-dim);
        background-color: var(--color-theme);
		clip-path: polygon(0 0, 0% 100%, 100% 50%);
    }
    .triangle-down {
		width: var(--triangle-dim);
        height: var(--triangle-dim);
        background-color: var(--color-theme);
		clip-path: polygon(0 0, 100% 0%, 50% 100%);
    }
    div.children{
        margin-left: 20px;
    }
</style>