import { defineStore } from 'pinia'

const POLY_ROBOT_HEALTH_PATH = window.__POLY_ROBOT_HEALTH_PATH__ || import.meta.env.VITE_POLY_ROBOT_HEALTH_PATH || '/poly-robot/healthz'

// Building definitions: id maps to Spirit building key (from HTTP probes + Prometheus)
// Layout: 7 buildings around Spirit at (480, 300)
const BUILDING_DEFS = [
  { id: 'golden-mine', label: 'Golden Mine', desc: 'Poly-Robot Runtime GUI', jobs: ['poly-robot'], icon: 'factory', x: 480, y: 70, appUrl: '/poly-robot/', appLabel: 'Open Poly-Robot GUI →', mem: 'n/a', port: 8765 },
  { id: 'agency', label: 'Agency', desc: 'OpenFang v0.5 Agent OS', jobs: ['openfang'], icon: 'barracks', x: 340, y: 120, appUrl: '/openfang/', appLabel: 'Open OpenFang →', mem: '512 MB', port: 4200 },
  { id: 'eventbus', label: 'Event Bus', desc: 'Redis 7 Streams', jobs: ['redis'], icon: 'tower', x: 620, y: 120, appUrl: null, mem: '256 MB', port: 6379 },
  { id: 'library', label: 'Library', desc: 'Prometheus + Alertmanager', jobs: ['prometheus'], icon: 'observatory', x: 160, y: 300, appUrl: '/prometheus/', appLabel: 'Open Prometheus →', mem: '512 MB', port: 9090 },
  { id: 'university', label: 'University', desc: 'llama.cpp (Qwen 3B)', jobs: ['llama-cpp'], icon: 'dome', x: 800, y: 300, appUrl: '/university/', appLabel: 'Open llama.cpp →', mem: '3 GB', port: 8081 },
  { id: 'fortress', label: 'Fortress', desc: 'Nextcloud AIO', jobs: ['nextcloud'], icon: 'castle', x: 340, y: 480, appUrl: '/fortress/', appLabel: 'Open Nextcloud AIO →', mem: '~2 GB', port: 8080 },
  { id: 'house', label: 'House', desc: 'PostgreSQL 16 + Gitea governance', jobs: ['postgres'], icon: 'house', x: 620, y: 480, appUrl: '/house/', appLabel: 'Open Gitea →', mem: '512 MB', port: 5432 },
]

async function fetchJson(url) {
  try {
    const res = await fetch(url, { signal: AbortSignal.timeout(8000) })
    if (!res.ok) return null
    return await res.json()
  } catch {
    return null
  }
}

function toBuildingAccessMap(payload) {
  const map = {}
  for (const item of payload?.buildings || []) {
    if (!item?.id) continue
    map[item.id] = item
  }
  return map
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
    operatorBuildingAccess: {},
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
        const access = state.operatorBuildingAccess[def.id]
        let health = 'unknown'
        for (const job of def.jobs) {
          const spiritState = spiritBuildings[job]
          const promState = targetMap[job]
          if (spiritState === 'up' || promState === 'up') {
            health = 'up'
            break
          }
          if (spiritState === 'down' || promState === 'down') health = 'down'
        }
        if (def.id === 'agency') {
          health = state.openfangOk ? 'up' : 'down'
        }
        if (def.id === 'golden-mine' && !access?.health_hint) {
          health = state.polyRobotOk ? 'up' : 'down'
        }
        if (access?.health_hint === 'up') health = 'up'
        if (access?.health_hint === 'down') health = 'down'
        if (health === 'unknown' && (def.id === 'eventbus' || def.id === 'house')) {
          if (state.spiritHealth?.status === 'healthy') health = 'up'
        }
        return {
          ...def,
          appUrl: access?.app_url !== undefined ? access.app_url : def.appUrl,
          appLabel: access?.app_label || def.appLabel,
          requiresConnection: Boolean(access?.requires_connection),
          health,
        }
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
        const results = await Promise.allSettled([
          fetchJson('/spirit/health'),
          fetchJson('/spirit/api/v1/status'),
          fetchJson('/spirit/api/v1/reflection'),
          fetchJson('/spirit/api/v1/meditation'),
          fetchJson('/openfang/api/agents'),
          fetchJson('/prometheus/api/v1/targets'),
          fetchJson(POLY_ROBOT_HEALTH_PATH),
          fetchJson('/operator/api/v1/connection/status'),
          fetchJson('/operator/api/v1/access/buildings'),
        ])

        const [health, status, refl, meditation, agents, targets, polyRobotHealth, operatorConnection, operatorAccess]
          = results.map(r => r.status === 'fulfilled' ? r.value : null)

        if (health)  this.spiritHealth = health
        if (status) {
          this.spiritStatus = status
          this.pendingApprovals = status.pending_approvals || []
        }
        if (refl)       this.reflection  = refl.reflection  || null
        if (meditation) this.meditation  = meditation.meditation || null
        if (agents) {
          this.agents    = Array.isArray(agents) ? agents : (agents.agents || [])
          this.openfangOk = true
        } else {
          this.openfangOk = false
        }
        if (targets) {
          this.targets = targets.data?.activeTargets || []
        }
        if (operatorConnection) {
          this.operatorConnection = operatorConnection
          this.operatorError = null
        }
        if (operatorAccess) {
          this.operatorBuildingAccess = toBuildingAccessMap(operatorAccess)
        }

        const operatorPolyRobot = operatorConnection?.health_checks?.find(c => c.name === 'poly-robot')
        if (operatorPolyRobot) {
          this.polyRobotOk = Boolean(operatorPolyRobot.ok)
        } else if (polyRobotHealth) {
          const s = String(polyRobotHealth.status || '').toLowerCase()
          this.polyRobotOk = s ? ['ok', 'healthy', 'up'].includes(s) : true
        } else {
          this.polyRobotOk = false
        }
      } catch (e) {
        this.pollError = e.message
      }

      // Demo fallback — show a living city when all APIs are offline
      const allUnknown = this.buildings.every(b => b.health === 'unknown')
      if (allUnknown) {
        this._applyDemoHealth()
      }
    },

    _applyDemoHealth() {
      const BASE = {
        'golden-mine': 84, agency: 91, eventbus: 78,
        library: 88,  university: 76, fortress: 94, house: 82,
      }
      const buildings = {}
      for (const [id, base] of Object.entries(BASE)) {
        const prev = this._demoHealth?.[id] ?? base
        const next = Math.max(10, Math.min(100, prev + (Math.random() * 12 - 6)))
        buildings[id] = next > 35 ? 'up' : 'down'
        if (!this._demoHealth) this._demoHealth = {}
        this._demoHealth[id] = next
      }
      this.spiritStatus = { ...this.spiritStatus, buildings }
      this.openfangOk   = (this._demoHealth.agency ?? 91) > 35
      this.polyRobotOk  = (this._demoHealth['golden-mine'] ?? 84) > 35
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
      const [connection, profile, access] = await Promise.all([
        fetchJson('/operator/api/v1/connection/status'),
        fetchJson('/operator/api/v1/connection/profile'),
        fetchJson('/operator/api/v1/access/buildings'),
      ])
      if (connection) this.operatorConnection = connection
      if (profile)    this.operatorProfile    = profile
      if (access)     this.operatorBuildingAccess = toBuildingAccessMap(access)
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
          this.pendingApprovals.splice(index, 1)
        }
      } catch {
        // next poll will reconcile
      }
    },
  },
})
