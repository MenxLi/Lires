import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Home from './components/Home.vue'

import './assets/main.css'

const app = createApp(Home);
const pinia = createPinia();
app.use(pinia);
app.mount('#app')
