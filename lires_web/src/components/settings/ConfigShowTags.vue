
<script setup lang="ts">
    import SettingsContainer from "./SettingsContainer.vue";
    import SwitchToggle from "./SwitchToggle.vue";
    import { useSettingsStore } from "@/state/store";
    import { computed } from "vue";

    const settings = useSettingsStore();
    const toggle = computed({
        get: ()=>settings.showTagPanel,
        set: (v)=>settings.setShowTagPanel(v)
    })

</script>

<template>
    <SettingsContainer title="Tag Panel" description="Show tag panel at home page">
        <SwitchToggle v-model:checked="toggle"/>
    </SettingsContainer>
</template>
