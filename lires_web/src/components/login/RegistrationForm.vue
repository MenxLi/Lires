<template>
    <form @submit="submitForm" id="registration-form">
        <div style="color: var(--color-text-soft); padding-inline: 0.5rem; margin-bottom: 1rem; font-size: small;">
            Get an invitation code from the server administrator
            <div id="show-password-container">
                <SwitchToggle v-model:checked="showPassword" />
                <label>Show password</label>
            </div>
        </div>
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
            <tr>
                <td colspan="2" style="text-align: center; padding: 0px">
                    <button type="submit">REGISTER</button>
                </td>
            </tr>
        </table>
    </form>
</template>

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

<style scoped>
/* Add your custom styles here */

#registration-form {
    margin: 0 auto;
    text-align: left;
}
#registration-form input {
    min-width: 15rem
}
#registration-form input:focus {
    outline: none;
}
#registration-form table{
    border-collapse: collapse;
    width: 100%;
}
#registration-form table td{
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;

    font-weight: bold;
    padding-block: 0.2rem;
    padding-inline: 0.5rem;
    border: 1px solid var(--color-border);
}
#registration-form button{
    width: 100%;
    height: 2.5rem;
    border: none;
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
</style>