<script setup lang="ts">
import Login from "./components/Login.vue"
import { ThemeMode } from "./core/misc";
import { MAINTAINER } from "./config";
ThemeMode.setDefaultDarkMode();
</script>

<template>
  <div id="main">
    <Login/>
    <label for="login" id="info">
      Need assistant? - <a :href="`mailto:${MAINTAINER.email}`">contact me</a>
    </label>
  </div>
</template>

<style scoped>
#info {
  bottom: 0;
  right: 0;
  margin: 0.5em;
  font-size: smaller;
}
</style>