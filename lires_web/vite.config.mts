import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue(), vueJsx()],
  server: {
    "host": '0.0.0.0',
    port: 1420,
    strictPort: true,
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  build:{
    chunkSizeWarningLimit: 1600,
    rollupOptions: {
      output:{
        manualChunks(id) {
          if (id.includes('node_modules')) {
              return id.toString().split('node_modules/')[1].split('/')[0].toString();
          }
        }
      }
    }
  },
  clearScreen: false,
  envPrefix: ["VITE_"],
})