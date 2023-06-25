
<script setup lang="ts">

    import { ref, computed } from "vue";
    import { useRouter } from "vue-router";
    import { cookieLogout } from "../../core/auth";
    import { ThemeMode } from "../../core/misc";
    import BannerIcon from "./BannerIcon.vue";
    import { MenuAttached } from './fragments.tsx'

    import { ServerConn } from "../../core/serverConn";
    import { getCookie } from "../../libs/cookie";

    // https://vitejs.dev/guide/assets.html
    import logoutIcon from "../../assets/icons/logout.svg";
    import exploreIcon from "../../assets/icons/explore.svg";
    import bulbTipsIcon from "../../assets/icons/bulb_tips.svg";

    // authentication on load
    const conn = new ServerConn();
    const router = useRouter();
    conn.authUsr(getCookie("encKey") as string).then(
        ()=>{},
        function(){
            logout();
        },
    )

    // logout related
    function logout(){
        cookieLogout();
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
            <BannerIcon :iconSrc="logoutIcon" labelText="Logout" shortcut="ctrl+q"
                @onClick="logout" title="logout"/>
            <MenuAttached :menuItems="[
                {name:'Home', action:()=>{router.push('/')}},
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
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: space-between;
        background-color: rgba(102, 51, 153, 0.491);
        background-color: var(--color-background-soft);
        border-radius: 10px;
        padding-left: 10px;
        padding-right: 10px;
        font-size: small;
        height: 25px;
    }
    div.button{
        display: flex;
        align-items: center;
        gap: 3px;
    }
</style>