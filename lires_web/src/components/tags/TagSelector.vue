<script setup lang="ts">
    import { computed} from 'vue';
    import { TagRule, TAG_SEP } from '../../core/tag';
    import TagCollapsibleToggle from './TagCollapsibleToggle.vue';
    import { TagStatus } from '../interface';

    const props = defineProps<{
        tagStatus: TagStatus
    }>()

    const emit = defineEmits<{
        (e: "update:tagStatus", status: TagStatus): void
    }>()
    
    const hierarchy = computed(() => TagRule.tagHierarchy(props.tagStatus.all));
    const sortedHierarchyKeys = computed(() => Object.keys(hierarchy.value).sort());

    const mutableTagStatus = computed({
        get: () => props.tagStatus,
        set: (newStatus: TagStatus) => emit("update:tagStatus", newStatus)
    })

</script>

<template>
    <div id="tagSelector-main" class="hover-scrollable">
        <TagCollapsibleToggle v-for="k of sortedHierarchyKeys"
            :identifier="String(k)" 
            :children="hierarchy[k]" 
            v-model:tagStatus="mutableTagStatus">
            {{ String(k).split(TAG_SEP).slice(-1)[0] }}
        </TagCollapsibleToggle>
    </div>
</template>

<style scoped>
    #tagSelector-main {
        flex-grow: 1;
    }
</style>