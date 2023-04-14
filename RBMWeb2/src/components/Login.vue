

<template>
    <div>
      <form>
        <label for="access-key">Access Key:</label>
        <input type="text" id="access-key" v-model="accessKey" />
        <br />
        <input v-model="stayLogin" type="checkbox" name="stay_login_chk" id="stayLoginChk"/>
        <label for="stay_login_chk">Stay login</label>
        <button type="submit" @click.prevent="login">Login</button>
      </form>
      <p v-if="error" class="error">{{ error }}</p>
    </div>
</template>
  
<script setup lang="ts">
import { ref } from 'vue';
import { ServerConn } from '@/serverConn/serverConn';
import { sha256 } from '@/libs/sha256lib';
import { setCookie } from '@/libs/cookie';
import { STAY_LOGIN_DAYS } from '@/config';
const accessKey = ref("");
const error = ref("");
const stayLogin = ref(false);

let keepTime: null|number = STAY_LOGIN_DAYS;
function login(){
    const encKey = sha256(accessKey.value);
    const conn = new ServerConn();
    conn.authUsr(encKey as string).then(
        (permission) => {
            setCookie("encKey", encKey, keepTime);
            setCookie("accountPermission", permission, keepTime);
            setCookie("keepLogin", stayLogin.value?"1":"0", keepTime);
            console.log("Logged in.")
        },
        (error_) => {
            error.value = error_;
        }
    );
};

</script>

<style>
.error {
color: red;
}
</style>
