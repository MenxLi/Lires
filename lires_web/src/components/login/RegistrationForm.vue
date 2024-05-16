<script>
import { useConnectionStore } from '../store';
import SwitchToggle from '../settings/SwitchToggle.vue';
export default {
    props: {
        defaultInvitationCode: { type: String, default: '' },
    },
    data() {
        return {
            invitationCode: this.defaultInvitationCode,
            username: '',
            password: '',
            passwordConfirm: '',
            name: '',
            showPassword: false
        };
    },
    emits: ['register-success', 'register-fail'],
    components: { SwitchToggle },
    methods: {
        submitForm() {
            // Handle form submission logic here
            // You can access the form data using this.invitationCode, this.username, this.password, this.name
            if (this.password !== this.passwordConfirm) {
                this.$emit('register-fail', 'Passwords do not match');
                return;
            }
            useConnectionStore().conn.registerUser(
                this.invitationCode, this.username, this.password, this.name
            ).then(
                () => { this.$emit('register-success'); },
                (err) => { this.$emit('register-fail', err); }
            )
        }
    }
};
</script>

<template>
    <form @submit="submitForm" id="registration-form">
        <div style="color: var(--color-text-soft); padding-inline: 0.5rem; margin-bottom: 1rem; font-size: small;">
            Get an invitation code from the server administrator
            <div id="show-password-container">
                <SwitchToggle v-model:checked="showPassword" />
                <label>Show password</label>
            </div>
        </div>
        <div id="table-container">
            <table>
                <tr>
                    <td style="color: var(--color-theme)">Invitation Code</td>
                    <td><input type="text" v-model="invitationCode" required
                        autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false"
                        ></td>
                </tr>
                <tr>
                    <td>Username</td>
                    <td><input type="text" v-model="username" required
                        autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false"
                        ></td>
                </tr>
                <tr>
                    <td>Password</td>
                    <td>
                        <div style="display: flex; flex-direction: row;">
                            <input :type="`${showPassword ? 'text' : 'password'}`" v-model="password" required>
                        </div>
                    </td>
                </tr>
                <tr>
                    <td>Confirm Password</td>
                    <td><input :type="`${showPassword ? 'text' : 'password'}`" v-model="passwordConfirm" required></td>
                </tr>
                <tr>
                    <td>Name</td>
                    <td><input type="text" v-model="name" required
                        autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false"
                        ></td>
                </tr>
                <!-- <tr>
                    <td colspan="2" style="text-align: center; padding: 0px; border-top: 1px solid var(--color-border); margin-top: 1rem">
                    </td>
                </tr> -->
            </table>

            <button type="submit">REGISTER</button>
        </div>
    </form>
</template>


<style scoped>
/* Add your custom styles here */

#registration-form {
    margin: 0 auto;
    text-align: left;
    padding: 1rem;
}
#registration-form button{
    width: 100%;
    height: 2.5rem;
    margin-top: 1rem;
    border: none;
    border-top: 1px solid var(--color-border);
    border-radius: 0px;
    font-size: medium;
    font-weight: bold;
    cursor: pointer;
}
td.horizontal{
    display: flex;
    flex-direction: row;
    gap: 0.5rem;
    align-items: center;
}
div#show-password-container{
    display: flex;
    flex-direction: row;
    gap: 0.2rem;
    align-items: center;
}

#table-container {
    padding-top: 1rem;
    border-radius: 20px;
    border: 1px solid var(--color-border);
    overflow: hidden;
    box-shadow: 0 5px 10px 0 var(--color-border);
}
#table-container table{
    border-collapse: collapse;
    /* border-collapse: separate;
    border-spacing: 0; */
    width: 100%;
}
#table-container table td{
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;

    /* font-weight: bold; */
    padding-block: 0.2rem;
    padding-inline: 0.5rem;
}
#table-container input {
    min-width: 15rem;
    border: 1px solid var(--color-border);
    background-color: var(--color-background);
    transition: all 0.3s;
}
#table-container input:focus {
    outline: none;
    border: 1px solid var(--color-theme);
}
</style>