<script setup lang="ts">
import LoginInput from "./login/LoginInput.vue"
import { ThemeMode } from "../core/misc";
import { MAINTAINER } from "../config";
ThemeMode.setDefaultDarkMode();

function _notImplemented(){
  alert("Not implemented yet. \nPlease contact the maintainer for registration.");
}
</script>

<template>
  <div id="main">
    <div id="container">
      <LoginInput/>
      <label for="login" id="info">
        Need assistant? - <a @click="_notImplemented">Register</a> | <a :href="`mailto:${MAINTAINER.email}`">Contact me</a>
      </label>
    </div>
  </div>
</template>

<style scoped>
#main{
  display: flex;
  height: 100vh;
  width: 100vw;
  justify-content: center;
  align-items: center;
}
#info {
  bottom: 0;
  right: 0;
  margin: 0.5em;
  font-size: smaller;
}
</style>