<!-- A popout at the right bottom corner of the screen that shows a loading animation -->
<script setup lang="ts">
    import LoadingWidget from "./LoadingWidget.vue";
</script>

<template>
    <div class="loading-popout">
        <LoadingWidget size="25px" />
        Loading...
    </div>
</template>

<style scoped>
div.loading-popout{
    position: absolute;
    bottom: 0;
    right: 0;
    padding: 10px;
    width: 180px;
    margin: 20px;

    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: center;
    gap: 10px;

    border: 1px solid var(--color-border);
    border-radius: 5px;
    box-shadow: 0px 1px 2px 0px var(--color-shadow);

    z-index: 99;
    background-color: var(--color-background-theme-thin);
    /* background-color: rebeccapurple; */
}
</style>