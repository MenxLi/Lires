import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
const { resolve } = require('path')

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue(), vueJsx()],
  server: {
    "host": '0.0.0.0'
  },
  build:{
    rollupOptions:{
      input:{
        main:resolve(__dirname,'index.html'),
      }
    }
  }
})