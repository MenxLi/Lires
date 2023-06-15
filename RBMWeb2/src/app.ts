// To replace other pages (except login) using routing


import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHashHistory } from 'vue-router'
import App from './App.vue'
import './assets/main.css'

import Home from './components/Home.vue';
import Feed from './components/Feed.vue';
import Login from './components/Login.vue';
import Reader from './components/Reader.vue';

const routes = [
  { path: '/', component: Home },
  { path: '/feed', component: Feed },
  { path: '/login', component: Login },
  { path: '/reader/:id', component: Reader },
]
const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

const pinia = createPinia();

const app = createApp(App);
app.use(pinia);
app.use(router)
app.mount('#app')
