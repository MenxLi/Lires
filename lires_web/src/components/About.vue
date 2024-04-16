<script setup lang="ts">
    import { useConnectionStore, useDataStore, useSettingsStore } from './store';
    import { ref, computed } from 'vue';
    import { type Changelog } from '../api/protocol';
    import { getBackendURL, docsURL } from '../config';
    import Toolbar from './header/Toolbar.vue';
    import FloatingWindow from './common/FloatingWindow.vue';
    import { registerServerEvenCallback } from '../api/serverWebsocketConn';
    import UsersWidget from './dashboard/UsersWidget.vue';

    const changelog = ref<Changelog>([]);
    const showChangelog = ref(false);
    const conn = useConnectionStore().conn;
    const updateChangelog = () => {
        conn.changelog().then(
            (data) => {
                changelog.value = data;
            },
            (err) => {
                console.error(err);
            }
        )
    }


    const __uptime = ref(-1);
    const __uptimestr = computed(() => {
        if (__uptime.value === -1) return 'N/A';
        const up_hours = Math.floor(__uptime.value / 3600);
        const up_minutes = Math.floor((__uptime.value - up_hours * 3600) / 60);
        const up_seconds = Math.floor(__uptime.value - up_hours * 3600 - up_minutes * 60);
        return `${up_hours}h ${up_minutes}m ${up_seconds}s`;
    })
    const serverInfo = ref({
        'backend': getBackendURL(),
        'version': '',
        'uptime': __uptimestr,
        '_uptime': -1,
        'numDocs': -1,
        'numConnections': -1,
    })
    const updateServerStatus = () => {
        conn.status().then(
            (data) => {
                __uptime.value = data.uptime;
                serverInfo.value.version = data.version;
                serverInfo.value.numDocs = data.n_data;
                serverInfo.value.numConnections = data.n_connections;
            },
            (err) => {
                console.error(err);
            }
        )
    }

    const reversedChangelog = computed(() => {
        return changelog.value.slice().reverse();
    })

    updateChangelog();
    updateServerStatus();
    window.setInterval(()=>__uptime.value++, 1000);

    registerServerEvenCallback('login', ()=>serverInfo.value.numConnections++);
    registerServerEvenCallback('logout', ()=>serverInfo.value.numConnections--);
</script>

<template>
    <div class="toolbar">
        <Toolbar/>
    </div>
    <div id="about-main" class="slideIn">

        <h1>About</h1>
        <div class="content">
            <p>
                Lires is a self-hosted web application for research literature management. <br>
                It is open source and available at <a href="https://github.com/MenxLi/Lires" target="_blank">GitHub - MenxLi/Lires</a>. <br>
            </p>

        </div>
        <div class="content">
            <h2> Resources </h2>
            <ul>
                <li> <a :href="docsURL" target="_blank">User manual</a> </li>
                <li> <a :href="useSettingsStore().backend()+`/_resources/lires-obsidian-plugin.zip?key=${useSettingsStore().encKey}`">Obsidian Plugin</a> </li>
                <li> <a :href="useSettingsStore().backend()+`/_resources/api.zip?key=${useSettingsStore().encKey}`">Javascript API</a> </li>
                <li> <a :href="useSettingsStore().backend()+`/_resources/api.py?key=${useSettingsStore().encKey}`">Python API</a> </li>
                <li> <a @click="showChangelog = true" style="cursor: pointer;">Change log</a> </li>
            </ul>

        </div>
        <div class="content" v-if="useDataStore().user.is_admin">
            <h2> Management </h2>
            <details>
                <summary>Server status </summary>
                <ul>
                    <li><b>Backend</b>: {{serverInfo.backend}}</li>
                    <li>
                        <b>Version</b>: {{serverInfo.version}}
                    </li>
                    <li><b>Uptime</b>: {{serverInfo.uptime}}</li>
                    <li><b>Connection count</b>: {{serverInfo.numConnections}}</li>
                </ul>
            </details>
            <details>
                <summary>User management</summary>
                <div style="
                border: 1px solid var(--color-border); 
                border-radius: 10px;
                display: flex; justify-content: center; 
                margin-block: 10px; padding: 10px;
                width: 100%;">
                    <UsersWidget/>
                </div>
            </details> 
        </div>

        <FloatingWindow v-model:show="showChangelog" title="Change log">
            <div id="versionHistory" class="content">
                <h1 style="margin-bottom: 0px;"> Version history </h1>
                <div class="block" v-for="i in reversedChangelog.length">
                    <h2>{{reversedChangelog[i-1][0].toString()}}</h2>
                    <ul>
                        <li v-for="change in reversedChangelog[i-1][1]">
                            <div v-if="typeof change === 'string'"> {{change}} </div>
                            <div v-else-if="(typeof change === 'object')">
                                <!-- change is an object with only one key, and the value is an array of strings -->
                                {{ Object.keys(change)[0] }}
                                <ul>
                                    <li v-for="item in change[Object.keys(change)[0] as any]">{{item}}</li>
                                </ul>
                            </div>
                        </li>
                    </ul>
                </div>
            </div>
        </FloatingWindow>

    </div>
</template>

<style scoped> 

    h1{
        font-size: 2rem;
        font-weight: bold;
        margin-top: 1rem;
        padding-block: 0.8rem;
    }
    h2{
        font-weight: bold;
        margin-top: 1rem;
        padding-block: 0.8rem;
        border-top: 1px solid var(--color-border);
    }

    div#about-main{
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        max-width: 900px;
        margin-top: 40px;
    }
    b{
        font-weight: bold;
    }
    div.content{
        padding-inline: 1rem;
        width: 100%;
        text-align: left;
    }
    div#versionHistory{
        padding: 20px;
        display: flex;
        flex-direction: column;
    }
    div#block{
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        align-items: flex-start;
    }
    hr{
        width: 100%;
        margin-top: 10px;
        margin-bottom: 10px;
        border: 1px solid var(--color-border);
        border-top: none;
    }
</style>