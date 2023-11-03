<script setup lang="ts">
    import Banner from './common/Banner.vue';
    import UserCard from './dashboard/UserCard.vue';
    import { ref, onActivated } from 'vue';
    import { useRoute } from 'vue-router';
    import { ServerConn } from '../core/serverConn';
    import { useUIStateStore } from './store';
    import type { UserInfo } from '../core/protocalT';

    const route = useRoute();
    const conn = new ServerConn();

    const userInfo = ref({
        id: 0,
        username: '',
        enc_key: '',
        name: '',
        is_admin: false,
        mandatory_tags: [],
        has_avatar: false,
    } as UserInfo);

    function updateUser(){
        conn.reqUserInfo(route.params.username as string).then(
            (res) => {
                userInfo.value = res;
            }, 
            (err) => {
                useUIStateStore().showPopup(err, 'error');
            }
        );
    }

    // update user info on load
    onActivated(updateUser);
    window.onhashchange = updateUser;

</script>


<template>
    <div id="main">
        <Banner />
        <UserCard v-model:user-info="userInfo"/>
    </div>
</template>

<style scoped>
    div#main{
        display: flex;
        flex-direction: column;
        margin-top: 20px;
        width: calc(100vw - 20px);
    }
</style>