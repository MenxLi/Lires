
<script setup lang="ts">
    import TagSelector from './TagSelector.vue';
    import type { TagStatus } from '../interface';
    import { TagRule } from '../../core/tag';
    import { watch, computed, ref } from 'vue';

    const props = withDefaults(defineProps<{
        tagStatus: TagStatus
        tagInputValue?: string
    }>(), {
        tagInputValue: "",
    })

    const emit = defineEmits<{
        (e: "update:tagStatus", status: TagStatus): void
        (e: "update:tagInputValue", value: string): void
    }>()

    const mutableTagStatus = computed({
        get: () => props.tagStatus,
        set: (newStatus: TagStatus) => emit("update:tagStatus", newStatus)
    })

    const __internal_tagInputValue = ref(props.tagInputValue)
    watch(() => props.tagInputValue, (newValue) => {
        __internal_tagInputValue.value = newValue
    })
    const mutableTagInput = computed({
        get: () => __internal_tagInputValue.value,
        set: (newValue: string) => {
            emit("update:tagInputValue", newValue);
            __internal_tagInputValue.value = newValue
        },
    })

    const addNewTag = () => {
        const tag = mutableTagInput.value.trim();
        if (tag === ""){ return; }
        mutableTagStatus.value.all.add(tag);
        mutableTagStatus.value.checked.add(tag);
        mutableTagStatus.value.unfolded.union_(TagRule.allParentsOf(tag));
        mutableTagInput.value = "";
    }

</script>

<template>
    <div id="tag-selector-with-entry-main">
        <div :style="{textAlign: 'left'}">
            <label for="tagSelector">Tags</label>
            <div id="tagSelector" class="scrollable">
                <TagSelector v-model:tagStatus="mutableTagStatus"></TagSelector>
            </div>
        </div>
        <div class="entry">
            <input type="text" placeholder="New tag" v-model="mutableTagInput" @keyup.enter="addNewTag">
            <button :class="`green${mutableTagInput?' to-be-confirmed':''}`" @click="addNewTag">ADD</button>
        </div>
    </div>
</template>

<style scoped>
    div#tag-selector-with-entry-main{
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        justify-content: center;
        width: 100%;
        height: 100%;
        gap: 10px;
    }

    textarea, input[type="text"], div#tagSelector {
        border: 1px solid var(--color-border);
        border-radius: 5px;
        background-color: var(--color-background);
        color: var(--color-text);
        width: 100%;
    }

    div#tagSelector{
        min-width: 300px;
        height: 420px;
        padding: 5px;
    }

    label {
        font-weight: bold;
    }

    input[type="text"] {
        border: 1px solid var(--color-border);
        border-radius: 5px;
    }

    div.entry {
        display: flex;
        flex-direction: row;
        align-items: center;
        width: 100%;
        gap: 5px
    }

    button {
        width: 80px;
        cursor: pointer;
    }
    button.to-be-confirmed{
        color: rgb(255, 0, 150);
        background-color: rgba(0, 255, 166, 0.75);
    }

</style>