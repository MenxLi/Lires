
<script setup lang="ts">

    import { ref } from "vue";
    import { useRouter } from "vue-router";
    import { settingsLogout } from "../../core/auth";
    import { useDataStore } from "../store";
    import ToolbarIcon from "./ToolbarIcon.vue";
    import { MenuAttached } from './fragments.tsx'

    import FloatingWindow from "./FloatingWindow.vue";
    import SettingsWindow from "../settings/SettingsWindow.vue";

    // https://vitejs.dev/guide/assets.html
    import logoutIcon from "../../assets/icons/logout.svg";
    import exploreIcon from "../../assets/icons/explore.svg";
    // import bulbTipsIcon from "../../assets/icons/bulb_tips.svg";
    import homeIcon from "../../assets/icons/home.svg";
    import settigsIcon from "../../assets/icons/tune.svg";

    const props = withDefaults(defineProps<{
        returnHome?: boolean,
        compact?: boolean,
    }>(), {
        returnHome: true,
        compact: false,
    })

    const router = useRouter();
    function logout(){
        settingsLogout(); // will trigger the watcher in App.vue
    }

    // theme related
    const mainDiv = ref(null as HTMLDivElement | null);
    let lastScrollTop = 0;
    window.addEventListener('scroll', function() {
        const scrollTop = window.scrollY || document.documentElement.scrollTop;
        if (scrollTop <= lastScrollTop || lastScrollTop < 10) {
            // Scrolling up
            if (mainDiv.value && mainDiv.value.classList.contains('hidden')){
                mainDiv.value!.classList.remove('hidden');
            }
        } else {
            // Scrolling down
            if (mainDiv.value && !mainDiv.value!.classList.contains('hidden')){
                mainDiv.value!.classList.add('hidden');
            }
        }
        lastScrollTop = scrollTop;
    });

    const showSettings = ref(false);

</script>

<template>
    <FloatingWindow v-model:show="showSettings" title="Settings">
        <SettingsWindow/>
    </FloatingWindow>

    <div :class="`main-toolbar ${props.compact ? 'compact-layout' : 'normal-layout shadow'}` "ref="mainDiv">
        <div class="button">
            <ToolbarIcon v-if="props.returnHome" :iconSrc="homeIcon" labelText="Home" shortcut="ctrl+h"
                @onClick="()=>{router.push('/')}" title="home"/>
            <ToolbarIcon v-else :iconSrc="logoutIcon" labelText="Logout" shortcut="ctrl+q"
                @onClick="logout" title="logout"/>
            <ToolbarIcon :iconSrc="settigsIcon" labelText="Settings" shortcut="ctrl+c"
                @onClick="()=>{showSettings=true}" title="Open settings"/>
            <MenuAttached :menuItems="[
                {name:'Home', action:()=>{router.push('/')}},
                {name:'Dashboard', action:()=>{router.push(`/dashboard/${useDataStore().user.username}`)}},
                {name:'Arxiv daily', action:()=>{router.push('/feed')}},
                {name:'About', action:()=>{router.push('/about')}},
            ]">
                <ToolbarIcon :iconSrc="exploreIcon" labelText="Explore" shortcut="ctrl+e" title="look around"/>
            </MenuAttached>
        </div>
        <slot> <!-- some additional components --> </slot>
    </div>
</template>

<style scoped>
    div.main-toolbar.normal-layout{
        /* height is 40px (10+30); */
        top: 10px;
        left: 10px;
        right: 5px;
        border-radius: 13px;
        padding-left: 10px;
        padding-right: 10px;
    }
    div.main-toolbar.compact-layout{
        top: 0px;
        left: 0px;
        right: 0px;
        border-radius: 0px;
        padding-left: 10px;
        padding-right: 10px;
    }

    div.main-toolbar{
        position: fixed;
        display: flex;
        align-items: center;
        justify-content: space-between;
        background-color: var(--color-background-soft);
        font-size: small;
        height: 30px;
        z-index: 1;
        transition: top 0.25s ease-in-out;
    }
    div.main-toolbar.hidden{
        top: -30px;
    }
    div.button{
        display: flex;
        align-items: center;
    }

    @media only screen and (max-width: 767px) {
        div.main-toolbar{
            left: 0px;
            right: 0px;
            border-radius: 0px;
        }
    }
</style>