
<script setup lang="ts">
    import { ref } from 'vue';
    import type { Ref } from "vue";
    import { useUIStateStore } from '../store';

    import type { SearchStatus } from "../interface";
    import type { SearchType } from '/@/api/protocol';
    import { lazify } from "../../utils/misc";

    const uiState = useUIStateStore();

    // search refealated
    const searchTypesPool: SearchType[] = ["title", "author", "year", "note", "publication", "feature", "uuid"];
    const searchInput = ref("")
    const searchSelector: Ref<HTMLSelectElement | null> = ref(null)
    function onSearchChanged(){
        const status: SearchStatus = {
            searchBy: searchSelector.value!.value as SearchType,
            content: searchInput.value
        }
        uiState.searchState = status;
        console.log(status);
        uiState.updateShownData();
    }
    const lazyOnSearchChanged = lazify(onSearchChanged, 300);

    function capitalizeFirstLetter(string: string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }
</script>

<template>
    <div id="searchbar">
        <div id="searchbar-container">
            <select ref="searchSelector" name="search_type" id="searchType" @change="onSearchChanged">
                <option v-for="v in searchTypesPool" :value="v">{{ capitalizeFirstLetter(v) }}</option>
            </select>
            <input type="text" id="searchbar-input" placeholder="Search" v-model="searchInput" @input="lazyOnSearchChanged">
        </div>
    </div>
</template>

<style scoped>
    div#searchbar{
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 5px 0;
    }

    div#searchbar-container{
        display: flex;
        align-items: center;
        gap: 10px;

        border: 1px solid var(--color-border);
        border-radius: 20px;
        padding-inline: 5px;
        margin-inline: 10px;
        width: 100%;
        height: 2rem;
    }

    select#searchType{
        border: none;
        outline: none;
        /* font-size: medium; */
        width: 100px;
        padding-inline: 5px;
        padding-block: 5px;
        border-radius: 20px;
        font-weight: bold;
        background-color: var(--color-background-ssoft);
        color: var(--color-theme);

        text-align-last: center;

        /* display: flex;
        align-items: center;
        justify-content: center; */
        /* font-weight: bold; */
    }

    input#searchbar-input{
        border: none;
        outline: none;
        width: 100%;
        font-size: medium;
        /* font-weight: bold; */
    }
    input#searchbar-input::placeholder{
        color: rgba(120, 120, 120, 0.5);
    }
</style>