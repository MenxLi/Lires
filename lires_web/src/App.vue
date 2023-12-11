
<script setup lang="ts">
    import { watch, ref, computed } from 'vue';
    import Popup from './components/common/Popup.vue';
    import { useUIStateStore, useSettingsStore, useDataStore } from './components/store';
    import { useRouter } from 'vue-router';
    import { settingsAuthentication, settingsLogout } from './core/auth';
    import { getSessionConnection, registerServerEvenCallback } from './core/serverWebsocketConn';
    import LoadingPopout from './components/common/LoadingPopout.vue';
    import type { Event_Data, Event_Tag, Event_User } from './core/protocalT'
    import { DataTags } from './core/dataClass';

    const router = useRouter();
    const uiState = useUIStateStore();
    const settingStore = useSettingsStore();

    router.isReady().then(()=>{
        // check if backend port and backend host is set via url query
        if (router.currentRoute.value.query.backendPort){
            useSettingsStore().setBackendPort(router.currentRoute.value.query.backendPort as string);
        }
        if (router.currentRoute.value.query.backendHost){
            useSettingsStore().setBackendHost(router.currentRoute.value.query.backendHost as string);
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
    })

    // session connection status hint
    const __sessionConnected = ref(false)
    const __isInLoginPage = ref(window.location.hash.split('?')[0] === "#/login")
    router.afterEach((to, _) => {
        __isInLoginPage.value = to.path === "/login"
    })
    const showConnectionHint = computed(()=>!__sessionConnected.value && !__isInLoginPage.value)

    // Authentication on load
    const logout = settingsLogout;
    function onLogin(){
        // on login
        console.log("Logged in.")
        // initialize session connection if it's not been
        getSessionConnection().init({
            onopenCallback: () => __sessionConnected.value = true,
            oncloseCallback: () => __sessionConnected.value = false,
        });
        uiState.reloadDatabase();
    }
    function onLogout(){
        console.log("Logged out from: ", router.currentRoute.value.fullPath);
        if (getSessionConnection().isOpen()){
            getSessionConnection().close();
        }
        router.push({
            path: "/login",
            query: {
                from: router.currentRoute.value.fullPath,
            }
        });
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
    registerServerEvenCallback('update_user', (event)=>{
        if ((event as Event_User).username === useDataStore().user.username){
            // update user info except enc_key
            if ((event as Event_User).user_info === null){
                throw new Error("assertion failed: User info is null"); // should be impossible
            }
            for (const key of Object.keys(useDataStore().user)){
                if (key !== 'enc_key'){
                    // @ts-ignore
                    useDataStore().user[key] = (event as Event_User).user_info![key]
                }
            }
        }
    })


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
    <LoadingPopout text="connecting..." v-if="showConnectionHint"></LoadingPopout>
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