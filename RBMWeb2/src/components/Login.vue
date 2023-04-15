
<script setup lang="ts">
import { ref, computed } from 'vue';
import { ServerConn } from '@/serverConn/serverConn';
import { sha256 } from '@/libs/sha256lib';
import { STAY_LOGIN_DAYS, LOCATIONS } from '@/config';
import { saveAuthentication } from '@/core/auth.js'

import Toggle from './common/Toggle.vue'

const accessKey = ref("");
const error = ref("");
const stayLogin = ref(false);
const showPassword = ref(false);
const inputType = computed(() => showPassword.value?"text":"password");

function login(){
    const encKey = sha256(accessKey.value);
    const conn = new ServerConn();
    conn.authUsr(encKey as string).then(
        (permission) => {
            saveAuthentication(encKey as string, permission, stayLogin.value, STAY_LOGIN_DAYS);
            error.value = "";
            console.log("Logged in.")
            // Redirect
            const urlSearchString : string|undefined = window.location.href.split("?")[1];
            console.log(urlSearchString);
            if (urlSearchString === undefined){
                window.location.href = LOCATIONS.main;
            }
            else {
                const params = new URLSearchParams(urlSearchString);
                const redirect = params.get("redirect") as null|"main"|"login";
                if (redirect){
                    window.location.href = LOCATIONS[redirect];
                }
            }
        },
        (error_) => {
            error.value = error_;
        }
    );
};
</script>

<template>
    <div id="login" class="gradIn">
      <form>
        <div class="loginLine">
            <label for="access-key">Access Key:</label>
            <input :type="inputType" id="access-key" v-model="accessKey" />
            <button type="submit" @click.prevent="login">Login</button>
        </div>
        <div class="options">
            <Toggle :checked="stayLogin" @onCheck="(is_checked) => {stayLogin=is_checked}">Stay login</Toggle>
            <Toggle :checked="showPassword" @onCheck="(is_checked) => {showPassword=is_checked}">Show key</Toggle>
        </div>
      </form>
      <p v-if="error" class="error">{{ error }}</p>
    </div>
</template>
  
<style>
.error {
color: red;
}

div#login {
    border: 2px solid var(--color-border);
    border-radius: 15px;
    padding: 15px;
}

div.loginLine{
    margin: 5px;
}

div.options {
    margin: 5px;
    display: flex;
    gap: 10px;
}

</style>
