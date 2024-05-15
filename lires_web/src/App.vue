
<script setup lang="ts">
    import { watch, ref, computed, onMounted } from 'vue';
    import Popup from './components/common/Popup.vue';
    import { useConnectionStore, useUIStateStore, useSettingsStore, useDataStore } from './components/store';
    import { useRouter } from 'vue-router';
    import { settingsAuthentication } from './core/auth';
    import { registerServerEvenCallback } from './api/serverWebsocketConn';
    import LoadingPopout from './components/common/LoadingPopout.vue';
    import type { Event_Data, Event_Tag, Event_User } from './api/protocol'
    import { DataTags } from './core/tag';
    import { ThemeMode } from "./core/misc";

    const router = useRouter();
    const uiState = useUIStateStore();
    const settingStore = useSettingsStore();

    router.isReady().then(()=>{
        /** deal with url params **/
        // check if backend port and backend host is set via url query
        if (router.currentRoute.value.query.backendPort){
            useSettingsStore().setBackendPort(router.currentRoute.value.query.backendPort as string);
        }
        if (router.currentRoute.value.query.backendHost){
            useSettingsStore().setBackendHost(router.currentRoute.value.query.backendHost as string);
        }
        // check if credentials are set via url query
        if (router.currentRoute.value.query.credential){
            useSettingsStore().setEncKey(router.currentRoute.value.query.credential as string, false);
        }

        /** authentication **/
        // if not on login page, try to authenticate with saved token
        if (window.location.hash.split('?')[0] !== "#/login"){
            console.log("Authenticating...");
            // Trigger logout event manually if authentication failed on page load.
            // Since the default value of the flag is false, 
            // the watcher will not be triggered when loggedIn flag is set to the same value
            const __logoutAndRedirect = ()=>{
                if (settingStore.loggedIn){
                    // redirect will be triggered by the watcher
                    settingStore.loggedIn = false;
                }
                else{
                    resetAndRedirectToLoginPage();
                }
            }
            settingsAuthentication().then(
                (userInfo)=>{if (!userInfo){ __logoutAndRedirect() }},
                ()=>{ __logoutAndRedirect() },
            )
        }
    })
    function resetAndRedirectToLoginPage(){
        useDataStore().$reset();
        useUIStateStore().$reset();
        wsConnection.close();
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
            else{ resetAndRedirectToLoginPage(); }
        }
    )

    const wsConnection = useConnectionStore().wsConn;
    // session connection status hint
    const __sessionConnected = ref(false)
    const __sessionFailed = ref(false)
    const __isInLoginPage = ref(window.location.hash.split('?')[0] === "#/login")
    router.afterEach((to, _) => {
        __isInLoginPage.value = to.path === "/login"
    })
    const showConnectionHint = computed(()=>!__sessionConnected.value && !__isInLoginPage.value && !__sessionFailed.value)
    const showConnectionFailedHint = computed(()=>__sessionFailed.value && !__isInLoginPage.value)

    function initConnection(){
        wsConnection.connect({
            onopenCallback: () => {
                __sessionConnected.value = true
                __sessionFailed.value = false
            },
            oncloseCallback: () => __sessionConnected.value = false,
            onfailedToConnectCallback: () => __sessionFailed.value = true,
        });
    }

    // the callbacks sometime not triggered, so we need to check the connection status periodically
    setInterval(()=>{
        if (!wsConnection.isOpen() && __sessionConnected.value 
            && !__isInLoginPage.value && !__sessionFailed.value){
            console.log("DEBUG: Connection lost, try to reconnect");
            __sessionConnected.value = false
            initConnection();
        }
        else if (__isInLoginPage.value && wsConnection.willTryReconnect()){
            console.log("DEBUG: In login page, close connection.");
            wsConnection.close();
        }
    }, 5000)

    // Authentication on load
    function onLogin(){
        // initialize session connection if it's not been
        initConnection();
        uiState.reloadDatabase();
    }

    // register some server event callbacks for global storage
    registerServerEvenCallback('add_entry', (event) => {
        const dataStore = useDataStore();
        const d_summary = (event as Event_Data).datapoint_summary!
        dataStore.database.update(d_summary).then(()=>{
            console.log("DEBUG: add entry update UI");
            uiState.updateShownData();
        });
    })
    registerServerEvenCallback(['update_entry', 'update_note'], (event) => {
        const dataStore = useDataStore();
        const d_summary = (event as Event_Data).datapoint_summary!
        dataStore.database.update(d_summary).then(()=>{
            console.log("DEBUG: update entry update UI");
            uiState.updateShownData();
        });
    })
    registerServerEvenCallback('delete_entry', (event) => {
        const dataStore = useDataStore();
        const uid = (event as Event_Data).uuid!
        dataStore.database.delete(uid).then(()=>{
            console.log("DEBUG: delete entry update UI")
            uiState.updateShownData();
        })
    })
    registerServerEvenCallback(['delete_tag', 'update_tag'], (event: any) =>{
        const oldTag = new DataTags([(event as Event_Tag).src_tag!]);
        const dataStore = useDataStore();
        (async function onTagChange() {
            // update database cache tag
            await dataStore.database.updateTagCache();
            // update shown data
            const needUpdate = dataStore.database.getCacheByTags(oldTag);
            await Promise.all(needUpdate.map( (d) => d.update()));
            uiState.updateShownData(); console.log("DEBUG: update tag update UI")
        })();
    })
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

    const __reloadPage = ()=>{ window.location.reload(); }

    onMounted(()=>{
        // set theme
        ThemeMode.setDefaultDarkMode();
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
    <Popup v-if="showConnectionFailedHint" styleType="info" position="center">
        <div style="display: flex; flex-direction: column; align-items: center; margin: 10px">
            <div>
                <div style="font-size: 2em; font-weight: bold; color: var(--color-red)">Failed to connect to server</div>
                <div style="color: gray">Maximum retry exceeded</div>
            </div>
            <div style="font-size: 1.2em; margin-top: 10px;">
                Please check if the server is running, 
                make sure your network is working properly, 
                and try to <a style="text-decoration:underline; cursor: pointer;" @click="__reloadPage">reload the page</a>.
            </div>
        </div>
    </Popup>
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
</style>./api/serverWebsocketConn./api/protocol