
<script setup lang="ts">
    import { computed } from 'vue'
    // a popup component at the top middle of the screen
    
    const props=withDefaults(defineProps<{
        // two-way binding
        show?: boolean
        style: "alert" | "warning" | "info" | "success"
    }>(),{
        show: false
    })

    const emits = defineEmits<{
        // two-way binding
        (e: 'update:show', value: boolean) : void
    }>()

    const showPopup = computed({
        get: () => props.show,
        set: (value) => {
            emits('update:show', value)
        }
    });

    const stylePopup = computed(
        ()=>{
            if (props.style === "alert"){
                return {
                    backgroundColor: "rgba(180, 0, 0, 0.8)",
                    color: "rgba(255, 255, 255, 0.9)"
                }
            }
            if (props.style === "warning"){
                return {
                    backgroundColor: "rgba(180, 180, 0, 0.8)",
                    color: "rgba(0, 0, 0, 0.9)"
                }
            }
            if (props.style === "info"){
                return {
                    backgroundColor: "rgba(0, 0, 0, 0.8)",
                    color: "rgba(255, 255, 255, 0.9)"
                }
            }
            if (props.style === "success"){
                return {
                    backgroundColor: "rgba(0, 180, 0, 0.8)",
                    color: "rgba(255, 255, 255, 0.9)"
                }
            }
            else{
                return {
                    backgroundColor: "rgba(0, 0, 0, 0.5)",
                    color: "var(--color-text)"
                }
            }
        }
    )

</script>

<template>
    <div id="popup" v-if="showPopup" :style="stylePopup">
        <slot></slot>
    </div>
</template>

<style scoped>
    @keyframes popupGradIn {
        0% {
            visibility: hidden;
            transform: translate(-50%, 0) scale(0.9);
            opacity: 0;
        }
        100% {
            visibility: visible;
            transform: translate(-50%, 0);
        }
    }
    #popup{
        position: fixed;
        top: 30px;
        left: 50%;
        transform: translate(-50%, 0);
        z-index: 100;

        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;

        box-shadow: 0px 3px 5px 5px var(--color-shadow);
        border-radius: 10px;
        padding: 10px;

        /* animation */
        animation: popupGradIn 0.25s ease-in-out;
    }
</style>