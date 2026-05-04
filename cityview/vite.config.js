import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { existsSync } from 'node:fs'

const runningInDocker = existsSync('/.dockerenv')
const OPERATOR_GATEWAY_HOST = process.env.OPERATOR_GATEWAY_HOST || (runningInDocker ? 'operator-gateway' : '127.0.0.1')
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
        ws: true,
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
      '/api/control': {
        target: `http://${OPERATOR_GATEWAY_HOST}:${OPERATOR_GATEWAY_PORT}`,
        changeOrigin: true,
        rewrite: (path) => `/api/v1/access/proxy/poly-robot${path}`,
      },
      '/api/dashboard': {
        target: `http://${OPERATOR_GATEWAY_HOST}:${OPERATOR_GATEWAY_PORT}`,
        changeOrigin: true,
        rewrite: (path) => `/api/v1/access/proxy/poly-robot${path}`,
      },
      '/api': {
        target: `http://${OPERATOR_GATEWAY_HOST}:${OPERATOR_GATEWAY_PORT}`,
        changeOrigin: true,
        ws: true,
        rewrite: (path) => `/api/v1/access/proxy/openfang${path}`,
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
