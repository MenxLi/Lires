
<script setup lang="ts">

    import { ref } from "vue";
    import type {SearchStatus} from "./_interface"
    import { saveAuthentication } from "@/core/auth";
    import type { Ref } from "vue";

    const props = defineProps<{
        initSearchText: string
    }>()

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
        saveAuthentication("", null, false, 0);
        window.location.reload();
    }

</script>

<template>
    <div class="main">
        <div class="button">
            <!-- <button @click="logout">Logout</button> -->
            <span class="hoverMaxout105 button" @click="logout">
                <img id="logoutIcon" src="@/assets/icons/logout.svg" alt="Logout">
                <label for="logoutIcon" id="logoutIconLabel">Logout</label>
            </span>
        </div>
        <div class="searchbar">
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
    }
    span.button{
        padding: 3px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        font-size: smaller;
    }
    span.button:hover{
        background-color: var(--theme-hover-hight-color);
    }
    #logoutIcon {
        height: 20px;
        filter: invert(0.5) opacity(0.5) drop-shadow(0 0 0 var(--color-border)) ;
    }
</style>