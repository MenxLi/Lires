<script setup lang="ts">
</script>

<template>
    <div id="widget-container-main">
        <slot></slot>
    </div>
</template>

<style scoped>
    div#widget-container-main{
        /* background-color: var(--color-background-soft); */
        box-shadow: 0px 2px 3px 0px var(--color-shadow);
        background-color: var(--color-background);
        border: 1px solid var(--color-border);
        border-radius: 20px;
        padding: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-wrap: wrap;
        flex-direction: row;

        max-width: 1200px;
    }

    @media only screen and (max-width: 767px) {
        /* Styles for mobile devices */
        div#widget-container-main{
            border-radius: 0px;
            border: none;
            box-shadow: none;
            padding: 0px;
        }
    }

</style>