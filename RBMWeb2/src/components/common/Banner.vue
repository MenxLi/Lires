
<script setup lang="ts">

    import { ref, computed, onMounted, type Ref } from "vue";
    import type {SearchStatus} from "../home/_interface"
    import { checkCookieLogout, cookieLogout } from "../../core/auth";
    import { ThemeMode } from "../../core/misc";
    import FloatingWindow from "./FloatingWindow.vue";
    import BannerIcon from "./BannerIcon.vue";

    const props = withDefaults(defineProps<{
        searchText: string,
        showSearch: boolean,
    }>(), {
        "searchText": "",
        "showSearch": true,
    })
    const searchTypesPool = ref(["general", "title", "feature"])

    const emit = defineEmits<{
        (e: "onSearchChange", status: SearchStatus):void
    }>();
    
    const searchInput = ref(props.searchText)
    const searchSelector: Ref<HTMLSelectElement | null> = ref(null)
    function _onSearchChange(_: Event){
        const status: SearchStatus = {
            searchBy: searchSelector.value!.value,
            content: searchInput.value
        }
        emit("onSearchChange", status);
    }

    // logout related
    function logout(){
        cookieLogout();
        window.location.reload();
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

    onMounted(() => {
        searchSelector.value!.focus()
    })

</script>

<template>
    <FloatingWindow v-if="showNavigation" @onClose="showNavigation=!showNavigation" title="Navigation">
        <div id="exploreContainer">
            <a href="../index.html">Home</a>
            <a href="../feed.html">Arxiv daily</a>
        </div>
    </FloatingWindow>
    
    <div class="main shadow">
        <div class="button">
            <BannerIcon icon_src="../../assets/icons/logout.svg" label_text="Logout" @onClick="logout"/>
            <BannerIcon icon_src="../../assets/icons/explore.svg" label_text="Explore" @onClick="()=>{showNavigation = !showNavigation}"/>
            <BannerIcon icon_src="../../assets/icons/bulb_tips.svg" :label_text="themeLabel" @onClick="()=>toggleTheme()"/>
        </div>
        <div v-if="!checkCookieLogout() && props.showSearch" class="searchbar">
            <label for="searchbar"> Search: </label>
            <select ref="searchSelector" name="search_type" id="searchType" @change="_onSearchChange">
                <option v-for="v in searchTypesPool" :value="v">{{ v }}</option>
            </select>
            <input id="searchbar" type="text" v-model="searchInput" @input="_onSearchChange">
        </div>
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