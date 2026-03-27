<template>
  <header class="status-bar">
    <div class="brand">
      <svg class="sun-icon" width="24" height="24" viewBox="0 0 32 32">
        <defs>
          <radialGradient id="sg" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#FFF9E6" />
            <stop offset="100%" stop-color="#C4A000" />
          </radialGradient>
        </defs>
        <circle cx="16" cy="16" r="7" fill="url(#sg)" />
      </svg>
      <span class="title">City of Light</span>
    </div>

    <div class="kpis">
      <div class="kpi" :class="healthClass">
        <span class="kpi-val">{{ city.cityHealth }}</span>
        <span class="kpi-lbl">Health</span>
      </div>
      <div class="kpi">
        <span class="kpi-val">{{ upBuildings }}/{{ totalBuildings }}</span>
        <span class="kpi-lbl">Buildings</span>
      </div>
      <div class="kpi">
        <span class="kpi-val">{{ runningAgents }}</span>
        <span class="kpi-lbl">Agents</span>
      </div>
      <div class="kpi">
        <span class="kpi-val">{{ uptime }}</span>
        <span class="kpi-lbl">Spirit</span>
      </div>
      <div class="kpi" :class="city.soulVerified === true ? 'good' : city.soulVerified === false ? 'crit' : ''">
        <span class="kpi-val">{{ city.soulVerified === true ? 'OK' : city.soulVerified === false ? 'FAIL' : '--' }}</span>
        <span class="kpi-lbl">Soul</span>
      </div>
    </div>

    <button class="quest-btn" @click="city.toggleQuestPanel()">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <polyline points="14 2 14 8 20 8" />
        <line x1="16" y1="13" x2="8" y2="13" />
        <line x1="16" y1="17" x2="8" y2="17" />
      </svg>
      <span v-if="city.approvalCount > 0" class="badge">{{ city.approvalCount }}</span>
    </button>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useCityStore } from '../stores/city.js'

const city = useCityStore()

const upBuildings = computed(() => city.buildings.filter(b => b.health === 'up').length)
const totalBuildings = computed(() => city.buildings.length)
const runningAgents = computed(() => city.agents.filter(a => a.state === 'Running').length)
const uptime = computed(() => {
  const s = city.spiritHealth?.uptime_seconds
  if (!s) return '--'
  if (s < 3600) return `${Math.floor(s / 60)}m`
  return `${Math.floor(s / 3600)}h`
})
const healthClass = computed(() => {
  const h = city.cityHealth
  if (h >= 70) return 'good'
  if (h >= 40) return 'warn'
  return 'crit'
})
</script>

<style scoped>
.status-bar {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--sp-lg);
  background: var(--cream-card);
  border-bottom: 1px solid var(--gold-border);
  z-index: 10;
  flex-shrink: 0;
}

.brand {
  display: flex;
  align-items: center;
  gap: var(--sp-sm);
}

.title {
  font-size: 18px;
  font-weight: 600;
  color: var(--charcoal);
}

.kpis {
  display: flex;
  gap: var(--sp-lg);
}

.kpi {
  text-align: center;
  min-width: 64px;
}

.kpi-val {
  display: block;
  font-size: 20px;
  font-weight: 700;
  line-height: 1.2;
}

.kpi-lbl {
  font-size: 11px;
  color: var(--charcoal-light);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.kpi.good .kpi-val { color: var(--status-up); }
.kpi.warn .kpi-val { color: var(--status-warning); }
.kpi.crit .kpi-val { color: var(--status-down); }

.quest-btn {
  position: relative;
  background: none;
  border: 1px solid var(--gold-border);
  border-radius: var(--radius-md);
  padding: var(--sp-sm);
  cursor: pointer;
  color: var(--charcoal);
  transition: background 150ms;
}

.quest-btn:hover {
  background: var(--gold-highlight);
}

.badge {
  position: absolute;
  top: -6px;
  right: -6px;
  background: var(--status-down);
  color: white;
  font-size: 11px;
  font-weight: 700;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
