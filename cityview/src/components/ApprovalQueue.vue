<template>
  <transition name="slide">
    <aside v-if="city.questPanelOpen" class="quest-panel">
      <div class="panel-header">
        <h3>Approval Quests</h3>
        <button class="close-btn" @click="city.toggleQuestPanel()">&times;</button>
      </div>

      <div v-if="city.pendingApprovals.length === 0" class="empty">
        No pending quests. The City is at peace.
      </div>

      <div
        v-for="(item, i) in city.pendingApprovals"
        :key="i"
        class="quest-card"
        :class="item.severity"
      >
        <div class="quest-severity">{{ item.severity }}</div>
        <div class="quest-action">{{ item.action }}</div>
        <div class="quest-reason">{{ item.reason }}</div>
        <div class="quest-footer">
          <span class="quest-time">{{ formatTime(item.timestamp) }}</span>
          <button class="approve-btn" @click="city.approveAction(i)">Approve</button>
        </div>
      </div>
    </aside>
  </transition>
</template>

<script setup>
import { useCityStore } from '../stores/city.js'

const city = useCityStore()

function formatTime(ts) {
  if (!ts) return ''
  const d = new Date(ts)
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped>
.quest-panel {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 320px;
  background: var(--cream-card);
  border-left: 1px solid var(--gold-border);
  z-index: 20;
  display: flex;
  flex-direction: column;
  box-shadow: -4px 0 16px rgba(0, 0, 0, 0.1);
}

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(100%);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--sp-md);
  border-bottom: 1px solid var(--gold-border);
}

.panel-header h3 {
  font-size: 16px;
  font-weight: 700;
  color: var(--charcoal);
}

.close-btn {
  background: none;
  border: none;
  font-size: 22px;
  cursor: pointer;
  color: var(--charcoal-light);
}

.empty {
  padding: var(--sp-lg);
  text-align: center;
  color: var(--charcoal-light);
  font-size: 13px;
}

.quest-card {
  margin: var(--sp-sm) var(--sp-md);
  padding: var(--sp-md);
  border-radius: var(--radius-md);
  border-left: 4px solid var(--charcoal-light);
  background: white;
}

.quest-card.critical { border-left-color: var(--status-down); }
.quest-card.warning { border-left-color: var(--status-warning); }

.quest-severity {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 2px;
}

.quest-card.critical .quest-severity { color: var(--status-down); }
.quest-card.warning .quest-severity { color: var(--status-warning); }

.quest-action {
  font-size: 14px;
  font-weight: 600;
  color: var(--charcoal);
}

.quest-reason {
  font-size: 12px;
  color: var(--charcoal-light);
  margin-top: 2px;
}

.quest-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--sp-sm);
}

.quest-time {
  font-size: 10px;
  color: var(--charcoal-light);
}

.approve-btn {
  background: var(--gold-primary);
  color: var(--charcoal);
  border: none;
  border-radius: var(--radius-sm);
  padding: 4px 12px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: background 150ms;
}

.approve-btn:hover {
  background: var(--gold-secondary);
}
</style>
