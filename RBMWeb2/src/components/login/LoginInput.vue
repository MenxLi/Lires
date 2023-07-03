
<script setup lang="ts">
import { ref, computed } from 'vue';
import { ServerConn } from '../../core/serverConn';
import { sha256 } from '../../libs/sha256lib';
import { useRouter } from 'vue-router';
import { saveAuthentication } from '../../core/auth.js'
import { useSettingsStore } from '../store';

import Toggle from '../common/Toggle.vue'

const accessKey = ref("");
const port = ref(useSettingsStore().backendPort);
const error = ref("");
const stayLogin = ref(true);
const showPassword = ref(false);
const inputType = computed(() => showPassword.value?"text":"password");
const loginText = ref("Login")

const router = useRouter();

function login(){
    useSettingsStore().setBackendPort(port.value);

    loginText.value = "Connecting..."

    const encKey = sha256(accessKey.value);
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
                <Toggle :checked="stayLogin" @onCheck="() => {stayLogin=!stayLogin}">Stay login</Toggle>
                <Toggle :checked="showPassword" @onCheck="() => {showPassword=!showPassword}">Show key</Toggle>
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
