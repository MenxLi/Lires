
<script setup lang="ts">
    // a popup component at the top middle of the screen

    import { computed } from 'vue'
    import { PopupStyle } from '../interface';
    
    const props=withDefaults(defineProps<{
        styleType?: PopupStyle
    }>(),{
        styleType: "info"
    })

    const stylePopup = computed(
        ()=>{
            if (props.styleType === "alert"){
                return {
                    backgroundColor: "rgba(180, 0, 20, 0.9)",
                    color: "rgba(255, 255, 255, 1)"
                }
            }
            if (props.styleType === "warning"){
                return {
                    backgroundColor: "rgba(210, 150, 0, 0.9)",
                    // color: "rgba(0, 0, 0, 0.9)"
                    color: "rgba(255, 255, 255, 1)"
                }
            }
            if (props.styleType === "info"){
                return {
                    backgroundColor: "rgba(0, 0, 0, 0.75)",
                    color: "rgba(255, 255, 255, 1)"
                }
            }
            if (props.styleType === "success"){
                return {
                    backgroundColor: "rgba(0, 180, 0, 0.9)",
                    color: "rgba(255, 255, 255, 1)"
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
    <div id="popup" :style="stylePopup">
        <slot></slot>
    </div>
</template>

<style scoped>
    @keyframes popupGradIn {
        0% {
            visibility: hidden;
            /* scale: 0.9; */
            opacity: 0;
        }
        100% {
            visibility: visible;
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

        box-shadow: 0px 1px 3px 3px var(--color-shadow);
        border-radius: 10px;
        padding: 10px;

        /* animation */
        animation: popupGradIn 0.25s ease-in-out;
    }
</style>