<script>
import { useConnectionStore } from '@/state/store';
import SwitchToggle from '../settings/SwitchToggle.vue';
import { predefinedUsernames } from '@/config';
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
            name: predefinedUsernames[Math.floor(Math.random() * predefinedUsernames.length)],
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
        <div id="form-container">

            <div class="form-elem">
                <div style="color: var(--color-text-soft); font-size: smaller; padding-inline: 0.5rem">
                    Get an invitation from the server administrator
                </div>
                <input type="text" v-model="invitationCode" required
                    autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false"
                >
                <span>Invitation code</span>
            </div>

            <div class="form-elem">
                <input type="text" v-model="username" required
                    autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false"
                >
                <span>Username</span>
            </div>

            <div class="form-elem">
                <input :type="`${showPassword ? 'text' : 'password'}`" v-model="password" required
                    autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false"
                >
                <span>Password</span>
            </div>

            <div class="form-elem">
                <input :type="`${showPassword ? 'text' : 'password'}`" v-model="passwordConfirm" required
                    autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false"
                >
                <span>Confirm password</span>
            </div>

            <div class="form-elem">
                <input type="text" v-model="name" required
                    autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false"
                >
                <span>Name</span>
            </div>

        </div>

            <div id="show-password-container">
                <SwitchToggle v-model:checked="showPassword" />
                <label>Show password</label>
            </div>

        <button type="submit">Register</button>
    </form>
</template>


<style scoped>
/* Add your custom styles here */

#registration-form {
    margin: 0 auto;
    text-align: left;
    padding: 1rem;
    padding-inline: 1.5rem;
}
#registration-form button{
    width: 100%;
    height: 2.5rem;
    margin-top: 1rem;
    border-radius: 1.25rem;
    border: 1px solid var(--color-border);
    background-color: var(--color-background-ssoft);
    transition: all 0.3s;
    font-size: medium;
    cursor: pointer;
    box-shadow: 0 2px 3px var(--color-shadow);
}
#registration-form button:hover{
    background-color: var(--color-background-theme);
}
td.horizontal{
    display: flex;
    flex-direction: row;
    gap: 0.5rem;
    align-items: center;
}
#form-container {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.form-elem{
    display: flex;
    flex-direction: column-reverse
}
.form-elem span{
    margin-left: 0.5rem;
    font-size: small;
    color: var(--color-text);
}
.form-elem input {
    font-family: "Gill Sans", sans-serif;
    font-size: medium;
    border-radius: 1rem;
    min-width: 8rem;
    border: 1px solid var(--color-border);
    background-color: var(--color-background);
    transition: all 0.3s;
    padding-inline: 0.5rem;
    height: 2rem;
}
.form-elem input:focus {
    outline: none;
    border: 1px solid var(--color-theme);
}

.form-elem input:focus + span{
    color: var(--color-theme);
}

div#show-password-container{
    margin-top: 0.5rem;
    display: flex;
    flex-direction: row;
    gap: 0.2rem;
    align-items: center;
}

</style>