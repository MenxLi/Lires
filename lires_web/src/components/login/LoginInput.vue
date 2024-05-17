
<script setup lang="ts">
import { ref, computed, nextTick } from 'vue';
import { useConnectionStore } from '@/state/store';
import { useRouter } from 'vue-router';
import { saveAuthentication, getEncKey } from '../../core/auth.js'
import { useSettingsStore } from '@/state/store';

import Toggle from '../common/Toggle.vue'

const username = ref("");
const password = ref("");
const error = ref("");
const stayLogin = ref(true);
const showPassword = ref(false);
const pwdInputType = computed(() => showPassword.value?"text":"password");
const loginText = ref("Login")

const router = useRouter();
const backendHost = ref("");
const backendPort = ref("");
router.isReady().then(()=>{
    // set backend host and port from settings
    // the settings may be set from url query in App.vue in the first place,
    // so we need to wait until the router is ready and set the settings
    nextTick(()=>{
        backendHost.value = useSettingsStore().backendHost;
        backendPort.value = useSettingsStore().backendPort;
    })
})


function login(){
    useSettingsStore().setBackendHost(backendHost.value);
    useSettingsStore().setBackendPort(backendPort.value);

    loginText.value = "Connecting..."

    const conn = useConnectionStore().conn;

    // temporary save the key, for auth user to use
    const encKey = getEncKey(username.value, password.value);
    useSettingsStore().setEncKey(encKey, false);

    conn.authorize().then(
        (userInfo) => {
            saveAuthentication(encKey as string, userInfo, stayLogin.value);
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
                <input class='key-input' type="text" id="username-input" v-model="username" placeholder="Username" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false"/>
            </div>
            <div class="loginLine">
                <!-- <label for="password-input">Password: </label> -->
                <input class="key-input" :type="pwdInputType" id="password-input" v-model="password" placeholder="Password"/>
            </div>
            <div class="options">
                <Toggle :checked="stayLogin" @onCheck="() => {stayLogin=!stayLogin}">Stay login</Toggle>
                <Toggle :checked="showPassword" @onCheck="() => {showPassword=!showPassword}">Show key</Toggle>
            </div>

            <!-- to be removed -->
            <details v-if="false">
                <summary>Settings</summary>
                <div id="settings">
                    <label for="backendHostInput">Backend: </label>
                    <input type="text" id="backendHostInput" v-model="backendHost" />
                    :
                    <input type="text" id="port" v-model="backendPort" />
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
    border: 1px solid var(--color-border);
    box-shadow: 0px 3px 5px var(--color-shadow);
    border-radius: 15px;
    padding: 15px;
    text-align: center;
    background-color: var(--color-background-ssoft);
    margin-bottom: 0.5rem;
}

input[type="text"],input[type="password"]{
    font-family: "Gill Sans", sans-serif;
    font-size: medium;
    border-radius: 1rem;
    min-width: 8rem;
    border: 1px solid var(--color-border);
    background-color: var(--color-background);
    transition: all 0.3s;
    padding-inline: .8rem;
    height: 2rem;
}
input:focus{
    outline: none;
    border: 1px solid var(--color-theme);
}

div.loginLine{
    margin-top: 0.5rem;
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
    width: 100%;
    margin-top: 0.5rem;
    border-radius: 1rem;
    height: 2rem;
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