<script setup lang="ts">
    import { computed, ref } from 'vue';
    import { DataBase } from '@/core/dataClass';
    import Toggle from './common/Toggle.vue'

    const prop = defineProps({
        database: DataBase
    })
    const emit = defineEmits<{
        (e: "onCheck", tag: string, checked: boolean) : void
    }>()

    const allTags = computed(() => prop.database?.getAllTags());

    function _onCheck(is_checked: boolean, identifier: string|undefined) {
        emit("onCheck", identifier!, is_checked);
    }

</script>

<template>
    <div id="tagSelector" class = "panel">
        <Toggle v-for="tag of allTags" :identifier="tag" @onCheck="_onCheck">{{ tag }}</Toggle>
    </div>
</template>

<style scoped>
    div#tagSelector{
        border: 3px solid var(--color-border);
        border-radius: 10px;
        padding: 20px;
    }
</style>