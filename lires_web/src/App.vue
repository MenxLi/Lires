
<script setup lang="ts">
    import { watch } from 'vue';
    import Popup from './components/common/Popup.vue';
    import { useUIStateStore, useSettingsStore, useDataStore } from './components/store';
    import { useRouter } from 'vue-router';
    import { settingsAuthentication, settingsLogout } from './core/auth';
    import { getSessionConnection, registerServerEvenCallback } from './core/serverWebsocketConn';
    import type { Event_Data, Event_Tag } from './core/protocalT'
import { DataTags } from './core/dataClass';

    const uiState = useUIStateStore();
    const settingStore = useSettingsStore();

    // Authentication on load
    const router = useRouter();
    const logout = settingsLogout;
    function onLogin(){
        // on login
        console.log("Logged in.")
        // initialize session connection if it's not been
        getSessionConnection().init();
        uiState.reloadDatabase();
    }
    function onLogout(){
        console.log("Logged out from: ", router.currentRoute.value.fullPath);
        getSessionConnection().close();
        router.push({
            path: "/login",
            query: {
                from: router.currentRoute.value.fullPath,
            }
        });
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
            if (new_){ onLogin() }
            else{ onLogout(); }
        }
    )

    // register some server event callbacks for global storage
    registerServerEvenCallback('add_entry', (event) => {
        const dataStore = useDataStore();
        const d_summary = (event as Event_Data).datapoint_summary!
        dataStore.database.add(d_summary);
        uiState.updateShownData();
    })
    registerServerEvenCallback('update_entry', (event) => {
        const dataStore = useDataStore();
        const d_summary = (event as Event_Data).datapoint_summary!
        dataStore.database.get(d_summary.uuid)?.update(d_summary)
        uiState.updateShownData();
    })
    registerServerEvenCallback('delete_entry', (event) => {
        const dataStore = useDataStore();
        const uid = (event as Event_Data).uuid!
        dataStore.database.delete(uid)
        uiState.updateShownData();
    })
    const __tagEventCallback = (event: any) =>{
        const oldTag = new DataTags([(event as Event_Tag).src_tag!]);
        const dataStore = useDataStore();
        const needUpdate = dataStore.database.getDataByTags(oldTag);
        Promise.all(needUpdate.map( (d) => d.update())).then(
            () => { uiState.updateShownData(); },
            () => { 
                uiState.showPopup("Tag rename succeded at server side, but faild to fetch update, please reload the page", 'error') 
            },
        )
    }
    registerServerEvenCallback('update_tag', __tagEventCallback)
    registerServerEvenCallback('delete_tag', __tagEventCallback)


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