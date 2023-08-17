<!-- 
    A loading widget that can be used to show a loading animation
-->
<script setup lang="ts">
    import { computed } from 'vue';

    const props = withDefaults(defineProps<{
        size?: string,
        border_width?: string,
    }>(),{
        size: "40px",
        border_width: "5px",
    })

    const style = computed(()=>{
        return {
            width: props.size,
            height: props.size,
            border: props.border_width + " solid var(--color-border)",
            borderTopColor: "var(--color-primary)",     // has to claim it here, otherwise it will be overwritten by the border property
        }
    })

</script>

<template>
    <div class="loading-widget">
        <div class="loading-widget__spinner" :style="style"></div>
    </div>
</template>

<style scoped>
    .loading-widget {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
    }

    .loading-widget__spinner {
        border-radius: 50%;
        animation: spin 1s ease-in-out infinite;
    }

    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }
</style>