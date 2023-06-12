import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
const { resolve } = require('path')

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  build:{
    rollupOptions:{
      input:{
        main:resolve(__dirname,'index.html'),
        login:resolve(__dirname,'login.html'),
        feed:resolve(__dirname,'feed.html'),
      }
    }
  }
})