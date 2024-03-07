
<script setup lang="ts">
    import SettingsContainer from "./SettingsContainer.vue";
    import SwitchToggle from "./SwitchToggle.vue";
    import { useSettingsStore } from "../store";

    const settings = useSettingsStore();

</script>

<template>
    <SettingsContainer title="Tag Display" description="Show tag panel on the home page">
        <SwitchToggle :checked="settings.showTagPanel" @on-change="(checked: boolean)=>{
            settings.setShowTagPanel(checked);
        }"/>
    </SettingsContainer>
</template>
