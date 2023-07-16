<script setup lang="ts">
    import { ServerConn } from '../core/serverConn';
    import { ref, computed } from 'vue';
    import Banner from './common/Banner.vue';

    const changelog = ref<Record<string, string[]>>({});

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
        const new_obj= {} as Record<string, string[]>;
        const rev_obj = Object.keys(changelog.value).reverse();
        rev_obj.forEach(function(i) { 
            new_obj[i] = changelog.value[i];
        })
        return new_obj;
    })

    
</script>

<template>
    <div id="main">
        <div class="banner">
            <Banner/>
        </div>

        <h1>Change log</h1>
        <div id="versionHistory" class="content">
            <div class="block" v-for="(changes, version) in reversedChangelog">
                <h2>{{version.toString()}}</h2>
                <ul>
                    <li v-for="change in changes">{{change}}</li>
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
        max-width: 800px;
        margin-top: 15px;
    }
    div.banner{
        display: flex;
        justify-content: center;
        width: 95vw;
        margin-bottom: 10px;
    }
    div.content{
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
</style>