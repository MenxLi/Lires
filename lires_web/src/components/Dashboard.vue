<script setup lang="ts">
    import Banner from './common/Banner.vue';
    import WidgetContainer from './dashboard/WidgetContainer.vue';
    import UserCard from './dashboard/UserCard.vue';
    import UsersWiget from './dashboard/UsersWidget.vue';
    import { ref, computed, onActivated } from 'vue';
    import { useRoute } from 'vue-router';
    import {useConnectionStore, useUIStateStore, useDataStore } from './store';
    import { registerServerEvenCallback } from '../api/serverWebsocketConn';
    import type { UserInfo, Event_User } from '../api/protocalT';

    const route = useRoute();
    const conn = useConnectionStore().conn;

    const THIS_USER = computed(() => {
        const thisUserId = useDataStore().user.id;
        // console.log("thisUserId", thisUserId, "userId", userInfo.value.id);
        return thisUserId === userInfo.value.id;
    });

    // must use this instead of datastore.user, 
    // because this page may be loaded for a different user
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

    registerServerEvenCallback('update_user', (event)=>{
        if ((event as Event_User).username === userInfo.value.username){ updateUser() }
    })

</script>


<template>
    <Banner />
    <div id="main-dashboard" class="slideIn">
        <WidgetContainer>
            <UserCard :user-info="userInfo"/>
        </WidgetContainer>
        <WidgetContainer>
            <UsersWiget v-if="THIS_USER"/>
        </WidgetContainer>
    </div>
</template>

<style scoped>
    div#main-dashboard{
        margin-top: calc(45px + 20px);
        display: flex;
        align-items: flex-start;
        flex-wrap: wrap;
        justify-content: center;
        flex-direction: row;
        width: calc(100vw - 20px);
        gap: 20px;
    }
</style>../api/serverConn../api/serverWebsocketConn../api/protocalT