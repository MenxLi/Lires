
<script setup lang="ts">
    import { watch } from 'vue';
    import Popup from './components/common/Popup.vue';
    import { useUIStateStore, useSettingsStore } from './components/store';
    import { useRouter } from 'vue-router';
    import { settingsAuthentication, settingsLogout } from './core/auth';

    const uiState = useUIStateStore();
    const settingStore = useSettingsStore();

    // Authentication on load
    const router = useRouter();
    const logout = settingsLogout;
    function onLogout(){
        console.log("Logged out from: ", router.currentRoute.value.fullPath);
        router.push({
            path: "/login",
            query: {
                from: router.currentRoute.value.fullPath,
            }
        })
    }
    // if not on login page, try to authenticate with saved token
    if (window.location.hash.split('?')[0] !== "#/login"){
        console.log("Authenticating...");
        // Trigger logout event manually if authentication failed on page load.
        // Since the default value of the flag is false, 
        // the watcher will not be triggered when loggedIn flag is set to the same value
        const __logoutAndRedirect = ()=>{
            logout();
            onLogout();
        }
        settingsAuthentication().then(
            (userInfo)=>{if (!userInfo){ __logoutAndRedirect() }},
            ()=>{ __logoutAndRedirect() },
        )
    }
    // React to login status change
    watch(
        () => settingStore.loggedIn,
        (new_: boolean, _: boolean) => {
            if (new_){
                // on login
                console.log("Logged in.")
                uiState.reloadDatabase(false);
            }
            else{
                // on logout
                onLogout();
            }
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