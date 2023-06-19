
<script setup lang="ts">
    import Popup from './components/common/Popup.vue';
    import { useUIStateStore } from './components/store';
    const uiState = useUIStateStore();
</script>

<template>
    <div id="popups">
        <Popup v-for="key, index in Object.keys(uiState.popupValues)" :key="index" :styleType="uiState.popupValues[key].styleType"
        :style="{
            transform: `translate(-50%, ${-50 + 110 * index}%) scale(0.9)`,
        }">
            {{ uiState.popupValues[key].content }}
        </Popup>
    </div>
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