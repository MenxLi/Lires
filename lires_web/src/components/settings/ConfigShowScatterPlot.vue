

<script setup lang="ts">
    import SettingsContainer from "./SettingsContainer.vue";
    import SwitchToggle from "./SwitchToggle.vue";
    import { useSettingsStore } from "../store";
    import { computed } from "vue";

    const settings = useSettingsStore();
    const toggle = computed({
        get: ()=>settings.show3DScatterPlot,
        set: (v)=>settings.setShow3DScatterPlot(v)
    })

</script>

<template>
    <SettingsContainer title="Scatter Plot" description="Show scatter plot on the home page">
        <SwitchToggle v-model:checked="toggle"/>
    </SettingsContainer>
</template>