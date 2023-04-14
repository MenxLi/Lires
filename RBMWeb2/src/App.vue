<script setup lang="ts">

import {ServerConn} from "./serverConn/serverConn.js"
const conn = new ServerConn();
conn.authUsr("xxx", {
  onFailure: function(err) {console.log(err);}
})

</script>

<template>

</template>