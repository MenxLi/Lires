<script setup lang="ts">
import { ref, computed } from 'vue';
import { useConnectionStore } from './store';
const __isDev = import.meta.env.DEV;

const methods = ['get', 'post', 'put', 'delete'] //, 'patch', 'options', 'head']
const httpMethod = ref("post")
const httpDest = ref("")
const fetcher = useConnectionStore().conn.fetcher
const requestEntries = ref([{key: '', value: ''}] as Record<'key'|'value', any>[]);
const requestBody = computed(() => {
    const body: Record<string, any> = {};
    requestEntries.value.forEach(entry => {
        if (!entry.key){return};
        body[entry.key] = entry.value;
    });
    return body;
});
const resText = ref("");

async function sendRequest() {
    if (httpMethod.value && httpDest.value) {
        try {
            let res;
            switch (httpMethod.value) {
                case "get":
                    res = await fetcher.get(httpDest.value, requestBody.value);
                    break;
                case "post":
                    res = await fetcher.post(httpDest.value, requestBody.value);
                    break;
                case "delete":
                    res = await fetcher.delete(httpDest.value, requestBody.value);
                    break;
                case "put":
                    throw new Error("PUT method is not implemented yet");
                // add other methods as necessary
            }
            resText.value = await res?.json();
        } catch (error: any) {
            console.error('HTTP request failed:', error);
            resText.value = error.toString();
        }
    }
}
</script>

<template>
    <div class="test" v-if="__isDev">
        <form @submit.prevent="sendRequest">
            <table>
                <tr>
                    <td> Test API </td>
                    <td>
                        <input type="text" v-model="httpDest" placeholder="/api/xxx"
                        autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false"
                        >
                    </td>
                </tr>

                <tr>
                    <td> HTTP Method </td>
                    <td>
                        <select v-model="httpMethod" style="width: 100%">
                            <option v-for="method in methods" :value="method">
                                {{ method.toUpperCase() }}
                            </option>
                        </select>
                    </td>
                </tr>

                <tr>
                    <td> Request Body </td>
                    <td>
                        <div v-for="(_, index) in requestEntries" :key="index" style="display: flex; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <input type="text" v-model="requestEntries[index].key" placeholder="key"
                            autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false"
                            >
                            <input type="text" v-model="requestEntries[index].value" placeholder="value" style="flex-grow: 1;"
                            autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false"
                            >
                            <a @click.prevent="requestEntries.splice(index, 1)" style="cursor: pointer; padding-inline: 0.5rem; border-radius: 0.5rem;">
                                Remove
                            </a>
                        </div>
                        <button @click.prevent="requestEntries.push({key: '', value: ''})">Add Field</button>
                    </td>

                </tr>

            </table>
            <button type="submit">Send Request</button>
        </form>
        <div style="text-align: left;" v-if="resText">
            <h2 style="font-weight: bold">Response</h2>
            <pre>{{ resText }}</pre>
        </div>
    </div>
    <p v-else>
        Test is not available in production
    </p>
</template>

<style scoped>
div.test{
    margin-top: 1rem;
    font-size: medium;
}
table{
    width: 100%;
    border: 1px solid var(--color-border);
    border-collapse: collapse;
}
td{
    padding: 0.5rem;
    text-align: left;
    border: 1px solid var(--color-border);
}
div.test form{
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}
div.test form label{
    margin-top: 0.5rem;
}
button {
    width: 100%;
    height: 2rem;
}
input, select{
    width: 100%;
    height: 1.8rem;
    border: 1px solid var(--color-border);
}
</style>
