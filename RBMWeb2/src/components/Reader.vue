<script setup lang="ts">
    import ReaderBody from './reader/ReaderBody.vue';
    import Banner from './common/Banner.vue';
    import { ref } from 'vue';
    import { useDataStore } from './store';
    import { useRoute } from 'vue-router';

    const dataStore = useDataStore();
    const route = useRoute();

    const uid = route.params.id as string;
    const datapoint = dataStore.database.get(uid);

    // 0: doc only
    // 1: note only
    // 2: doc and note
    const layoutType = ref<number>(2);

</script>

<template>
    <div id="main">
        <div id="banner">
            <Banner>
                <p>{{ datapoint.toString() }}</p>
            </Banner>
        </div>
        <ReaderBody :datapoint="datapoint" :layoutType="layoutType"></ReaderBody>
    </div>
</template>

<style scoped>
div#main{
    padding: 10px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 97vw;
    height: 97vh;
    background-color: var(--color-background);
}
div#banner{
    padding-bottom: 10px;
    width: 100%;
}
</style>