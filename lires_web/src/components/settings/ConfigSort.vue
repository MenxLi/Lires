
<script setup lang="ts">
    import { useSettingsStore, useUIStateStore } from "@/state/store";
    import { computed } from "vue";
    import SettingsContainer from "./SettingsContainer.vue";

    const settings = useSettingsStore();
    const uiState = useUIStateStore();
    const val = computed(
        {
            get: () => settings.sortBy,
            set: (value) => settings.setSortBy(value)
        }
    );

</script>

<template>
    <SettingsContainer title="Order by" description="Change the order of the items">
        <select v-model="val" @change="uiState.updateShownData" :style="{
            width: '100px',
            textAlign: 'center',
            padding: '0.2rem',
            justifySelf: 'flex-end'
        }">
            <option value="title">Title</option>
            <option value="time_import">Time added</option>
            <option value="last_read">Last read</option>
        </select>
    </SettingsContainer>
</template>
