
<script setup lang="ts">
    import ConfigTheme from './ConfigTheme.vue';
</script>

<template>
    <div :style="{
        display: 'flex',
        flexDirection: 'column',
        gap: '1rem',
        padding: '1rem',
        width: '100%',
        height: '100%',
        overflowY: 'auto',
    }">
        <ConfigTheme/>
    </div>
</template>