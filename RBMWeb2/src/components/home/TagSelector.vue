<script setup lang="ts">
    import { computed} from 'vue';
    import { TagRule, TAG_SEP, type TagHierarchy } from '../../core/dataClass';
    import TagCollapsibleToggle from './TagCollapsibleToggle.vue';
    import { assert } from '@vue/compiler-core';
    import { useUIStateStore, useDataStore } from '../store';

    import type { TagCheckStatus } from "../interface"

    const emit = defineEmits<{
        (e: "onCheck", status: TagCheckStatus) : void
    }>()

    const dataStore = useDataStore()
    const allTags = computed(() => dataStore.database.getAllTags());
    const hierarchy = computed(() => TagRule.tagHierarchy(allTags.value!));
    function sortedHierarchyKeys(hierarchy: TagHierarchy){
        return Object.keys(hierarchy).sort();
    }

    function _onCheck(is_checked: boolean, identifier: string|undefined) {
        assert(typeof(allTags.value) != "undefined");
        emit("onCheck", {
            identifier: identifier as string,
            isChecked: is_checked,
            currentlySelected: Array.from(useUIStateStore().currentlySelectedTags)
        });
    }

</script>

<template>
    <div id="tagSelector" class="scrollable">
        <TagCollapsibleToggle v-for="k of sortedHierarchyKeys(hierarchy)"
            :identifier="String(k)" 
            :children="hierarchy[k]" 
            @onCheck="_onCheck">
            {{ String(k).split(TAG_SEP).slice(-1)[0] }}
        </TagCollapsibleToggle>
    </div>
</template>

<style scoped>
    #tagSelector {
        flex-grow: 1;
    }
</style>