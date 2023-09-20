<!-- A popout at the right bottom corner of the screen that shows a loading animation -->
<script setup lang="ts">
    import { computed } from "vue";

    const props = withDefaults(
        defineProps<{
            text?: string
            perc: number
        }>(),
        {
            "text": "Progress: "
        }
    )

    const barStyle = computed(() => {
        return {
            width: props.perc*120 + 'px'
        }
    })
</script>

<template>
    <div class="loading-popout">
        <label>{{ props.text }}</label>
        <div class="bar" id="bar">
            <div class="bar" id="barCurrent" :style=barStyle></div>
        </div>
    </div>
</template>

<style scoped>
div.loading-popout{
    position: absolute;
    bottom: 0;
    right: 0;
    padding: 10px;
    margin: 20px;
    padding-left: 25px;
    padding-right: 25px;
    min-width: 260px;

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

label{
    min-width: 90px;
}
div.bar{
    height: 8px;
    border-radius: 4px;
}
div#bar{
    width: 120px;
    background-color: var(--color-border)
}
div#barCurrent{
    background-color: var(--color-text);
}


</style>