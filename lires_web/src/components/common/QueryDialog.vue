
<script setup lang="ts">
    import FloatingWindow from './FloatingWindow.vue';
    import { computed } from 'vue';

    const props = withDefaults(defineProps<{
        "show": boolean,
        "title"?: string,
        "showCancel"?: boolean,
        "zIndex"?: number,
    }>(), {
        title: "Query",
        showCancel: true,
        zIndex: 99,
    });

    const emit = defineEmits<{
        (e: 'update:show', value: boolean): void,
        (e: "onClose"): void,   // equivalent to (e: "close")
        (e: "onAccept"): void,
        (e: "onCancel"): void,
    }>();

    const showWindow = computed({
        get: () => props.show,
        set: (value) => {
            emit("update:show", value)
        },
    });

</script>

<template>
    <FloatingWindow v-model:show="showWindow" :title="title" :compact="true" :z-index="zIndex"
    @on-close="()=>emit('onClose')">
        <div id="query-dialog-main">
            <div class="content">
                <slot></slot>
            </div>
            <div id="buttons">
                <div class="button ok-button" @click="()=>emit('onAccept')">OK</div>
                <div class="button cancel-button last-button" v-if="showCancel" @click="()=>emit('onCancel')">Cancel</div>
            </div>
        </div>
    </FloatingWindow>
</template>

<style scoped>
    div#query-dialog-main{
        display: flex;
        flex-direction: column;
        height: 100%;
    }

    div#buttons{
        display: flex;
        flex-direction: row;
        justify-content: space-around;
        margin-top: 10px;
        border-top: 1px solid var(--color-border);
    }

    div.button{
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        padding: 5px;
        cursor: pointer;
        background-color: var(--color-background-soft);
    }

    div.button:hover{
        box-shadow: inset 0px 0px 5px 1px var(--color-shadow);
    }
    div.ok-button:hover{
        background-color: var(--color-background-theme-highlight);
    }
    div.cancel-button:hover{
        background-color: var(--color-danger-hover);
    }
    div.last-button {
        border-left: 1px solid var(--color-border);
    }


</style>