<script setup lang="ts">
  const emit = defineEmits<{
    (e: "onClose"): void,
  }>();

  // use v-if to render the component
  function closeWindow() {
    emit("onClose");
  }
</script>

<template>
  <div class="floating-window">
    <button class="close-button" @click="closeWindow">
      <span class="close-icon">✕</span>
    </button>
    <div class="window-content">
      <slot></slot>
    </div>
  </div>
</template>


<style scoped>
@keyframes floatingWindowGradIn {
    0% {
        visibility: hidden;
        transform: translate(-50%, -50%) scale(0.9);
        opacity: 0;
    }
    100% {
        visibility: visible;
        transform: translate(-50%, -50%);
    }
}
.floating-window {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: var(--color-background-soft);
  /* border: 1px solid #ccc; */
  border: 1px solid var(--color-border);
  border-radius: 5px;
  padding: 15px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  z-index: 100;

  animation-duration: 0.15s; /* the duration of the animation */
  animation-timing-function: ease-out; /* how the animation will behave */
  animation-delay: 0s; /* how long to delay the animation from starting */
  animation-iteration-count: 1; /* how many times the animation will play */
  animation-name: floatingWindowGradIn;
}

.window-content {
  margin-top: 10px;
}

.close-button {
  align-self: flex-end;
  background: none;
  border: 1px solid var(--color-border);
  cursor: pointer;
  padding: 0;
}

.close-icon {
  margin: 5px;
  font-size: small;
  font-weight: bold;
}
</style>
