
<script setup lang="ts">
    import SettingsContainer from "./SettingsContainer.vue";
    import SwitchToggle from "./SwitchToggle.vue";
    import { useSettingsStore } from "../store";
    import { computed } from "vue";

    const settings = useSettingsStore();
    const toggle = computed({
        get: ()=>settings.showTagPanel,
        set: (v)=>settings.setShowTagPanel(v)
    })

</script>

<template>
    <SettingsContainer title="Tag Display" description="Show tag panel on the home page">
        <SwitchToggle v-model:checked="toggle"/>
    </SettingsContainer>
</template>
