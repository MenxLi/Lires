
<script setup lang="ts">
    withDefaults(defineProps<{
        iconSrc: string,
        labelText: string,
        title?: string
    }>(), {
        title: ""
    })

    const emit = defineEmits<{
        (e: "onClick"): void
    }>();

    function onClick(){
        emit("onClick");
    }

</script>

<template>
    <span class="hoverMaxout105 button" @click="onClick" :title="title">
        <img id="icon" class="icon" :src="iconSrc" :alt="labelText.toUpperCase() + '_ICON'">
        <label for="icon" class="iconLabel">{{ labelText }}</label>
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
        background-color: var(--color-background-theme-highlight);
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