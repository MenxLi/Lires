<script setup lang="ts">
    import ReaderBody from './reader/ReaderBody.vue';
    import Banner from './common/Banner.vue';
    import BannerIcon from './common/BannerIcon.vue';
    import { ref, onMounted } from 'vue';
    import { useDataStore } from './store';
    import { useRoute } from 'vue-router';

    import splitscreenIcon from '../assets/icons/splitscreen.svg';

    const dataStore = useDataStore();
    const route = useRoute();

    const uid = route.params.id as string;
    const datapoint = dataStore.database.get(uid);

    // 0: doc only
    // 1: note only
    // 2: doc and note
    const layoutType = ref<number>(2);

    // initialize layoutType according to screen size
    if (window.innerWidth < 800){
        layoutType.value = 0;
    }
    function changeLayout(){
        if (window.innerWidth < 800){
            // only two layouts for small screen
            layoutType.value = (layoutType.value + 1)%2
        } else {
            layoutType.value = (layoutType.value + 1)%3
        }
    }

    // empty database check 
    const banner = ref<null | typeof Banner>(null);
    onMounted(() => {
        if (Object.keys(dataStore.database.data).length === 0){
            banner.value!.showPopup("Database not loaded or empty database.", "alert");
        }
    })

</script>

<template>
    <div id="main">
        <div id="banner">
            <Banner ref="banner">
                <div id="bannerOps">
                    <BannerIcon :iconSrc="splitscreenIcon" labelText="" @onClick="changeLayout" title="change layout"></BannerIcon>
                    |
                    <p>{{ `${datapoint.authorAbbr()} (${datapoint.summary.year})` }}</p>
                </div>
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
    width: 98vw;
    height: 96vh;
    background-color: var(--color-background);
}
div#banner{
    padding-bottom: 10px;
    width: 100%;
}
div#bannerOps{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
}
</style>