
<script setup lang="ts">
    import { watch } from 'vue';
    import Popup from './components/common/Popup.vue';
    import { useUIStateStore, useSettingsStore } from './components/store';
    const uiState = useUIStateStore();
    const settingStore = useSettingsStore();
    watch(
        () => settingStore.loggedIn,
        (new_: boolean, old_: boolean) => {
            if (new_){ uiState.reloadDatabase(false); }
            if (!new_ && new_ !== old_){ console.log("Logged out.") }
            if (new_ && new_ !== old_){ console.log("Logged in.") }
        }
    )
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
        <!-- https://stackoverflow.com/a/65619387/6775765 -->
        <router-view v-slot="{Component}">
            <KeepAlive exclude="Reader">
                <component :is="Component"></component>
            </KeepAlive>
        </router-view>
    </div>
</template>

<style scoped>
#app{
    margin: 0px;
    padding: 0px;
}
</style>