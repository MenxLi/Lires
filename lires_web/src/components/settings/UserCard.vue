
<script setup lang="ts">
    import type { UserInfo } from '../../api/protocol';
    import {useConnectionStore, useSettingsStore, useUIStateStore, useDataStore } from '../store';
    import { ref, computed } from 'vue';
    import { CircularImage, FileSelectButton } from '../common/fragments.tsx';
    import { getBackendURL } from '../../config';
    import { sha256 } from '../../utils/sha256lib';
    import { copyToClipboard } from '../../utils/misc';

    import QueryDialog from '../common/QueryDialog.vue';
    import EditSquareIcon from '../../assets/icons/edit_square.svg'
    import DiskUsage from './DiskUsage.vue';

    const props = withDefaults(defineProps<{
        userInfo: UserInfo;
        avatarSize?: string;
    }>(), {
        avatarSize: '168px',
    });

    const conn = useConnectionStore().conn;

    const emit = defineEmits<{
        (e: "update:userInfo", userInfo: UserInfo): void
    }>()

    // Indicate whether this user is the current user
    // must use computed to make it avaliable when the page is reloaded
    const THIS_USER = computed(() => useDataStore().user.id === props.userInfo.id)

    const avatarUploadBtn = ref(null as HTMLInputElement | null);
    const avatarURL = ref(getAvatarURL());
    function getAvatarURL(){
        return `${getBackendURL()}/user-avatar/${props.userInfo.username}?t=${Date.now()}&size=256`
    }
    function onUploadAvatarImage(file: File){
        // check if the file is an image
        if(!file.type.startsWith('image/')){
            useUIStateStore().showPopup('Please select an image file', 'error');
            return;
        }
        useUIStateStore().showPopup('Uploading avatar...');
        conn.uploadUserAvatar( props.userInfo.username, file).then(
            (new_userInfo: UserInfo) => {
                avatarURL.value = getAvatarURL();
                emit("update:userInfo", new_userInfo);
            },
            (err) => { useUIStateStore().showPopup(err, 'error'); }
        )
    }


    const showUserSettingsDialog = ref(false);
    const settings_nickname = ref("");
    const settings_oldPassword = ref("");
    const settings_newPassword = ref("");
    const settings_confirmNewPassword = ref("");
    function onConfirmUserSettings(){
        // maybe update the name
        if (!(settings_nickname.value === "" || settings_nickname.value === props.userInfo.name)){
            if (settings_nickname.value !== props.userInfo.name){
                conn.updateUserNickname(settings_nickname.value).then(
                    (new_userInfo: UserInfo) => {
                        emit("update:userInfo", new_userInfo);
                        showUserSettingsDialog.value = false;
                    },
                    (err) => { useUIStateStore().showPopup(err, 'error'); }
                )
            }
        }

        // maybe update the password
        if (settings_newPassword.value !== "" || settings_confirmNewPassword.value !== ""){
            // check completeness
            if (settings_newPassword.value === ""){
                useUIStateStore().showPopup("Please enter the new password", "error");
                return;
            }
            if (settings_newPassword.value !== settings_confirmNewPassword.value){
                useUIStateStore().showPopup("The new passwords do not match", "error");
                return;
            }

            // update the password
            if (useSettingsStore().encKey !== sha256(props.userInfo.username + sha256(settings_oldPassword.value))){
                useUIStateStore().showPopup("The old password is incorrect", "error");
                return;
            }
            conn.updateUserPassword(settings_newPassword.value).then(
                (_: UserInfo) => {
                    const new_encKey = sha256(props.userInfo.username + sha256(settings_newPassword.value)) as string;
                    useSettingsStore().setEncKey(new_encKey);
                    // clear the password fields
                    settings_oldPassword.value = "";
                    settings_newPassword.value = "";
                    settings_confirmNewPassword.value = "";
                    showUserSettingsDialog.value = false;
                },
                (err) => { useUIStateStore().showPopup(err, 'error'); }
            )
        }
    }


</script>

<template>

    <div id="usercard-main">
        <QueryDialog v-model:show="showUserSettingsDialog" title="User settings"
        @on-cancel="showUserSettingsDialog=false" @on-accept="onConfirmUserSettings">
            <div id="user-settings">
                <b>{{ props.userInfo.username }}</b>
                <input type="text" v-model="settings_nickname" placeholder="Nickname" class="input"/>
                <hr>
                <details>
                    <summary>Change password</summary>
                    <div id="password-container">
                        <input type="password" v-model="settings_oldPassword" placeholder="Old password" class="input"/>
                        <input type="password" v-model="settings_newPassword" placeholder="New password" class="input"/>
                        <input type="password" v-model="settings_confirmNewPassword" placeholder="Confirm new password" class="input"/>
                    </div>
                </details>
            </div>
        </QueryDialog>

        <div id="info">
            <div id="avatar" :style="THIS_USER?{'cursor':'pointer', 'borderRadius': '50%'}:{}">
                <CircularImage :href="avatarURL" :size="avatarSize" @click="THIS_USER?avatarUploadBtn?.click():()=>{}"/>
                <FileSelectButton :text="'Change avatar'" :action="onUploadAvatarImage" ref="avatarUploadBtn" :style="{'display': 'none'}"/>
            </div>
            <div id="user-desc">
                <div id="name-edit">
                    <h1 id="name">{{ props.userInfo.name }}</h1>
                    <img v-if="THIS_USER" :src="EditSquareIcon" alt="" class="icon" id="edit-settings-icon" @click="showUserSettingsDialog=true">
                </div>
                <p @click="showUserSettingsDialog=true" style="cursor: pointer;">
                    {{ props.userInfo.username}} <label class='admin_hint' v-if="props.userInfo.is_admin">admin</label>
                </p>
                <!-- <p id="backendurl">{{ getBackendURL() }}</p> -->
                <DiskUsage></DiskUsage>
                <div style="height: 0.2rem;"></div>
                <!-- <p id="credential" @click="()=>{copyToClipboard(useSettingsStore().encKey).then(
                    ()=>{useUIStateStore().showPopup('Secret copied to clipboard', 'info')})
                }">Credential:{{ useSettingsStore().encKey.substring(0, 8)}}</p> -->
            </div>
        </div>
        <p id="credential" @click="()=>{copyToClipboard(useSettingsStore().encKey).then(
            ()=>{useUIStateStore().showPopup('Secret copied to clipboard', 'info')})
        }">-- Credential:{{ useSettingsStore().encKey.substring(0, 12)}} --</p>
    </div>
</template>

<style scoped>
    /* div{
        border: 1px solid red;
    } */
    div#usercard-main{
        margin-top: 10px;
        display: flex;
        align-items: center;
        flex-direction: column;
        gap: 0.5rem;
        width: 100%;
    }
    div#info{
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: row;
        gap: 20px;
    }
    label.admin_hint{
        font-size: x-small;
        padding-left: 5px;
        padding-right: 5px;
        height: 12px;
        border-radius: 5px;
        background-color: var(--color-background-theme);
        /* color: var(--color-text-soft); */
        color: var(--color-theme);
    }
    div#info div#name-edit{
        display: flex;
        flex-direction: row;
        align-items: center;
        gap: 10px;
    }
    div#info div#user-desc{
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        justify-self: flex-start;
    }
    /* @media only screen and (max-width: 767px) {
        div#info{
            flex-direction: column;
            align-items: center;
            gap: 10px;
        }
        div#info div#user-desc{
            align-items: center;
        }
        img#edit-settings-icon{
            display: none;
        }
    } */
    p#credential{
        font-family: monospace;
        color: var(--color-text-soft);
        cursor: pointer;
        font-size: 0.75rem;
    }
    h1{
        font-weight: bold;
    }

    img.icon {
        height: 25px;
        filter: invert(0.5) opacity(0.75) drop-shadow(0 0 0 var(--color-border)) ;
    }
    img#edit-settings-icon{
        padding-top: 8px;
        opacity: 0;
        transition: all 0.2s ease-in-out;
    }
    img#edit-settings-icon:hover{
        cursor: pointer;
    }
    div#name-edit:hover img#edit-settings-icon{
        opacity: 1;
    }

    div#user-settings{
        margin: 10px;
        margin-top: 0px;
        display: flex;
        flex-direction: column;
        text-align: left;
    }
    div#user-settings 
    hr{
        margin: 0px;
        padding: 0px;
    }
    div#user-settings 
    b{
        font-weight: bold;
    }
    div#user-settings input[type=text]{
        width: 300px;
        background-color: var(--color-background);
        height: 36px;
    }
    div#user-settings details summary{
        margin-top: 5px;
        text-align: left;
        font-size: smaller;
    }
    div#password-container{
        display: flex;
        flex-direction: column;
        gap: 5px;
    }
    div#password-container input[type=password]{
        width: 300px;
        background-color: var(--color-background);
    }
</style>