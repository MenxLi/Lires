

<script setup lang="ts">

    const emit = defineEmits<{
        (e: "onCheck", identifier: string|undefined): void
    }>()
    const props = withDefaults(defineProps<{
        checked: boolean,
        identifier?: string,
    }>(), {
        identifier: "",
    })

    function _onCheck(_: Event){
        emit("onCheck", props.identifier);
    }
</script>

<template>
    <div class="toggle">
        <label for="chk" @click="_onCheck">
            <slot></slot>
        </label>
        <div id="checkCircle" @click="_onCheck">
            <div v-if="checked" id="checkStatus"></div>
        </div>
    </div>
</template>

<style scoped>
    div{
        --radius: 16px;
        --radius-inner: 6px;
        display: flex;
        align-items: center;
        gap: 5px;
    }
    div.toggle{
        justify-content: left;
        flex-direction: row-reverse;
        flex-wrap: nowrap;
    }
    #checkCircle {
        border: 3px solid var(--color-border);
        height: var(--radius);
        width: var(--radius);
        border-radius: 50%;
        justify-content: center;
    }
    #checkStatus{
        height: var(--radius-inner);
        width: var(--radius-inner);
        border-radius: 50%;
        background-color: var(--color-theme);
    }
    #checkCircle:hover {
        background-color: var(--color-background-theme-highlight);
        transition: all 0.2s;
    }
    label:hover + #checkCircle {
        background-color: var(--color-background-theme-highlight);
        transition: all 0.2s;
    }
    label{
        text-align: left;
        text-overflow: ellipsis;
        overflow: clip;
        /* white-space: nowrap; */
    }
</style>