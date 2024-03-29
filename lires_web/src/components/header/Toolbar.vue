
<script setup lang="ts">

    import { computed, ref } from "vue";
    import { useRouter, useRoute } from "vue-router";
    import { settingsLogout } from "../../core/auth";
    import ToolbarIcon from "../header/ToolbarIcon.vue";
    import { MenuAttached } from '../common/fragments.tsx'
    import FloatingWindow from "../common/FloatingWindow.vue";
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
        showNavigator?: boolean,
    }>(), {
        returnHome: true,
        compact: true,
        showNavigator: true,
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

    const route = useRoute();
    const currPage = computed(()=>{
        const ret = route.path.split('/')[1];
        // console.log("currPage", ret);
        return ret;
    });

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
            <ToolbarIcon :iconSrc="settigsIcon" labelText="Settings" shortcut="ctrl+,"
                @onClick="()=>{showSettings=true}" title="Open settings"/>
            <MenuAttached :menuItems="[
                {name:'Home', action:()=>{router.push('/')}},
                {name:'Feed', action:()=>{router.push('/feed')}},
                {name:'About', action:()=>{router.push('/about')}},
            ]" v-if="!showNavigator">
                <ToolbarIcon :iconSrc="exploreIcon" labelText="Explore" shortcut="ctrl+e" title="look around"/>
            </MenuAttached>
        </div>

        <div id="navigator" v-if="showNavigator">
            <div class="nav-toggle">
                <div :class="`button ${currPage === 'home' || !currPage ? 'active-nav' : ''}`" @click="()=>{router.push('/')}">Home</div>
                <!-- <div :class="`button ${currPage === 'dashboard' ? 'active-nav' : ''}`" @click="()=>{router.push(`/dashboard/${useDataStore().user.username}`)}">Dashboard</div> -->
                <div :class="`button ${currPage === 'feed' ? 'active-nav' : ''}`" @click="()=>{router.push('/feed')}">Feed</div>
                <div :class="`button ${currPage === 'about' ? 'active-nav' : ''}`" @click="()=>{router.push('/about')}">About</div>
            </div>
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
        padding-inline: 10px;
        padding-right: 10px;
    }
    div.main-toolbar.compact-layout{
        top: 0px;
        left: 0px;
        right: 0px;
        border-radius: 0px;
        padding-inline: 20px;
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

    div.nav-toggle{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1.5rem;
        background-color: var(--color-background-soft);
        font-size: small;
        height: 30px;
        z-index: 1;
        transition: top 0.25s ease-in-out;
    }
    div.nav-toggle div.button{
        cursor: pointer;
        user-select: none;
        font-weight: bold;
        color: var(--color-text-soft);
    }
    div.nav-toggle div.button.active-nav{
        border-bottom: 1px solid var(--color-theme);
        color: var(--color-theme);
    }

    @media only screen and (max-width: 767px) {
        div.main-toolbar{
            left: 0px;
            right: 0px;
            border-radius: 0px;
        }
    }
</style>