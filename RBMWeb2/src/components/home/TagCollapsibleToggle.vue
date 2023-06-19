

<script setup lang="ts">

    import {ref, computed} from "vue";
    import Toggle from "../common/Toggle.vue";
    import TagCollapsibleToggle from "./TagCollapsibleToggle.vue"
    import { TAG_SEP } from '../../core/dataClass';
    import { useUIStateStore } from "../store";
    import type { TagHierarchy } from "../../core/dataClass";

    const uiState = useUIStateStore()

    const props = withDefaults(defineProps<{
        identifier: string,
        children: TagHierarchy,
    }>(), {
        identifier: ""
    })

    // emit from both itself and the following children
    const emit = defineEmits<{
        (e: "onCheck", is_checked: boolean, identifier: string|undefined): void
    }>()

    // if has child change style
    const buttonClass = ref("collapseButton")
    if (Object.keys(props.children).length !== 0) {
        buttonClass.value += " collapsible"
    }

    const button = ref(null);
    const collapsed = computed(() => !uiState.unfoldedTags.has(props.identifier))
    const triangleClass = computed(() => collapsed.value?"triangle-right":"triangle-down rotate90in")
    function onClickButton(_: Event){
        if (uiState.unfoldedTags.has(props.identifier)){
            uiState.unfoldedTags.delete(props.identifier);
        }
        else{
            uiState.unfoldedTags.add(props.identifier);
        }
    }

    // change tag store and emit
    const isChecked = computed(() => uiState.currentlySelectedTags.has(props.identifier))
    function _onCheck(identifier: string|undefined){
        // change global state
        if (identifier === undefined){ return;}
        let is_checked = false;
        if (!uiState.currentlySelectedTags.has(identifier)){
            uiState.currentlySelectedTags.add(identifier);
            is_checked = true;
        }
        else{
            uiState.currentlySelectedTags.delete(identifier)
        }
        // emit
        emit("onCheck", is_checked, identifier);
    }
</script>

<template>
    <div class="row">
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
            @onCheck="(is_checked: boolean, identifier: string | undefined) => emit('onCheck', is_checked, identifier)">
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