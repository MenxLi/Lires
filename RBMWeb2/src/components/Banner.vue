
<script setup lang="ts">

    import { ref } from "vue";
    import type {SearchStatus} from "./_interface"
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

</script>

<template>
    <div class="main">
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
    }
</style>