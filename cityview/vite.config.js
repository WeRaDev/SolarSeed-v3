import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Target host: use CITY_HOST env or default to Tailscale IP
const CITY_HOST = process.env.CITY_HOST || '100.82.194.96'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/spirit': {
        target: `http://${CITY_HOST}:9105`,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/spirit/, ''),
      },
      '/openfang': {
        target: `http://${CITY_HOST}:4200`,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/openfang/, ''),
      },
      '/prometheus': {
        target: `http://${CITY_HOST}:9090`,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/prometheus/, ''),
      },
    },
  },
})
