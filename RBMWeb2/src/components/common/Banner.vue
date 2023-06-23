
<script setup lang="ts">

    import { ref, computed } from "vue";
    import { useRouter } from "vue-router";
    import { cookieLogout } from "../../core/auth";
    import { ThemeMode } from "../../core/misc";
    import BannerIcon from "./BannerIcon.vue";
    import Menu from "./Menu.vue";

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
    const exploreBtn = ref(null as typeof BannerIcon | null);
    const showNavigation = ref(false);
    const navigationMenuPosition = computed(function(){
        if (showNavigation.value){
            // this is tricky, because the button is not rendered yet on the first time
            // showNavigation is set to false by default, so it is safe to use !.
            // use other methods to get the position of the button, such as coditioned value, 
            // will cause the menu to be rendered at the wrong position somehow... may need to fix this later
            // exploreBtn.value is a BannerIcon component, the getBoundingClientRect() method is an exposed method
            return {
                left: exploreBtn.value!.getBoundingClientRect().left + exploreBtn.value!.getBoundingClientRect().width / 2,
                top: exploreBtn.value!.getBoundingClientRect().bottom + 5,
            }
        }
        else {
            return {
                left: 0,
                top: 0,
            }
        }
    })

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
    <Menu v-model:show="showNavigation" :menuItems="[
        {name:'Home', action:()=>{router.push('/')}},
        {name:'Arxiv daily', action:()=>{router.push('/feed')}}
        ]" :position="navigationMenuPosition" :middleTop="true" :arrow="true"></Menu>

    <div class="main shadow">
        <div class="button">
            <BannerIcon :iconSrc="logoutIcon" labelText="Logout" shortcut="ctrl+q"
                @onClick="logout" title="logout"/>
            <BannerIcon :iconSrc="exploreIcon" labelText="Explore" shortcut="ctrl+e" ref="exploreBtn"
                @onClick="()=>{showNavigation = !showNavigation}" title="look around"/>
            <BannerIcon :iconSrc="bulbTipsIcon" :labelText="themeLabel" shortcut="ctrl+t"
                @onClick="()=>toggleTheme()" title="change theme"/>
        </div>
        <slot> <!-- some additional components --> </slot>
    </div>
</template>

<style scoped>
    /* div#exploreContainer{
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
        background-color: var(--color-background-theme-highlight);
        box-shadow: 0 1px 3px 2px var(--color-shadow);
        transition: all 0.2s;
    } */
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
    }
    div.button{
        display: flex;
        align-items: center;
        gap: 3px;
    }
</style>