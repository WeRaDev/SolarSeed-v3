<template>
  <div v-if="city.reflection" class="reflection-panel">
    <div class="reflection-header">Spirit Reflection</div>
    <p class="reflection-text">{{ city.reflection.text }}</p>
    <span class="reflection-time">{{ timeAgo }}</span>
  </div>
  <div v-else class="reflection-panel reflection-empty">
    <div class="reflection-header">Spirit Reflection</div>
    <p class="reflection-text">Awaiting first reflection cycle...</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useCityStore } from '../stores/city.js'

const city = useCityStore()

const timeAgo = computed(() => {
  if (!city.reflection?.timestamp) return ''
  const diff = Date.now() - new Date(city.reflection.timestamp).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  return `${Math.floor(mins / 60)}h ago`
})
</script>

<style scoped>
.reflection-panel {
  position: absolute;
  bottom: var(--sp-lg);
  left: var(--sp-lg);
  z-index: 5;
  background: var(--cream-card);
  border: 1px solid var(--gold-border);
  border-radius: var(--radius-lg);
  padding: var(--sp-md);
  max-width: 340px;
  box-shadow: 0 4px 12px var(--gold-shadow);
  animation: fade-in 0.4s ease;
}

.reflection-empty {
  opacity: 0.6;
}

.reflection-header {
  font-size: 12px;
  font-weight: 700;
  color: var(--gold-dark);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: var(--sp-xs);
}

.reflection-text {
  font-size: 13px;
  line-height: 1.5;
  color: var(--charcoal);
}

.reflection-time {
  display: block;
  font-size: 10px;
  color: var(--charcoal-light);
  margin-top: var(--sp-xs);
}
</style>
