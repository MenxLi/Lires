<script setup lang="ts">
  import {computed} from "vue";
  const props = withDefaults(defineProps<{
    "title"?: string,
    "show": boolean,
    "closeKey"?: string,
  }>(), {
    title: "_",
    closeKey: "Escape",
  });
  const emit = defineEmits<{
    (e: "close"): void,
    (e: "onClose"): void,   // equivalent to (e: "close")
    (e: 'update:show', value: boolean): void,
  }>();

  // two-way binding
  const showWindow = computed({
    get: () => props.show,
    set: (value) => {
      emit("update:show", value)
    },
  });
  function closeWindow() {
    showWindow.value = false;
    emit("onClose");
    emit("close")
  }

  window.addEventListener("keydown", (e) => {
    if (e.key === props.closeKey) {
      closeWindow();
      e.preventDefault()
    }
  });

</script>

<template>
  <div id="window" v-if="showWindow">
    <div id="blocker" @click="closeWindow"></div>
    <div class="floating-window">
      <div class="header">
        <label>{{ props.title }}</label>
        <button class="close-button" @click="closeWindow">
          <span class="close-icon">✕</span>
        </button>
      </div>
      <div class="window-content">
        <slot></slot>
      </div>
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

div#blocker {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 99;
}

div.header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 10px;
}

.header label, .header span{
  font-size: x-small;
  color: var(--color-text);
  opacity: 0.5;
}
.header label {
  text-align: left;
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
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  z-index: 100;
  box-shadow: 0 1px 3px 2px var(--color-shadow);

  animation-duration: 0.12s; /* the duration of the animation */
  animation-timing-function: ease-out; /* how the animation will behave */
  animation-delay: 0s; /* how long to delay the animation from starting */
  animation-iteration-count: 1; /* how many times the animation will play */
  animation-name: floatingWindowGradIn;
}

.window-content {
  margin: 15px;
  margin-top: 10px;
}

.close-button {
  min-width: 2.6em;
  width: 2.6em;
  height: 1.8em;

  align-self: flex-start;
  background: none;
  border: 1px solid var(--color-border);
  border-radius: 0.75em;
  cursor: pointer;
  padding: 0;

  display: flex;
  align-items: center;
  justify-content: center;
}

.close-button:hover{
  background-color: rgba(200, 50, 80, 0.3);
  transition: all 0.2s;
}

.close-icon {
  margin: 0px;
  font-size: medium;
  font-weight: bold;
}
</style>
