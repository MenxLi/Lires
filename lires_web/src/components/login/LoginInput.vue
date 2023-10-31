
<script setup lang="ts">
import { ref, computed } from 'vue';
import { ServerConn } from '../../core/serverConn';
import { sha256 } from '../../libs/sha256lib';
import { useRouter } from 'vue-router';
import { saveAuthentication } from '../../core/auth.js'
import { useSettingsStore } from '../store';

import Toggle from '../common/Toggle.vue'

const username = ref("");
const password = ref("");
const error = ref("");
const stayLogin = ref(true);
const showPassword = ref(false);
const pwdInputType = computed(() => showPassword.value?"text":"password");
const loginText = ref("Login")

const backendUrl = ref(useSettingsStore().backendUrl);
const port = ref(useSettingsStore().backendPort);
const router = useRouter();

function login(){
    useSettingsStore().setBackendUrl(backendUrl.value);
    useSettingsStore().setBackendPort(port.value);

    loginText.value = "Connecting..."

    const encKey = sha256(username.value + password.value);
    const conn = new ServerConn();
    conn.authUsr(encKey as string).then(
        (permission) => {
            saveAuthentication(encKey as string, permission, stayLogin.value);
            error.value = "";
            const urlFrom = router.currentRoute.value.query.from;
            if (!urlFrom){
                router.push("/");
            }
            else {
                console.log("Redirecting to", urlFrom);
                router.push(urlFrom as string);
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
        <div id="login" class="slideIn">
        <form>
            <div class="loginLine">
                <!-- <label for="username-input">Username: </label> -->
                <input class='key-input' type="text" id="username-input" v-model="username" placeholder="Username"/>
            </div>
            <div class="loginLine">
                <!-- <label for="password-input">Password: </label> -->
                <input class="key-input" :type="pwdInputType" id="password-input" v-model="password" placeholder="Password"/>
            </div>
            <details>
                <summary>Settings</summary>
                <div id="settings">
                    <label for="backendUrl">Backend: </label>
                    <input type="text" id="backendUrl" v-model="backendUrl" />
                    :
                    <input type="text" id="port" v-model="port" />
                    <div class="options">
                        <Toggle :checked="stayLogin" @onCheck="() => {stayLogin=!stayLogin}">Stay login</Toggle>
                        <Toggle :checked="showPassword" @onCheck="() => {showPassword=!showPassword}">Show key</Toggle>
                    </div>
                </div>
            </details>
            <button type="submit" @click.prevent="login">{{ loginText }}</button>
        </form>
        <p v-if="error" class="error">{{ error }}</p>
        </div>
    </div>
</template>
  
<style scoped>
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
    background-color: var(--color-background-ssoft);
}

input[type="text"],input[type="password"]{
    background-color: var(--color-background);
    font-family: 'Courier New', Courier, monospace;
    font-weight: bold;
}

div.loginLine{
    margin: 5px;
}

div.loginLine label{
    font-weight: bold;
}

div.options {
    margin: 5px;
    display: flex;
    gap: 10px;
}
button{
    width: 200px
}
input.key-input {
    width: 275px
}

details{
    padding: 5px;
}
div#settings{
    border-radius: 5px;
    background-color: var(--color-background-mute);
    padding: 5px;
}
details summary{
    text-align: left;
}
details input{
    width: 160px;
}
#port {
    display: inline-block;
    width: 50px
}

</style>
