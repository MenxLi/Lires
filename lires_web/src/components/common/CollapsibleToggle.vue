
<!-- DEPRECATED, use TagCollapsibleToggle -->

<script setup lang="ts">

    import {ref, computed} from "vue";
    import Toggle from "./Toggle.vue";
    import CollapsibleToggle from "./CollapsibleToggle.vue"
    import { TAG_SEP, type TagHierarchy } from '../../core/tag';

    const props = withDefaults(defineProps<{
        identifier: string,
        children: TagHierarchy,
        checked?: boolean,
    }>(), {
        checked: false,
    })

    // emit from both itself and the following children
    const emit = defineEmits<{
        (e: "onCheck", identifier: string|undefined): void
    }>()

    const buttonClass = ref("collapseButton")
    if (Object.keys(props.children).length !== 0) {
        buttonClass.value += " collapsible"
    }

    const toggled = ref(false);
    const button = ref(null);
    const triangleClass = computed(() => toggled.value?"triangle-down rotate90in":"triangle-right")
    function onClickButton(_: Event){
        toggled.value = !toggled.value;
    }

</script>

<template>
    <div class="row">
        <div id="button" :class="buttonClass" ref="button" @click="onClickButton">
            <div v-if="Object.keys(props.children).length !== 0" :class="triangleClass"></div>
        </div>
        <Toggle 
            :checked="props.checked" 
            :identifier="props.identifier"
            @onCheck="(identifier: string|undefined) => emit('onCheck', identifier)">
            <slot></slot>
        </Toggle>
    </div>
    <div v-show="toggled" class="children slideInDown">
        <CollapsibleToggle v-for="(v, k) in children" 
            :identifier="String(k)" 
            :children="v" 
            @onCheck="(identifier: string|undefined) => emit('onCheck', identifier)">
            {{ String(k).split(TAG_SEP).slice(-1)[0] }}
        </CollapsibleToggle>
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
    /* .triangle-right {
        border-left: calc(var(--button-dim)/2) solid var(--color-theme);
        border-right: calc(var(--button-dim)/2) solid transparent;
        border-bottom: calc(var(--button-dim)/2) solid transparent;
        border-top: calc(var(--button-dim)/2) solid transparent;
    } */
    /* .triangle-down {
        border-top: calc(var(--button-dim)/2) solid var(--color-theme);
        border-right: calc(var(--button-dim)/2) solid transparent;
        border-bottom: calc(var(--button-dim)/2) solid transparent;
        border-left: calc(var(--button-dim)/2) solid transparent;
    } */
    div.children{
        margin-left: 20px;
    }
</style>