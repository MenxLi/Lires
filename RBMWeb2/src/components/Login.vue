
<script setup lang="ts">
import { ref, computed } from 'vue';
import { ServerConn } from '@/core/serverConn';
import { sha256 } from '@/libs/sha256lib';
import { STAY_LOGIN_DAYS, LOCATIONS } from '@/config';
import { saveAuthentication } from '@/core/auth.js'
import { setCookie } from '@/libs/cookie';

import Toggle from './common/Toggle.vue'

const accessKey = ref("");
const port = ref("8080");
const error = ref("");
const stayLogin = ref(false);
const showPassword = ref(false);
const inputType = computed(() => showPassword.value?"text":"password");
const loginText = ref("Login")

function login(){
    setCookie("backendPort", port.value, STAY_LOGIN_DAYS);
    loginText.value = "Connecting..."

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
            loginText.value = "Login"
        },
        (error_) => {
            error.value = error_;
            loginText.value = "Login"
        }
    );
};
</script>

<template>
    <div class="main">
        <!-- RBMWeb2 login -->
        <div id="login" class="gradIn">
        <form>
            <div class="loginLine">
                <label for="access-key">Access Key </label>
                <input :type="inputType" id="access-key" v-model="accessKey" />
                ::
                <label for="port">Port </label>
                <input type="text" id="port" v-model="port" />
            </div>
            <div class="options">
                <Toggle :checked="stayLogin" @onCheck="(is_checked) => {stayLogin=is_checked}">Stay login</Toggle>
                <Toggle :checked="showPassword" @onCheck="(is_checked) => {showPassword=is_checked}">Show key</Toggle>
            </div>
            <button type="submit" @click.prevent="login">{{ loginText }}</button>
        </form>
        <p v-if="error" class="error">{{ error }}</p>
        </div>
    </div>
</template>
  
<style>
.error {
color: red;
}
div.main{
    text-align: center;
}

div#login {
    border: 2px solid var(--color-border);
    border-radius: 15px;
    padding: 15px;
    text-align: center;
}

div.loginLine{
    margin: 5px;
}

div.options {
    margin: 5px;
    display: flex;
    gap: 10px;
}
button{
    width: 200px
}
#access-key{
    width: 150px
}
#port {
    width: 50px
}

</style>
