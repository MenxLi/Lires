<script setup lang="ts">
    import { useSettingsStore } from "@/state/store";
    import { computed, ref } from "vue";
    import SettingsContainer from "./SettingsContainer.vue";
    import FloatingWindow from "../common/FloatingWindow.vue";

    const settings = useSettingsStore();

    const apiBase = computed({
        get: () => settings.openaiApiBase,
        set: (val) => settings.setOpenaiApiBase(val)
    });

    const apiKey = computed({
        get: () => settings.openaiApiKey,
        set: (val) => settings.setOpenaiApiKey(val)
    });

    const modelName = computed({
        get: () => settings.openaiModelName,
        set: (val) => settings.setOpenaiModelName(val)
    });

    const showWindow = ref(false);
</script>

<template>
    <SettingsContainer title="AI Settings" description="Configure OpenAI compatible API settings">
        <button class="config-btn" @click="showWindow = true">Configure</button>
        
        <FloatingWindow v-model:show="showWindow" title="OpenAI Configuration">
            <div class="config-openai-container">
                <div class="input-group">
                    <label>API Base</label>
                    <input v-model="apiBase" type="text" placeholder="https://api.openai.com/v1" />
                </div>
                <div class="input-group">
                    <label>API Key</label>
                    <input v-model="apiKey" type="password" placeholder="sk-..." />
                </div>
                <div class="input-group">
                    <label>Model Name</label>
                    <input v-model="modelName" type="text" placeholder="gpt-3.5-turbo" />
                </div>
            </div>
        </FloatingWindow>
    </SettingsContainer>
</template>

<style scoped>
.config-btn {
    padding: 0.3rem 0.8rem;
    background-color: var(--color-background-soft);
    border: 1px solid var(--color-border);
    border-radius: 4px;
    cursor: pointer;
    color: var(--color-text);
    font-size: 0.9rem;
    transition: background-color 0.2s;
}

.config-btn:hover {
    background-color: var(--color-background-mute);
}

.config-openai-container {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
    width: 400px;
    max-width: 90vw;
}

.input-group {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
}

.input-group label {
    font-size: 0.85rem;
    font-weight: 500;
    color: var(--color-text-soft);
}

.input-group input {
    padding: 0.5rem;
    border: 1px solid var(--color-border);
    border-radius: 4px;
    background-color: var(--color-background-mute);
    color: var(--color-text);
    font-family: inherit;
    font-size: 0.95rem;
}

.input-group input:focus {
    outline: none;
    border-color: var(--color-border-hover);
    box-shadow: 0 0 0 2px var(--color-focus-ring, rgba(0, 123, 255, 0.2));
}
</style>
