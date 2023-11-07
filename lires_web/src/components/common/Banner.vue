
<script setup lang="ts">

    import { ref, computed } from "vue";
    import { useRouter } from "vue-router";
    import { settingsLogout, settingsAuthentication } from "../../core/auth";
    import { useSettingsStore } from "../store";
    import { ThemeMode } from "../../core/misc";
    import BannerIcon from "./BannerIcon.vue";
    import { MenuAttached } from './fragments.tsx'

    // https://vitejs.dev/guide/assets.html
    import logoutIcon from "../../assets/icons/logout.svg";
    import exploreIcon from "../../assets/icons/explore.svg";
    import bulbTipsIcon from "../../assets/icons/bulb_tips.svg";
    import homeIcon from "../../assets/icons/home.svg";

    const props = withDefaults(defineProps<{
        returnHome?: boolean,
    }>(), {
        returnHome: true,
    })

    // authentication on load
    const router = useRouter();
    settingsAuthentication().then(
        (userInfo)=>{if (!userInfo){ logout(); }},
        ()=>{logout();},
    )

    // logout related
    function logout(){
        settingsLogout();
        console.log("Logged out.", router.currentRoute.value.fullPath);
        router.push({
            path: "/login",
            query: {
                from: router.currentRoute.value.fullPath,
            }
        })
    }

    // theme related
    ThemeMode.setDefaultDarkMode();
    const _currentDarkTheme = ref(ThemeMode.isDarkMode());
    const themeLabel = computed(function(){
        if (_currentDarkTheme.value){ return "LightMode"; }
        else { return "DarkMode"; }
    })
    function toggleTheme(){
        ThemeMode.toggleDarkMode();
        _currentDarkTheme.value = !_currentDarkTheme.value;
    }

</script>

<template>
    <div class="main shadow">
        <div class="button">
            <BannerIcon v-if="props.returnHome" :iconSrc="homeIcon" labelText="Home" shortcut="ctrl+h"
                @onClick="()=>{router.push('/')}" title="home"/>
            <BannerIcon v-else :iconSrc="logoutIcon" labelText="Logout" shortcut="ctrl+q"
                @onClick="logout" title="logout"/>
            <MenuAttached :menuItems="[
                {name:'Home', action:()=>{router.push('/')}},
                {name:'Dashboard', action:()=>{router.push(`/dashboard/${useSettingsStore().userInfo!.username}`)}},
                {name:'Arxiv daily', action:()=>{router.push('/feed')}},
                {name:'About', action:()=>{router.push('/about')}},
            ]">
                <BannerIcon :iconSrc="exploreIcon" labelText="Explore" shortcut="ctrl+e" title="look around"/>
            </MenuAttached>
            <BannerIcon :iconSrc="bulbTipsIcon" :labelText="themeLabel" shortcut="ctrl+t"
                @onClick="()=>toggleTheme()" title="change theme"/>
        </div>
        <slot> <!-- some additional components --> </slot>
    </div>
</template>

<style scoped>
    div.main{
        position: fixed;
        top: 10px;
        left: 10px;
        right: 5px;
        /* height is 40px (10+30); */

        display: flex;
        align-items: center;
        justify-content: space-between;
        background-color: var(--color-background-soft);
        border-radius: 10px;
        padding-left: 10px;
        padding-right: 10px;
        font-size: small;
        height: 30px;
        z-index: 1;
    }
    div.button{
        display: flex;
        align-items: center;
    }
</style>