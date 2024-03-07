<script setup lang="ts">

    const isChecked = defineModel({ default: false, })

    const emit = defineEmits<{
        (e: "onCheck", checkStatus: boolean): void
    }>()

</script>

<template>
    <div class="switch-toggle">
        <input type="checkbox" id="toggle" v-model="isChecked" @change="emit('onCheck', isChecked)">
        <label for="toggle" class="switch"></label>
    </div>
</template>

<style scoped>
.switch-toggle {
    position: relative;
    display: inline-block;
    width: 2rem;
    height: 1.2rem;
}

.switch-toggle input[type="checkbox"] {
    display: none;
}

.switch-toggle .switch {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: #ccc;
    border-radius: 1rem;
    cursor: pointer;
    transition: background-color 0.3s;
}

.switch-toggle .switch:before {
    position: absolute;
    content: "";
    height: 0.84rem;
    width: 0.84rem;
    left: 0.18rem;
    bottom: 0.18rem;
    background-color: white;
    border-radius: 50%;
    transition: transform 0.3s;
}

.switch-toggle input[type="checkbox"]:checked + .switch {
    background-color: #2196f3;
}

.switch-toggle input[type="checkbox"]:checked + .switch:before {
    transform: translateX(0.8rem);
}
</style>