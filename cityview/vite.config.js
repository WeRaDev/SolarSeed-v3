import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Target host: use CITY_HOST env or default to Tailscale IP
const CITY_HOST = process.env.CITY_HOST || '100.82.194.96'
const POLY_ROBOT_HOST = process.env.POLY_ROBOT_HOST || CITY_HOST
const POLY_ROBOT_OPERATOR_TOKEN = process.env.POLY_ROBOT_OPERATOR_TOKEN || ''
const OPERATOR_GATEWAY_HOST = process.env.OPERATOR_GATEWAY_HOST || 'operator-gateway'
const OPERATOR_GATEWAY_PORT = process.env.OPERATOR_GATEWAY_PORT || '8780'

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
      '/poly-robot': {
        target: `http://${OPERATOR_GATEWAY_HOST}:${OPERATOR_GATEWAY_PORT}`,
        changeOrigin: true,
        headers: POLY_ROBOT_OPERATOR_TOKEN
          ? { 'X-Operator-Token': POLY_ROBOT_OPERATOR_TOKEN }
          : {},
        rewrite: (path) => path.replace(/^\/poly-robot/, '/api/v1/access/proxy/poly-robot'),
      },
      '/api': {
        target: `http://${OPERATOR_GATEWAY_HOST}:${OPERATOR_GATEWAY_PORT}`,
        changeOrigin: true,
        headers: POLY_ROBOT_OPERATOR_TOKEN
          ? { 'X-Operator-Token': POLY_ROBOT_OPERATOR_TOKEN }
          : {},
        rewrite: (path) => `/api/v1/access/proxy/poly-robot${path}`,
      },
      '/fortress': {
        target: `http://${CITY_HOST}:8080`,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/fortress/, ''),
      },
      '/university': {
        target: `http://${CITY_HOST}:8081`,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/university/, ''),
      },
      '/house': {
        target: `http://${CITY_HOST}:3000`,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/house/, ''),
      },
      '/operator': {
        target: `http://${OPERATOR_GATEWAY_HOST}:${OPERATOR_GATEWAY_PORT}`,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/operator/, ''),
      },
    },
  },
})
