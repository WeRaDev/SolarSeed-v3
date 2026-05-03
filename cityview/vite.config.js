import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Target host: use CITY_HOST env or default to Tailscale IP
const OPERATOR_GATEWAY_HOST = process.env.OPERATOR_GATEWAY_HOST || 'operator-gateway'
const OPERATOR_GATEWAY_PORT = process.env.OPERATOR_GATEWAY_PORT || '8780'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/spirit': {
        target: `http://${OPERATOR_GATEWAY_HOST}:${OPERATOR_GATEWAY_PORT}`,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/spirit/, '/api/v1/access/proxy/spirit'),
      },
      '/openfang': {
        target: `http://${OPERATOR_GATEWAY_HOST}:${OPERATOR_GATEWAY_PORT}`,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/openfang/, '/api/v1/access/proxy/openfang'),
      },
      '/prometheus': {
        target: `http://${OPERATOR_GATEWAY_HOST}:${OPERATOR_GATEWAY_PORT}`,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/prometheus/, '/api/v1/access/proxy/prometheus'),
      },
      '/poly-robot': {
        target: `http://${OPERATOR_GATEWAY_HOST}:${OPERATOR_GATEWAY_PORT}`,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/poly-robot/, '/api/v1/access/proxy/poly-robot'),
      },
      '/api': {
        target: `http://${OPERATOR_GATEWAY_HOST}:${OPERATOR_GATEWAY_PORT}`,
        changeOrigin: true,
        rewrite: (path) => `/api/v1/access/proxy/poly-robot${path}`,
      },
      '/fortress': {
        target: `http://${OPERATOR_GATEWAY_HOST}:${OPERATOR_GATEWAY_PORT}`,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/fortress/, '/api/v1/access/proxy/fortress'),
      },
      '/university': {
        target: `http://${OPERATOR_GATEWAY_HOST}:${OPERATOR_GATEWAY_PORT}`,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/university/, '/api/v1/access/proxy/university'),
      },
      '/house': {
        target: `http://${OPERATOR_GATEWAY_HOST}:${OPERATOR_GATEWAY_PORT}`,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/house/, '/api/v1/access/proxy/house'),
      },
      '/operator': {
        target: `http://${OPERATOR_GATEWAY_HOST}:${OPERATOR_GATEWAY_PORT}`,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/operator/, ''),
      },
    },
  },
})
