

<script setup lang="ts">
    import {ref} from "vue"

    const emit = defineEmits<{
        (e: "onCheck", is_checked: boolean, identifier: string|undefined): void
    }>()
    const props = withDefaults(defineProps<{
        checked?: boolean,
        identifier?: string,
    }>(), {
        checked: false,
        identifier: "",
    })
    const is_checked = ref(props.checked);

    function _onCheck(event: Event){
        is_checked.value = !is_checked.value;
        emit("onCheck", is_checked.value?true:false, props.identifier);
    }
</script>

<template>
    <div class="toggle">
        <label for="chk" @click="_onCheck">
            <slot></slot>
        </label>
        <div class="checkCircle" @click="_onCheck">
            <div v-if="is_checked" class="checkStatus"></div>
        </div>
    </div>
</template>

<style scoped>
    div{
        --radius: 16px;
        --radius-inner: 8px;
        display: flex;
        align-items: center;
        gap: 5px;
    }
    div.toggle{
        justify-content: left;
        flex-direction: row-reverse;
        flex-wrap: wrap;
    }
    div.checkCircle {
        border: 3px solid var(--color-border);
        height: var(--radius);
        width: var(--radius);
        border-radius: 50%;
        /* margin-right: 5px; */
    }
    div.checkStatus{
        height: var(--radius-inner);
        width: var(--radius-inner);
        border-radius: 50%;
        background-color: var(--theme-color);
    }
    div.checkCircle:hover {
        background-color: var(--theme-hover-hight-color);
    }
    label:hover + div.checkCircle {
        background-color: var(--theme-hover-hight-color);
    }
</style>