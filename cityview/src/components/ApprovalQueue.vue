<template>
  <Transition name="fade">
    <div v-if="city.questPanelOpen" class="approval-queue" role="dialog" aria-modal="true" aria-label="Approval queue">
      <div class="queue-header">
        <span class="queue-title">Pending Approvals</span>
        <button class="close-btn" @click="city.toggleQuestPanel()" aria-label="Close">✕</button>
      </div>

      <div class="queue-body">
        <div v-if="city.pendingApprovals.length === 0" class="queue-empty">
          No pending approvals — the city is at peace.
        </div>
        <div
          v-for="(approval, i) in city.pendingApprovals"
          :key="i"
          class="approval-item"
        >
          <div class="approval-text">{{ approval.description || approval.action || JSON.stringify(approval) }}</div>
          <button class="approve-btn" @click="city.approveAction(i)">Approve</button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { useCityStore } from '../stores/city.js'
const city = useCityStore()
</script>

<style scoped>
.approval-queue {
  position: fixed;
  right: var(--sp-lg);
  top: 72px;
  width: 340px;
  max-height: 60vh;
  display: flex;
  flex-direction: column;
  background: rgba(253, 240, 216, 0.94);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid var(--gold-border);
  border-radius: var(--radius-lg);
  box-shadow: 0 8px 32px var(--navy-shadow);
  z-index: 15;
  animation: fade-in 0.2s ease;
}

.queue-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--sp-md) var(--sp-lg);
  border-bottom: 1px solid var(--gold-border);
  flex-shrink: 0;
}

.queue-title {
  font-family: var(--font-display);
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1.2px;
  color: var(--brand-navy);
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  color: var(--brand-navy-muted);
}
.close-btn:hover { color: var(--brand-navy); }

.queue-body {
  overflow-y: auto;
  padding: var(--sp-md) var(--sp-lg);
  display: flex;
  flex-direction: column;
  gap: var(--sp-sm);
}

.queue-empty {
  font-size: 13px;
  color: var(--brand-navy-muted);
  font-style: italic;
  text-align: center;
  padding: var(--sp-md) 0;
}

.approval-item {
  display: flex;
  align-items: flex-start;
  gap: var(--sp-sm);
  padding: var(--sp-sm);
  background: rgba(255,255,255,0.5);
  border-radius: var(--radius-md);
  border: 1px solid var(--gold-border);
}

.approval-text {
  flex: 1;
  font-size: 12px;
  color: var(--brand-navy);
  line-height: 1.45;
}

.approve-btn {
  flex-shrink: 0;
  background: var(--brand-green);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
}
.approve-btn:hover { background: var(--brand-green-mid); }

.fade-enter-active, .fade-leave-active { transition: opacity 0.2s, transform 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-8px); }
</style>
