
<script setup lang="ts">
    import { getBackendURL } from '../../config';
    import {useConnectionStore, useDataStore } from '../store';
    import type { UserInfo, Event_User } from '../../api/protocol';
    import { ref, computed, onMounted } from 'vue';
    import { registerServerEvenCallback } from '../../api/serverWebsocketConn';

    import TagBubbleContainer from '../tags/TagBubbleContainer.vue';
    import QueryDialog from '../common/QueryDialog.vue';
    // import Toggle from '../common/Toggle.vue';
    import SwitchToggle from '../settings/SwitchToggle.vue';
    import { useUIStateStore } from '../store';
    import { EditableParagraph } from '../common/fragments';
    import { predefinedUsernames } from '../../config';

    import EditIcon from '../../assets/icons/edit_note.svg'

    const allUsers = ref([] as UserInfo[]);
    const is_admin = computed(() => useDataStore().user.is_admin);
    const conn = useConnectionStore().conn;

    // Edit user related
    const showEditUserDialog = ref(false);
    const editUserDialog_userInfo = ref({} as UserInfo);
    function editUser(userInfo: UserInfo){
        if (!is_admin.value) return;
        const userInfo_copy = JSON.parse(JSON.stringify(userInfo));
        editUserDialog_userInfo.value = userInfo_copy;
        editUserDialog_userInfo.value.max_storage /= 1024*1024;     // convert to MB
        showEditUserDialog.value = true;
    }
    function onEditMandatoryTagsDone(input: string){
        const split_input = input.split(';').map((s:string)=>s.trim());
        if (split_input.length === 1 && split_input[0] === '') editUserDialog_userInfo.value!.mandatory_tags = [];
        else editUserDialog_userInfo.value!.mandatory_tags = split_input;
    }
    function onEditUserOK(){
        console.log(editUserDialog_userInfo.value);
        conn.updateUserAccess(
            editUserDialog_userInfo.value!.username,
            editUserDialog_userInfo.value!.is_admin,
            editUserDialog_userInfo.value!.mandatory_tags, 
            editUserDialog_userInfo.value!.max_storage * 1024*1024
        ).then(
            (_) => { showEditUserDialog.value = false; },
            (err) => { console.log(err); useUIStateStore().showPopup(err, 'error');}
        )
    }

    // Delete user related
    const showDeleteUserDialog = ref(false);
    const deleteUserConfirmInput = ref('');
    function onDeleteUserConfirm(){
        if (deleteUserConfirmInput.value !== editUserDialog_userInfo.value!.username){
            useUIStateStore().showPopup('Wrong input', 'error');
            return;
        }
        conn.deleteUser(editUserDialog_userInfo.value!.username).then(
            (_) => {
                useUIStateStore().showPopup(`User ${editUserDialog_userInfo.value!.username} deleted`, 'info');
                showDeleteUserDialog.value = false;
                showEditUserDialog.value = false;
            },
            (err) => { console.log(err); useUIStateStore().showPopup(err, 'error');}
        )
    }

    // Create user related
    const showCreateUserDialog = ref(false);
    const createUser_username = ref('');
    const createUser_name = ref(predefinedUsernames[Math.floor(Math.random()*predefinedUsernames.length)]);
    const createUser_password = ref('');
    const createUser_isAdmin = ref(false);
    const createUser_mandatoryTags = ref('');
    const createUser_maxStorage = ref(100);
    function closeCreateUserDialog(){
        showCreateUserDialog.value = false;
        // reset the fields
        createUser_username.value = '';
        createUser_name.value = predefinedUsernames[Math.floor(Math.random()*predefinedUsernames.length)];
        createUser_password.value = '';
        createUser_isAdmin.value = false;
        createUser_mandatoryTags.value = '';
    }
    function onConfirmCreateUser(){
        if (createUser_username.value === ''){
            useUIStateStore().showPopup('Please enter the username', 'error');
            return;
        }
        const mandatoryTags = createUser_mandatoryTags.value.split(';').map((s:string)=>s.trim());
        if (mandatoryTags.length === 1 && mandatoryTags[0] === '') mandatoryTags.splice(0, 1);
        conn.createUser(
            createUser_username.value,
            createUser_name.value,
            createUser_password.value,
            createUser_isAdmin.value,
            mandatoryTags,
            createUser_maxStorage.value
        ).then(
            (_) => {
                useUIStateStore().showPopup(`User ${createUser_username.value} created`, 'success');
                closeCreateUserDialog();
            },
            (err) => { console.log(err); useUIStateStore().showPopup(err, 'error');}
        )
    }


    onMounted(() => {
        // get all users
        conn.reqUserList().then(
            (res) => { 
                allUsers.value = res; 
            },
            (err) => { console.log(err); }
        );
    });

    registerServerEvenCallback('add_user', (ev) => {
        const additionalUser = (ev as Event_User).user_info!;
        allUsers.value.push(additionalUser);
    })
    registerServerEvenCallback('update_user', (ev) => {
        const changedUser = (ev as Event_User).user_info!;
        allUsers.value.map((elem, idx)=>{
            if (elem.id === changedUser.id){
                allUsers.value[idx] = changedUser;
            }
        })
    })
    registerServerEvenCallback('delete_user', (ev) => {
        const delUsername = (ev as Event_User).username;
        allUsers.value = allUsers.value.filter(item => item.username !== delUsername)
    })

</script>

<template>
    <div id="users-widget-main">
        <QueryDialog v-model:show="showEditUserDialog" title="editor" 
        @on-accept="onEditUserOK" @on-cancel="()=>showEditUserDialog=false">
            <div id="user-editor-main">
                <div class="horizontal">
                    <img :src="`${getBackendURL()}/user-avatar/${editUserDialog_userInfo.username}?size=128`" alt="" class="avatar-big"/>
                    <div id="user-editor">
                        <div class="horizontal">
                            <h2> {{editUserDialog_userInfo.name}} </h2> ({{editUserDialog_userInfo.username}})
                        </div>
                        <div class="horizonal" style="display: flex; align-items: center; gap: 0.5rem">
                            <b>Administrator </b>
                            <SwitchToggle v-model:checked="editUserDialog_userInfo.is_admin"/>
                        </div>
                        <div class="full-width left-align">
                            <b>Max Storage (MB):</b><br>
                            <input type="number" v-model="editUserDialog_userInfo.max_storage"/>
                        </div>
                        <div class="full-width left-align" v-if="!editUserDialog_userInfo.is_admin">
                            <b>Mandatory Tags:</b>
                            <div id="mandatory-tag-edit">
                                <EditableParagraph :style="{width:'100%'}" :content-editable="!editUserDialog_userInfo.is_admin" @finish="(inp) => onEditMandatoryTagsDone(inp as string)">
                                    {{ editUserDialog_userInfo.mandatory_tags.join('; ')  }}
                                </EditableParagraph>
                            </div>
                        </div>
                    </div>
                </div>
                <input id="delete-user-button" type="button" value="Delete user" @click="()=>{showDeleteUserDialog=true}"/>
            </div>
        </QueryDialog>
        <QueryDialog v-model:show="showDeleteUserDialog" title="Delete user" 
            @on-cancel="()=>{showDeleteUserDialog=false; deleteUserConfirmInput=''}" 
            @on-close="()=>{showDeleteUserDialog=false; deleteUserConfirmInput=''}"
            @on-accept="onDeleteUserConfirm">
            <div id="delete-user-dialog-main">
                <p>
                    Are you sure to delete user <b>{{editUserDialog_userInfo.name}} ({{editUserDialog_userInfo.username}})</b>? 
                    <p style="color:var(--color-danger)">
                        All data under this user will be deleted!
                    </p>
                </p>
                <hr style="margin-block: 1rem;">
                Type <b>{{editUserDialog_userInfo.username}}</b> to confirm:
                <input type="text" id="delete-user-input" v-model="deleteUserConfirmInput" autocomplete="off">
            </div>
        </QueryDialog>
        <QueryDialog v-model:show="showCreateUserDialog" 
        @on-cancel="closeCreateUserDialog" @on-accept="onConfirmCreateUser" @on-close="closeCreateUserDialog">
            <div id="create-user-main">
            <table id="create-user-table">
                <tr>
                    <td>Username:</td>
                    <td><input type="text" v-model="createUser_username" autocomplete="off" class="create-user-input"/></td>
                </tr>
                <tr>
                    <td>Name:</td>
                    <td><input type="text" v-model="createUser_name" autocomplete="off" class="create-user-input"/></td>
                </tr>
                <tr>
                    <td>Password:</td>
                    <td><input type="text" v-model="createUser_password" autocomplete="off" class="create-user-input"/></td>
                </tr>
                <tr>
                    <td>Max Storage (MB):</td>
                    <td><input type="text" v-model="createUser_maxStorage" autocomplete="off" class="create-user-input"/></td>
                </tr>
                <tr>
                    <td>Mandatory Tags:</td>
                    <td><input type="text" v-model="createUser_mandatoryTags" autocomplete="off" class="create-user-input"
                        placeholder="Separate with semicolon ';'" ></td>
                </tr>
                <tr>
                    <td>Administrator:</td>
                    <td style="display: flex; align-items: center; padding-block: 0.25rem;">
                        <SwitchToggle v-model:checked="createUser_isAdmin"></SwitchToggle>
                    </td>
                </tr>
            </table>
            </div>
        </QueryDialog>

        <div id="user-widget-header">
            <div>
                <b> Users </b>
            </div>
            <div v-if="is_admin" id="add-user-div" @click="()=>showCreateUserDialog=true">+</div>
        </div>

        <table>
            <tr>
                <th v-if="is_admin">  </th>
                <th> Avatar </th>
                <th> Username </th>
                <th> Name </th>
                <th> Storage </th>
                <th> Accessibility </th>
            </tr>
            <tr v-for="user in allUsers" class="user-line">
                <!-- <td v-if="is_admin"> {{user.id}} </td> -->
                <td v-if="is_admin"> 
                    <div class="edit-button" @click="()=>editUser(user)">
                        <img :src="EditIcon" alt="" class="icon"/>
                    </div> 
                </td>
                <td> 
                    <div class="center full-width full-height">
                        <img :src="`${getBackendURL()}/user-avatar/${user.username}?size=60`" alt="" class="avatar" /> 
                    </div>
                </td>
                <td class="username"> {{user.username}} </td>
                <td> {{user.name}} </td>
                <td style="text-align: right;"> 
                    {{ 
                    user.max_storage/1024/1024 > 1024 ? 
                    `${(user.max_storage/1024/1024/1024).toFixed(1)} G` : 
                    `${(user.max_storage/1024/1024).toFixed(0)} M`
                    }}
                </td>
                <td>
                    <TagBubbleContainer v-if="!user.is_admin" :tags="user.mandatory_tags" :max-width="200" :middle-align="true"/>
                    <label class=admin_hint v-else>ADMIN</label>
                </td>
            </tr>
            <tr>
                <td colspan="5" v-if="allUsers.length===0"> No users </td>
            </tr>
        </table>
    </div>
</template>

<style scoped>
    div.horizontal{
        display: flex;
        flex-direction: row;
        align-items: center;
        gap: 10px;
    }
    h2{
        /* no new line */
        white-space: nowrap;
    }
    div.center{
        display: flex;
        justify-content: center;
        align-items: center;
    }
    div.full-width{
        width: 100%;
    }
    div.full-height{
        height: 100%;
    }
    div.left-align{
        text-align: left;
    }

    img.avatar{
        width: 32px;
        height: 32px;
        border-radius: 50%;
    }

    label.admin_hint{
        font-size: small;
        font-weight: bold;
        padding-left: 5px;
        padding-right: 5px;
        padding-top: 3px;
        padding-bottom: 3px;
        border-radius: 7px;
        background-color: var(--color-background-theme);
        /* color: var(--color-text-soft); */
        color: var(--color-theme);
    }

    div#user-widget-header{
        display: flex;
        flex-direction: row;
        justify-content: center;
        align-items: center;
        gap: 10px;
    }
    div#user-widget-header b{
        font-weight: bolder;
        font-size: x-large;
    }
    div#add-user-div{
        margin-top: 5px;

        width: 25px;
        height: 25px;
        display: flex;
        justify-content: center;
        align-items: center;
        border-radius: 5px;
        border: 2px solid var(--color-border);
        background-color: var(--color-background-ssoft);
        font-weight: bolder;
        opacity: 30%;
        transition: opacity 0.25s;
        transition-delay: 0.1s;
        cursor: pointer;
    }
    div#add-user-div:hover{
        opacity: 90%;
    }


    table{
        border-collapse: collapse;
    }

    tr.user-line:hover{
        border-radius: 5px;
    }
    tr.user-line:hover{
        background-color: var(--color-background-theme);
    }

    th{
        font-weight: bold;
        text-align: center;
        vertical-align: middle;
        justify-self: center;
        padding-top: 2px;
        padding-bottom: 2px;
        padding-left: 5px;
        padding-right: 5px;
    }

    td{
        text-align: center;
        vertical-align: middle;
        justify-self: center;
        padding-top: 2px;
        padding-bottom: 2px;
        padding-left: 5px;
        padding-right: 5px;
    }
    td.username{
        font-weight: bold;
        font-size: smaller;
        color: var(--color-text-soft);
    }

    b{
        font-weight: bold;
    }

    img.icon {
        height: 20px;
        filter: invert(0.5) opacity(0.75) drop-shadow(0 0 0 var(--color-border)) ;
    }
    div.edit-button{
        border-radius: 30%;
        width: 20px;
        height: 20px;
        cursor: pointer;
        opacity: 30%;
    }
    div.edit-button:hover{
        opacity: 100%;
    }

    div#user-editor-main{
        padding-inline: 2rem;
        padding-block: 1rem;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }
    img.avatar-big{
        width: 128px;
        height: 128px;
        border-radius: 5%;
    }
    div#user-editor{
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }
    div#mandatory-tag-edit{
        padding-left: 5px;
        padding-right: 5px;
        width: 100%;
        border-radius: 8px;
        background-color: var(--color-background);
    }


    div#delete-user-dialog-main{
        padding: 10px;
        padding-inline: 2rem;
    }
    input[type=button]#delete-user-button{
        padding: 5px;
        border-radius: 5px;
        border: 1px solid var(--color-border);
        background-color: var(--color-red-transparent);
        color: var(--color-danger);
        font-weight: bold;
        width: 100%
    }
    input[type=button]#delete-user-button:hover{
        background-color: var(--color-danger-hover);
    }
    input[type=text]#delete-user-input{
        padding: 5px;
        border-radius: 5px;
        border: 1px solid var(--color-border);
    }


    div#create-user-main{
        padding-inline: 1rem;
        padding-block: 0.7rem;
    }
    table#create-user-table{
        width: 100%;
        border-collapse: collapse;
    }
    table#create-user-table tr td{
        text-align: left;
    }
    input[type=text].create-user-input{
        padding: 5px;
        width: 100%;
        background-color: var(--color-background);
        min-width: 200px;
    }

    input[type=number]{
        padding: 5px;
        width: 100%;
        background-color: var(--color-background);
        min-width: 200px;
        border: none;
        color: var(--color-text);
        border-radius: 5px;
    }
</style>