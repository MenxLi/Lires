<script setup lang="ts">
    import { ServerConn } from '../core/serverConn';
    import { ref, computed } from 'vue';
    import { type Changelog } from '../core/protocalT';
    import { getBackendURL } from '../config';
    import Banner from './common/Banner.vue';
    import FloatingWindow from './common/FloatingWindow.vue';
    import { registerServerEvenCallback } from '../core/serverWebsocketConn';

    const changelog = ref<Changelog>([]);
    const showChangelog = ref(false);
    const updateChangelog = () => {
        new ServerConn().changelog().then(
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
        new ServerConn().status().then(
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
    <div class="banner">
        <Banner/>
    </div>
    <div id="about-main" class="slideIn">

        <h1>About</h1>
        <div id="about-div" class="content">
            <p>
                Lires is a self-hosted web application for research literature management.
                <br>
                It is open source and available at <a href="https://github.com/MenxLi/Lires" target="_blank">GitHub - MenxLi/Lires</a>.
            </p>
            <p>
                <b>Server status: </b>
                <ul>
                    <li><b>Backend</b>: {{serverInfo.backend}}</li>
                    <li>
                        <b>Version</b>: {{serverInfo.version}}
                    </li>
                    <li><b>Uptime</b>: {{serverInfo.uptime}}</li>
                    <li><b>Number of documents</b>: {{serverInfo.numDocs}}</li>
                    <li><b>Number of connections</b>: {{serverInfo.numConnections}}</li>

                </ul>
            </p>
            <a @click="showChangelog = true" style="cursor: pointer;">View change log</a>
        </div>

        <FloatingWindow v-model:show="showChangelog" title="Change log">
            <div id="versionHistory" class="content">
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
    div#about-div{
        padding: 10px;
        padding-left: 15px;
        padding-right: 15px;
        border-radius: 10px;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    div.content{
        width: 100%;
        text-align: left;
    }
    div#versionHistory{
        padding: 20px;
        display: flex;
        flex-direction: column;
        gap: 20px
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