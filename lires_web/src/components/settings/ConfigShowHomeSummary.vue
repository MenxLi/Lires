
<script setup lang="ts">
    import SettingsContainer from "./SettingsContainer.vue";
    import SwitchToggle from "./SwitchToggle.vue";
    import { useSettingsStore } from "../store";
    import { computed } from "vue";

    const settings = useSettingsStore();
    const toggle = computed({
        get: ()=>settings.showHomeSummaryPanel,
        set: (v)=>settings.setShowHomeSummaryPanel(v)
    })

</script>

<template>
    <SettingsContainer title="Summary Panel Display" description="Show summary panel on the home page">
        <SwitchToggle v-model:checked="toggle"/>
    </SettingsContainer>
</template>
