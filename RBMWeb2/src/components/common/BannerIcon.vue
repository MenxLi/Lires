
<script setup lang="ts">
    import { onMounted, onUnmounted, computed, ref } from 'vue';

    const props = withDefaults(defineProps<{
        iconSrc: string,
        labelText: string,
        title?: string,
        shortcut?: string | null
    }>(), {
        title: "",
        shortcut: null
    })

    const title = computed(() => props.title + (props.shortcut === null ? "" : ` (${props.shortcut})`));

    const emit = defineEmits<{
        (e: "onClick"): void
        (e: "click"): void
    }>();

    const button = ref(null as HTMLButtonElement | null);
    const getBoundingClientRect = () => button.value?.getBoundingClientRect();
    defineExpose({getBoundingClientRect})

    function onClick(){
        emit("onClick");
        emit("click");
    }

    function evalShortcut(shortcut: string | null) : ((e: KeyboardEvent) => void) | null{
        if (shortcut === null) return null;
        const keys = shortcut.toLowerCase().split("+");
        return (e) => {
            if (keys.includes("ctrl") && !e.ctrlKey) return;
            if (keys.includes("alt") && !e.altKey) return;
            if (keys.includes("shift") && !e.shiftKey) return;
            if (keys.includes("meta") && !e.metaKey) return;
            if (!keys.includes(e.key.toLowerCase())) return;
            console.log("shortcut triggered: " + shortcut + " | " + props.labelText);
            onClick();
            e.preventDefault();
        }
    }

    const shortcutHandler = evalShortcut(props.shortcut);

    onMounted(() => {
        if (shortcutHandler !== null) window.addEventListener("keydown", shortcutHandler);
    });

    onUnmounted(() => {
        if (shortcutHandler !== null) window.removeEventListener("keydown", shortcutHandler);
    });

</script>

<template>
    <span class="hoverMaxout105 button non-selecable" @click="onClick" :title="`${title}`" ref="button">
        <img id="icon" class="icon" :src="iconSrc" :alt="labelText.toUpperCase() + '_ICON'">
        <label for="icon" class="iconLabel non-selectable">{{ labelText }}</label>
    </span>
</template>

<style scoped>
    span.button{
        padding: 3px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: smaller;
        gap: 2px;
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