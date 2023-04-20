import { createApp } from 'vue'
import { createPinia } from 'pinia'
import MainApp from './MainApp.vue'

import './assets/main.css'

const app = createApp(MainApp);
const pinia = createPinia();
app.use(pinia);
app.mount('#app')
