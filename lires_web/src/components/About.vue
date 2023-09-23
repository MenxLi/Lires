<script setup lang="ts">
    import { ServerConn } from '../core/serverConn';
    import { ref, computed } from 'vue';
    import { getBackendURL } from '../config';
    import { type Changelog } from '../core/protocalT';
    import Banner from './common/Banner.vue';

    const changelog = ref<Changelog>([]);

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

    updateChangelog();

    const reversedChangelog = computed(() => {
        return changelog.value.slice().reverse();
    })

    
</script>

<template>
    <div id="main">
        <div class="banner">
            <Banner/>
        </div>

        <!-- <h2>Document distribution</h2>
        <p>
            Visualize the distribution of documents using transformer encoder and tSNE.
            (<a :href="`${getBackendURL()}/static/visfeat`" target="_blank">Open externally</a>, 
            <a :href="`${getBackendURL()}/static/visfeat3d`" target="_blank"> 3D</a>)
        </p> 
        <iframe :src="`${getBackendURL()}/static/visfeat`" frameborder="0" id="visfeat"></iframe>

        <hr/> -->

        <h2>Info</h2>
        <div class="content">
            <p>
                <b>BackendURL</b>: {{getBackendURL()}}
            </p>
            <p>
                <b>About Lires</b>: ...
            </p>
        </div>

        <hr>

        <h2>Change log</h2>
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
    </div>
</template>

<style scoped> 
    div#main{
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        max-width: 900px;
        margin-top: 15px;
    }
    div.banner{
        display: flex;
        justify-content: center;
        width: 95vw;
        margin-bottom: 10px;
    }
    iframe#visfeat{
        width: 100%;
        height: 850px;
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
        margin-top: 20px;
        margin-bottom: 20px;
    }
</style>