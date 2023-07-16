<script setup lang="ts">
    import { computed } from 'vue';
    const props = withDefaults(defineProps<{
        "show": boolean,
        "menuItems": {
            "name": string,
            "action": () => void,
        }[],
        "position": {
            "x": number,
            "y": number,
        },
        "blocker"?: boolean,
        // middleTop: if true, the menu will be displayed with transition x = x - width/2
        //      else the menu will be displayed with top-left corner at (x, y)
        "middleTop"?: boolean,      
        "zIndex"?: number,
        "arrow"? : boolean,
    }>(), {
        "blocker": false,
        "middleTop": false,
        "zIndex": 100,
        "arrow": false,
    });

    const emits = defineEmits<{
        (e: 'update:show', value: boolean): void,
    }>();

    const showMenu = computed({
        get: () => props.show,
        set: (value) => {
            emits("update:show", value)
        },
    });

    function closeMenu() {
        showMenu.value = false;
    }
</script>

<template>
    <div id="blocker" @click="closeMenu" v-if="blocker"
        :style="{ zIndex: props.zIndex - 1, }"
    ></div>
    <div id="floatingMenu" :style="{
        left: props.position.x + 'px',
        top: props.position.y + 'px',
        visibility: showMenu ? 'visible' : 'hidden',
        transform: props.middleTop ? 'translate(-50%, 0)' : '',
        zIndex: props.zIndex,
    }">
        <div id="arrow" v-if="props.arrow"></div>
        <div :class="`non-selectable floatingMenuItem${index!==props.menuItems.length-1?'':' floatingMenuItemLast'}`" 
            tabindex="0" @keydown.enter="item.action(); closeMenu()"
            v-for="(item, index) in props.menuItems" @click="item.action(); closeMenu()">
            {{ item.name }}
        </div>
    </div>
</template>

<style scoped>
    div#blocker {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
    }
    #arrow {
        position: absolute;
        top: -10px;
        left: 50%;
        margin-left: -10px;
        width: 0;
        height: 0;
        border-left: 10px solid transparent;
        border-right: 10px solid transparent;
        border-bottom: 10px solid var(--color-background-soft);
    }
    #floatingMenu{
        position: fixed;
        z-index: 101;
        background-color: var(--color-background-soft);
        border: 1px solid var(--color-border);
        border-radius: 5px;
        box-shadow: 0 1px 3px 2px var(--color-shadow);
    }
    .floatingMenuItem{
        cursor: pointer;
        padding: 5px;
        padding-left: 15px;
        padding-right: 15px;
        border-bottom: 1px solid var(--color-border);
        /* min-width: 80px; */
    }
    .floatingMenuItemLast{
        border-bottom: none;
    }
    .floatingMenuItem:hover{
        background-color: var(--color-background-theme-highlight);
    }
</style>