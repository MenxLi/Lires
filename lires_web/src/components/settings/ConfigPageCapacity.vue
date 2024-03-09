
<script setup lang="ts">
    import SettingsContainer from "./SettingsContainer.vue";
    import { computed } from "vue";
    import { useSettingsStore } from "../store";

    const numItemsPerPage = computed({
        get: ()=>useSettingsStore().numItemsPerPage,
        set: (v)=>useSettingsStore().setNumItemsPerPage(v)
    })

    const numChoices = [10, 20, 50, 100, 200, 500];


</script>

<template>
    <SettingsContainer title="Page Capacity" description="Smaller number can improve performance">
        <select v-model="numItemsPerPage" :style="{
            width: '80px',
            textAlign: 'center',
            padding: '0.2rem',
            justifySelf: 'flex-end'
        }">
            <option v-for="choice in numChoices" :value="choice" :key="choice">{{choice}}</option>
        </select>
    </SettingsContainer>
</template>
