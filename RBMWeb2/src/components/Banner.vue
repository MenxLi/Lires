
<script setup lang="ts">

    import { ref, computed } from "vue";
    import type {SearchStatus} from "./_interface"
    import { checkCookieLogout, cookieLogout } from "@/core/auth";
    import type { Ref } from "vue";
    import { toggleDarkMode, isDefaultDarkMode } from "@/core/misc";

    const props = withDefaults(defineProps<{
        initSearchText: string
    }>(), {
        "initSearchText": ""
    })

    const emit = defineEmits<{
        (e: "onSearchChange", status: SearchStatus):void
    }>();
    
    const searchInput = ref(props.initSearchText)
    function _onSearchChange(event: Event){
        const status: SearchStatus = {
            content: searchInput.value
        }
        emit("onSearchChange", status);
    }

    function logout(){
        cookieLogout();
        window.location.reload();
    }

    const isDarkMode = ref(isDefaultDarkMode());
    const themeLabel = computed(function(){
        if (isDarkMode.value){ return "LightMode"; }
        else { return "DarkMode"; }
    })
    if (isDarkMode.value) {
        toggleDarkMode()
    }
    function toggleTheme(){
        toggleDarkMode();
        isDarkMode.value = !isDarkMode.value;
    }

</script>

<template>
    <div class="main shadow">
        <div class="button">
            <!-- <button @click="logout">Logout</button> -->
            <span v-if="!checkCookieLogout()" class="hoverMaxout105 button" @click="logout">
                <img id="logoutIcon" class="icon" src="@/assets/icons/logout.svg" alt="Logout">
                <label for="logoutIcon" id="logoutIconLabel">Logout</label>
            </span>
            <span class="hoverMaxout105 button" @click="(ev)=>toggleTheme()">
                <img id="themeIcon" class="icon" src="@/assets/icons/bulb_tips.svg" alt="Logout">
                <label for="themeIcon" id="themeIconLabel">{{ themeLabel }}</label>
            </span>
        </div>
        <div v-if="!checkCookieLogout()" class="searchbar">
            <label for="searchbar"> Search: </label>
            <input id="searchbar" type="text" v-model="searchInput" @input="_onSearchChange">
        </div>
    </div>
</template>

<style scoped>
    div.main{
        display: flex;
        align-items: center;
        justify-content: space-between;
        background-color: rgba(102, 51, 153, 0.491);
        background-color: var(--color-background-soft);
        border-radius: 10px;
        padding-left: 10px;
        padding-right: 10px;
    }
    div.button{
        display: flex;
        align-items: center;
        gap: 3px;
    }
    span.button{
        padding: 3px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        font-size: smaller;
    }
    span.button:hover{
        background-color: var(--theme-hover-highlight-color);
        box-shadow: 0 1px 3px 2px var(--color-shadow);
        transition: all 0.2s;
    }
    img.icon {
        height: 20px;
        filter: invert(0.5) opacity(0.75) drop-shadow(0 0 0 var(--color-border)) ;
    }
</style>