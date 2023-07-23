
<script setup lang="ts">
    import { TAG_SEP } from '../../core/dataClass';
    import { computed } from 'vue';

    const props = withDefaults(defineProps<{
        tag: string,
        highlight?: boolean
    }>(), {
        highlight: false,
    })

    const tagComponents = computed(() => {
        const sp_tag = props.tag.split(TAG_SEP);
        if (sp_tag.length == 1){
            return ["", sp_tag[0]];
        }
        return [sp_tag.slice(0, sp_tag.length - 1).join('·'), sp_tag[sp_tag.length - 1]];
    })

</script>

<template>
    <div :class="`bubble${highlight? ' highlight' : ''}`">
        <div class="prefix" v-if="tagComponents[0]">
            {{ tagComponents[0] }}
        </div>
        {{ tagComponents[1] }}
    </div>
</template>

<style scoped>
div.bubble{
    padding: 5px;
    text-align: left;
    border-radius: 5px;
    background-color: var(--color-background-soft);
    transition: all 0.2s;

    font-size: small;

    display: flex;
    justify-content: center;
    align-items: center;
}

div.highlight{
    background-color: rgba(248, 54, 255, 0.247);
    box-shadow: 0 0 5px var(--color-shadow);
    transition: all 0.2s;
}

div.prefix{
    padding: 3px;
    background-color: var(--color-background-theme-thin);
    font-size: x-small;
    color: var(--color-text-theme);
    border-radius: 3px;
    margin-right: 5px;
}
</style>