
<script setup lang="ts">
    import Popup from './components/common/Popup.vue';
    import { useUIStateStore } from './components/store';
    const uiState = useUIStateStore();
</script>

<template>
    <Popup v-model:show="uiState.popupValue.show" :style="(uiState.popupValue.style as any)">
        {{ uiState.popupValue.content }}
    </Popup>
    <div id="app">
        <router-view />
    </div>
</template>

<style scoped>
#app{
    margin: 0px;
    padding: 0px;
}
</style>