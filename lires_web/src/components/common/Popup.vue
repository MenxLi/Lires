
<script setup lang="ts">
    // a popup component at the top middle of the screen

    import { computed } from 'vue'
    import { PopupStyle } from '@/state/interface';
    
    const props=withDefaults(defineProps<{
        styleType?: PopupStyle
        position?: "top-center" | "center"
    }>(),{
        styleType: "info",
        position: "top-center"
    })

    const stylePopup = computed(
        ()=>{
            switch (props.styleType) {
                case "alert":
                case "error":
                    return {
                        backgroundColor: "rgba(180, 0, 20, 0.9)",
                        color: "rgba(255, 255, 255, 1)"
                    };
                case "warning":
                    return {
                        backgroundColor: "rgba(210, 150, 0, 0.9)",
                        color: "rgba(255, 255, 255, 1)"
                    };
                case "info":
                    return {
                        backgroundColor: "rgba(0, 0, 0, 0.75)",
                        color: "rgba(255, 255, 255, 1)"
                    };
                case "success":
                    return {
                        backgroundColor: "rgba(0, 180, 0, 0.9)",
                        color: "rgba(255, 255, 255, 1)"
                    };
                default:
                    return {
                        backgroundColor: "rgba(0, 0, 0, 0.5)",
                        color: "var(--color-text)"
                    };
            }
        }
    )

    const stylePopupPosition = computed(
        ()=>{
            if (props.position === "top-center"){
                return {
                    top: "30px",
                    left: "50%",
                    transform: "translate(-50%, 0)"
                }
            }
            if (props.position === "center"){
                return {
                    top: "50%",
                    left: "50%",
                    transform: "translate(-50%, -50%)"
                }
            }
            throw Error("Incorrect style.")
        }
    )

</script>

<template>
    <div id="popup" :style="{
        ...stylePopup,
        ...stylePopupPosition
        }">
        <slot></slot>
    </div>
</template>

<style scoped>
    @keyframes popupGradIn {
        0% {
            visibility: hidden;
            opacity: 0;
        }
        100% {
            visibility: visible;
        }
    }
    #popup{
        position: fixed;
        z-index: 100;

        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;

        box-shadow: 0px 1px 3px 3px var(--color-shadow);
        border-radius: 10px;
        padding: 10px;

        /* animation */
        animation: popupGradIn 0.25s ease-in-out;
    }
</style>