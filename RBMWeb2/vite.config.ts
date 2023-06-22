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
    chunkSizeWarningLimit: 1200,
    rollupOptions:{
      input:{
        main:resolve(__dirname,'index.html'),
      },
      output:{
        manualChunks(id) {
            if (id.includes('node_modules')) {
                return id.toString().split('node_modules/')[1].split('/')[0].toString();
            }
        }
      }
    }
  }
})