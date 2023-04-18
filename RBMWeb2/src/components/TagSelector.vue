<script setup lang="ts">
    import { computed, ref } from 'vue';
    import { DataBase, TagRule, TAG_SEP } from '@/core/dataClass';
    import CollapsibleToggle from './common/CollapsibleToggle.vue';
    import { assert } from '@vue/compiler-core';

    import type { TagCheckStatus } from "./_interface"

    const prop = defineProps({
        database: DataBase
    })
    const emit = defineEmits<{
        (e: "onCheck", status: TagCheckStatus) : void
    }>()

    let selected: string[] = [];

    const allTags = computed(() => prop.database?.getAllTags());
    const hierarchy = computed(() => TagRule.tagHierarchy(Array.from(allTags.value!)));

    function _onCheck(is_checked: boolean, identifier: string|undefined) {
        assert(typeof(allTags.value) != "undefined");
        console.log(identifier);
        if (is_checked && allTags.value?.has(identifier!)) {
            selected.push(identifier!);
        }
        if (!is_checked) {
            selected = selected.filter((v) => v!=identifier)
        }
        emit("onCheck", {
            identifier: identifier as string,
            isChecked: is_checked,
            currentlySelected: selected
        });
    }
    console.log(hierarchy.value);

</script>

<template>
    <div id="tagSelector">
        <CollapsibleToggle v-for="(v, k) in hierarchy" 
            :identifier="String(k)" 
            :children="v" 
            @onCheck="_onCheck">
            {{ String(k).split(TAG_SEP).slice(-1)[0] }}
        </CollapsibleToggle>
    </div>
</template>

<style scoped>
</style>