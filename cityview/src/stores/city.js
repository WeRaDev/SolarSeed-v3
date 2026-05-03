import { defineStore } from 'pinia'

// Resolve host for app links: Tailscale IP or env override
const CITY_HOST = window.__CITY_HOST__ || import.meta.env.VITE_CITY_HOST || '100.82.194.96'
const POLY_ROBOT_URL = window.__POLY_ROBOT_URL__ || import.meta.env.VITE_POLY_ROBOT_URL || '/poly-robot/'
const POLY_ROBOT_HEALTH_PATH = window.__POLY_ROBOT_HEALTH_PATH__ || import.meta.env.VITE_POLY_ROBOT_HEALTH_PATH || '/poly-robot/healthz'

// Building definitions: id maps to Spirit building key (from HTTP probes + Prometheus)
// Layout: 7 buildings around Spirit at (480, 300)
const BUILDING_DEFS = [
  { id: 'golden-mine', label: 'Golden Mine', desc: 'Poly-Robot Runtime GUI', jobs: ['poly-robot'], icon: 'factory', x: 480, y: 70, appUrl: POLY_ROBOT_URL, appLabel: 'Open Poly-Robot GUI →', mem: 'n/a', port: 8765 },
  { id: 'agency',     label: 'Agency',      desc: 'OpenFang v0.5 Agent OS',    jobs: ['openfang'],  icon: 'barracks',    x: 340, y: 120, appUrl: `http://${CITY_HOST}:4200`,                       appLabel: 'Open App →',                 mem: '512 MB', port: 4200 },
  { id: 'eventbus',   label: 'Event Bus',   desc: 'Redis 7 Streams',           jobs: ['redis'],     icon: 'tower',       x: 620, y: 120, appUrl: null,                                                     mem: '256 MB', port: 6379 },
  { id: 'library',    label: 'Library',     desc: 'Prometheus + Alertmanager', jobs: ['prometheus'], icon: 'observatory', x: 160, y: 300, appUrl: `http://${CITY_HOST}:9090`,                       appLabel: 'Open App →',                 mem: '512 MB', port: 9090 },
  { id: 'university', label: 'University',  desc: 'llama.cpp (Qwen 3B)',       jobs: ['llama-cpp'], icon: 'dome',        x: 800, y: 300, appUrl: `http://${CITY_HOST}:8081`,                       appLabel: 'Open App →',                 mem: '3 GB',   port: 8081 },
  { id: 'fortress',   label: 'Fortress',    desc: 'Nextcloud AIO',             jobs: ['nextcloud'], icon: 'castle',      x: 340, y: 480, appUrl: `http://${CITY_HOST}:8080`,                       appLabel: 'Open App →',                 mem: '~2 GB',  port: 8080 },
  { id: 'house',      label: 'House',       desc: 'PostgreSQL 16 + Gitea governance', jobs: ['postgres'],  icon: 'house', x: 620, y: 480, appUrl: `http://${CITY_HOST}:3000/admin/house-db-governance`, appLabel: 'Open DB Governance (Gitea) →', mem: '512 MB', port: 5432 },
]
const APPROVAL_TIERS = ['guest', 'external_agent', 'internal_agent', 'admin']

async function fetchJson(url) {
  try {
    const res = await fetch(url)
    if (!res.ok) return null
    return await res.json()
  } catch {
    return null
  }
}

export const useCityStore = defineStore('city', {
  state: () => ({
    // Spirit
    spiritHealth: null,
    spiritStatus: null,
    reflection: null,
    meditation: null,
    pendingApprovals: [],

    // OpenFang
    agents: [],
    openfangOk: false,
    polyRobotOk: false,

    // Prometheus
    targets: [],

    // Soul
    soulVerified: null,

    // UI
    selectedBuildingId: null,
    questPanelOpen: false,
    connectionPanelOpen: false,
    lastPollTime: null,
    pollError: null,

    // Operator gateway connection state
    operatorConnection: null,
    operatorProfile: null,
    operatorBusy: false,
    operatorError: null,
  }),

  getters: {
    buildings(state) {
      const spiritBuildings = state.spiritStatus?.buildings || {}
      const targetMap = {}
      for (const t of state.targets) {
        targetMap[t.labels?.job] = t.health
      }

      return BUILDING_DEFS.map((def) => {
        // Determine health from Spirit status first, Prometheus targets as fallback
        let health = 'unknown'
        for (const job of def.jobs) {
          const spiritState = spiritBuildings[job]
          const promState = targetMap[job]
          if (spiritState === 'up' || promState === 'up') { health = 'up'; break }
          if (spiritState === 'down' || promState === 'down') health = 'down'
        }
        // Special overrides for services without Prometheus scrape targets
        if (def.id === 'agency') {
          health = state.openfangOk ? 'up' : 'down'
        }
        if (def.id === 'golden-mine') {
          health = state.polyRobotOk ? 'up' : 'down'
        }
        // Redis and PostgreSQL have no Prometheus target but Spirit knows them
        // via compose healthchecks -- if Spirit doesn't report them, check compose status
        if (health === 'unknown' && (def.id === 'eventbus' || def.id === 'house')) {
          // These services are healthy if Spirit itself is healthy (they're compose dependencies)
          if (state.spiritHealth?.status === 'healthy') health = 'up'
        }
        return { ...def, health }
      })
    },

    cityHealth(state) {
      const bs = this.buildings
      if (bs.length === 0) return 0
      const up = bs.filter((b) => b.health === 'up').length
      return Math.round((up / bs.length) * 100)
    },

    skyMood(state) {
      const h = this.cityHealth
      if (h >= 70) return 'healthy'
      if (h >= 40) return 'warning'
      return 'critical'
    },

    approvalCount(state) {
      return state.pendingApprovals.length
    },

    connectionState(state) {
      return state.operatorConnection?.state || 'UNKNOWN'
    },

    connectionHealthy(state) {
      return Boolean(state.operatorConnection?.healthy)
    },
  },

  actions: {
    async poll() {
      this.lastPollTime = new Date().toISOString()
      this.pollError = null
      try {
        const [health, status, refl, meditation, agents, targets, polyRobotHealth, operatorConnection] = await Promise.all([
          fetchJson('/spirit/health'),
          fetchJson('/spirit/api/v1/status'),
          fetchJson('/spirit/api/v1/reflection'),
          fetchJson('/spirit/api/v1/meditation'),
          fetchJson('/openfang/api/agents'),
          fetchJson('/prometheus/api/v1/targets'),
          fetchJson(POLY_ROBOT_HEALTH_PATH),
          fetchJson('/operator/api/v1/connection/status'),
        ])

        if (health) this.spiritHealth = health
        if (status) {
          this.spiritStatus = status
          this.pendingApprovals = status.pending_approvals || []
        }
        if (refl) this.reflection = refl.reflection || null
        if (meditation) this.meditation = meditation.meditation || null
        if (agents) {
          // OpenFang v0.5+ returns array or object with agents
          this.agents = Array.isArray(agents) ? agents : (agents.agents || [])
          this.openfangOk = true
        } else {
          this.openfangOk = false
        }
        if (targets) {
          this.targets = targets.data?.activeTargets || []
        }
        if (polyRobotHealth) {
          const status = String(polyRobotHealth.status || '').toLowerCase()
          this.polyRobotOk = status ? ['ok', 'healthy', 'up'].includes(status) : true
        } else {
          this.polyRobotOk = false
        }
        if (operatorConnection) {
          this.operatorConnection = operatorConnection
          this.operatorError = null
        }
      } catch (e) {
        this.pollError = e.message
      }
    },

    selectBuilding(id) {
      this.selectedBuildingId = this.selectedBuildingId === id ? null : id
    },

    toggleQuestPanel() {
      this.questPanelOpen = !this.questPanelOpen
    },

    toggleConnectionPanel() {
      this.connectionPanelOpen = !this.connectionPanelOpen
    },

    async refreshConnectionStatus() {
      const [connection, profile] = await Promise.all([
        fetchJson('/operator/api/v1/connection/status'),
        fetchJson('/operator/api/v1/connection/profile'),
      ])
      if (connection) this.operatorConnection = connection
      if (profile) this.operatorProfile = profile
      if (!connection) this.operatorError = 'Connection status unavailable'
      else this.operatorError = null
    },

    async startConnection() {
      this.operatorBusy = true
      this.operatorError = null
      try {
        const res = await fetch('/operator/api/v1/connection/start', { method: 'POST' })
        if (!res.ok) {
          const text = await res.text()
          throw new Error(text || `Start failed (${res.status})`)
        }
        await this.refreshConnectionStatus()
      } catch (e) {
        this.operatorError = e.message
      } finally {
        this.operatorBusy = false
      }
    },

    async stopConnection() {
      this.operatorBusy = true
      this.operatorError = null
      try {
        const res = await fetch('/operator/api/v1/connection/stop', { method: 'POST' })
        if (!res.ok) {
          const text = await res.text()
          throw new Error(text || `Stop failed (${res.status})`)
        }
        await this.refreshConnectionStatus()
      } catch (e) {
        this.operatorError = e.message
      } finally {
        this.operatorBusy = false
      }
    },

    async approveAction(index) {
      try {
        const res = await fetch('/spirit/approve', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ index }),
        })
        if (res.ok) {
          // Remove from local list optimistically
          this.pendingApprovals.splice(index, 1)
        }
      } catch {
        // next poll will reconcile
      }
    },
  },
})
