
<script setup lang="ts">

    import { ref, computed } from "vue";
    import { useRouter } from "vue-router";
    import { cookieLogout } from "../../core/auth";
    import { ThemeMode } from "../../core/misc";
    import FloatingWindow from "./FloatingWindow.vue";
    import BannerIcon from "./BannerIcon.vue";

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

    // Navigation related
    const showNavigation = ref(false);

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
    <FloatingWindow v-if="showNavigation" @onClose="showNavigation=!showNavigation" title="Navigation">
        <div id="exploreContainer">
            <!-- <a href="../index.html">Home</a> -->
            <!-- <a href="../feed.html">Arxiv daily</a> -->
            <router-link to="/">Home</router-link>
            <router-link to="/feed">Arxiv daily</router-link>
        </div>
    </FloatingWindow>
    
    <div class="main shadow">
        <div class="button">
            <BannerIcon :iconSrc="logoutIcon" labelText="Logout" @onClick="logout"/>
            <BannerIcon :iconSrc="exploreIcon" labelText="Explore" @onClick="()=>{showNavigation = !showNavigation}"/>
            <BannerIcon :iconSrc="bulbTipsIcon" :labelText="themeLabel" @onClick="()=>toggleTheme()"/>
        </div>
        <slot> <!-- some additional components --> </slot>
    </div>
</template>

<style scoped>
    div#exploreContainer{
        display: flex;
        flex-direction: column;
        min-width: 100px;
        padding: 10px;
        padding-left: 15px;
        padding-right: 15px;
        gap: 20px;
    }
    div#exploreContainer a{
        min-height: 2.5em;
        min-width: 8em;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: var(--color-background-mute);
        border: 1px solid var(--color-border);
        border-radius: 5px;
        color: var(--color-text);
    }
    div#exploreContainer a:hover{
        background-color: var(--theme-hover-highlight-color);
        box-shadow: 0 1px 3px 2px var(--color-shadow);
        transition: all 0.2s;
    }
    div.main{
        display: flex;
        align-items: center;
        justify-content: space-between;
        background-color: rgba(102, 51, 153, 0.491);
        background-color: var(--color-background-soft);
        border-radius: 10px;
        padding-left: 10px;
        padding-right: 10px;
        font-size: small;
    }
    div.button{
        display: flex;
        align-items: center;
        gap: 3px;
    }
</style>