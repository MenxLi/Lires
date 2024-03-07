
<script setup lang="ts">
    import { ThemeMode } from "../../core/misc";
    import { ref } from "vue";
    import SettingsContainer from "./SettingsContainer.vue";

    type ThemeT = "light" | "dark" | "auto";
    const currentDarkTheme = ref("auto" as ThemeT);
    function updateFlag(){ currentDarkTheme.value = ThemeMode.getThemeMode(); }

    function toggleTheme(
        theme: ThemeT
    ){
        if (theme === "auto"){
            ThemeMode.clear();
            ThemeMode.setDefaultDarkMode();
        } else if (theme === "light"){
            ThemeMode.setDarkMode(false);
        } else if (theme === "dark"){
            ThemeMode.setDarkMode(true);
        }
        updateFlag();
    }
    updateFlag();
</script>

<template>
    <SettingsContainer title="Theme" description="Change the theme of the app">
        <select v-model="currentDarkTheme" @change="toggleTheme(currentDarkTheme)" :style="{
            width: '80px',
            textAlign: 'center',
            padding: '0.2rem',
            justifySelf: 'flex-end'
        }">
            <option value="auto">Auto</option>
            <option value="light">Light</option>
            <option value="dark">Dark</option>
        </select>
    </SettingsContainer>
</template>
