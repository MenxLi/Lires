<script setup lang="ts">
    import Banner from './common/Banner.vue';
    import UserCard from './dashboard/UserCard.vue';
    import UsersWiget from './dashboard/UsersWidget.vue';
    import { ref, computed, onActivated } from 'vue';
    import { useRoute } from 'vue-router';
    import { ServerConn } from '../core/serverConn';
    import { useUIStateStore, useSettingsStore } from './store';
    import type { UserInfo } from '../core/protocalT';

    const route = useRoute();
    const conn = new ServerConn();

    const THIS_USER = computed(() => {
        const thisUserId = useSettingsStore().userInfo?useSettingsStore().userInfo!.id:-1;
        console.log(thisUserId, userInfo.value.id);
        return thisUserId === userInfo.value.id;
    });

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
    <Banner />
    <div id="main-dashboard">
        <UserCard v-model:user-info="userInfo"/>
        <UsersWiget v-if="THIS_USER"/>
    </div>
</template>

<style scoped>
    div#main-dashboard{
        margin-top: 45px;
        display: flex;
        align-items: center;
        flex-direction: column;
        width: calc(100vw - 20px);
        gap: 50px;
    }
</style>