<script setup lang="ts">
import LoginInput from "./login/LoginInput.vue"
import FloatingWindow from "./common/FloatingWindow.vue";
import RegistrationForm from "./login/RegistrationForm.vue";
import { useUIStateStore } from "../state/store";
import { useRouter } from "vue-router";
import { ThemeMode } from "../core/misc";
import { MAINTAINER } from "../config";
import { ref } from "vue";
ThemeMode.setDefaultDarkMode();

const defaultInvitationCode = ref('');
const showRegistration = ref(false);
const router = useRouter();
// check if invitation code is provided
console.log(router.currentRoute.value.query.invitation);
if (router.currentRoute.value.query.invitation) {
  showRegistration.value = true;
  defaultInvitationCode.value = router.currentRoute.value.query.invitation as string;
}
</script>

<template>
  <FloatingWindow title="User registration" v-model:show="showRegistration" :compact="true" >
    <RegistrationForm
      :default-invitation-code="defaultInvitationCode"
      @register-success="()=>{showRegistration=false; useUIStateStore().showPopup('Registration successful', 'success')}" 
      @register-fail="useUIStateStore().showPopup($event, 'error')"
    />
  </FloatingWindow>
  <div id="login-main">
    <div id="container">
      <LoginInput/>
      <label for="login" id="info">
        Need assistant? - <a @click="showRegistration=true">Register</a> | <a :href="`mailto:${MAINTAINER.email}`">Contact me</a>
      </label>
    </div>
  </div>
</template>

<style scoped>
#login-main{
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
div#login-main a{
  cursor: pointer;
  padding-inline: 0.5rem;
  border-radius: 0.5rem;
}
</style>