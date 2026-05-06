import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },

  server: {
    watch: {
      usePolling: true, // Esto obliga a Vite a detectar cambios en archivos de Windows desde WSL
    },
    host: true, // Ayuda a que la conexión sea más estable entre WSL y el navegador de Windows
  },
})
