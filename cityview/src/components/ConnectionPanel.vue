<template>
  <transition name="slide">
    <aside v-if="city.connectionPanelOpen" class="connection-panel">
      <div class="panel-header">
        <h3>TRL4 Connection</h3>
        <button class="close-btn" @click="city.toggleConnectionPanel()">&times;</button>
      </div>

      <div class="section">
        <div class="row">
          <span class="label">State</span>
          <span class="value" :class="stateClass">{{ city.connectionState }}</span>
        </div>
        <div class="row">
          <span class="label">Healthy</span>
          <span class="value">{{ city.connectionHealthy ? 'Yes' : 'No' }}</span>
        </div>
        <div class="row" v-if="city.operatorProfile">
          <span class="label">Profile</span>
          <span class="value">{{ city.operatorProfile.name }}</span>
        </div>
      </div>

      <div class="actions">
        <button class="btn primary" :disabled="city.operatorBusy" @click="city.startConnection()">
          {{ city.operatorBusy ? 'Starting…' : 'Start' }}
        </button>
        <button class="btn danger" :disabled="city.operatorBusy" @click="city.stopConnection()">
          {{ city.operatorBusy ? 'Stopping…' : 'Stop' }}
        </button>
        <button class="btn" :disabled="city.operatorBusy" @click="city.refreshConnectionStatus()">
          Refresh
        </button>
      </div>

      <div class="section">
        <h4>Forwards</h4>
        <div v-if="!forwards.length" class="muted">No forwards configured.</div>
        <div v-for="f in forwards" :key="f.name + f.local_port" class="item">
          <div class="name">{{ f.name }}</div>
          <div class="meta">localhost:{{ f.local_port }} → {{ f.remote_host }}:{{ f.remote_port }}</div>
          <div class="status" :class="f.listening ? 'up' : 'down'">{{ f.listening ? 'LISTENING' : 'DOWN' }}</div>
        </div>
      </div>

      <div class="section">
        <h4>Health Checks</h4>
        <div v-if="!checks.length" class="muted">No checks configured.</div>
        <div v-for="c in checks" :key="c.name + c.url" class="item">
          <div class="name">{{ c.name }}</div>
          <div class="meta">{{ c.url }}</div>
          <div class="status" :class="c.ok ? 'up' : 'down'">{{ c.ok ? 'OK' : 'FAIL' }}</div>
        </div>
      </div>

      <p v-if="city.operatorError" class="error">{{ city.operatorError }}</p>
    </aside>
  </transition>
</template>

<script setup>
import { computed } from 'vue'
import { useCityStore } from '../stores/city.js'

const city = useCityStore()

const forwards = computed(() => city.operatorConnection?.forwards || [])
const checks = computed(() => city.operatorConnection?.health_checks || [])
const stateClass = computed(() => {
  const state = city.connectionState
  if (state === 'CONNECTED') return 'up'
  if (state === 'DEGRADED') return 'warn'
  return 'down'
})
</script>

<style scoped>
.connection-panel {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  width: 360px;
  background: var(--cream-card);
  border-right: 1px solid var(--gold-border);
  z-index: 25;
  display: flex;
  flex-direction: column;
  padding: var(--sp-md);
  gap: var(--sp-sm);
  overflow-y: auto;
}

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.25s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(-100%);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h3 {
  font-size: 16px;
  font-weight: 700;
}

.close-btn {
  background: none;
  border: none;
  font-size: 22px;
  cursor: pointer;
  color: var(--charcoal-light);
}

.section {
  background: white;
  border: 1px solid var(--gold-border);
  border-radius: var(--radius-md);
  padding: var(--sp-sm);
}

.row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  margin-bottom: 4px;
}

.label {
  color: var(--charcoal-light);
}

.value {
  font-weight: 600;
}

.actions {
  display: flex;
  gap: var(--sp-xs);
}

.btn {
  border: 1px solid var(--gold-border);
  background: white;
  border-radius: var(--radius-sm);
  padding: 6px 10px;
  font-size: 12px;
  cursor: pointer;
}

.btn:disabled {
  opacity: 0.5;
  cursor: default;
}

.btn.primary {
  background: var(--gold-primary);
  border-color: var(--gold-primary);
}

.btn.danger {
  color: var(--status-down);
}

.item {
  border-top: 1px dashed var(--gold-border);
  padding-top: 6px;
  margin-top: 6px;
}

.name {
  font-weight: 600;
  font-size: 12px;
}

.meta {
  font-size: 11px;
  color: var(--charcoal-light);
}

.status {
  margin-top: 2px;
  font-size: 11px;
  font-weight: 700;
}

.status.up {
  color: var(--status-up);
}

.status.warn {
  color: var(--status-warning);
}

.status.down {
  color: var(--status-down);
}

.muted {
  font-size: 12px;
  color: var(--charcoal-light);
}

.error {
  color: var(--status-down);
  font-size: 12px;
  line-height: 1.4;
}
</style>
