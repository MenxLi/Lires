
<script setup lang="ts">
    import SettingsContainer from "./SettingsContainer.vue";
    import SwitchToggle from "./SwitchToggle.vue";
    import { useSettingsStore } from "../store";
    import { computed } from "vue";

    const settings = useSettingsStore();
    const toggle = computed({
        get: ()=>settings.showHomeInfoPanel,
        set: (v)=>settings.setShowHomeInfoPanel(v)
    })

</script>

<template>
    <SettingsContainer title="Info Panel" description="Show info panel at home page">
        <SwitchToggle v-model:checked="toggle"/>
    </SettingsContainer>
</template>
