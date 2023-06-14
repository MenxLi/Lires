
<script setup lang="ts">
    import { computed } from "vue";

    const props = defineProps<{
        icon_src: string,
        label_text: string,
    }>()

    const emit = defineEmits<{
        (e: "onClick"): void
    }>();

    function onClick(){
        emit("onClick");
    }

    // Compute the resolved path using the current URL and the relative icon_src
    const resolvedIconSrc = computed(() => {
    const baseUrl = new URL(import.meta.url);
    baseUrl.pathname = baseUrl.pathname.replace(/\/[^/]*$/, '/');
    return new URL(props.icon_src, baseUrl).href;
    });

</script>

<template>
    <span class="hoverMaxout105 button" @click="onClick">
        <img id="icon" class="icon" :src="resolvedIconSrc" :alt="label_text.toUpperCase() + '_ICON'">
        <label for="icon" class="iconLabel">{{ label_text }}</label>
    </span>
</template>

<style scoped>
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
    @media (max-width: 600px){
        .iconLabel{
            display: none;
        }
    }
</style>