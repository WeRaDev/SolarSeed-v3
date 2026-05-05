<template>
  <div
    class="reflection-panel"
    :class="{ 'is-fresh': isFresh, 'is-empty': !city.reflection }"
    role="region"
    aria-live="polite"
    aria-label="Spirit Reflection"
  >
    <div class="reflection-header">
      <span class="live-dot" :class="{ pulse: isFresh && city.reflection }" aria-hidden="true" />
      Spirit Reflection
    </div>

    <p class="reflection-text">
      {{ city.reflection ? city.reflection.text : 'Awaiting first reflection cycle…' }}
    </p>

    <div v-if="city.reflection" class="reflection-footer">
      <span class="reflection-time">{{ timeAgo }}</span>
      <span v-if="city.reflection.category" class="reflection-tag">
        {{ city.reflection.category }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useCityStore } from '../stores/city.js'

const city = useCityStore()
const isFresh = ref(false)
let freshTimer = null

const timeAgo = computed(() => {
  if (!city.reflection?.timestamp) return ''
  const diff = Date.now() - new Date(city.reflection.timestamp).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  return `${Math.floor(mins / 60)}h ago`
})

watch(
  () => city.reflection?.timestamp,
  () => {
    isFresh.value = true
    clearTimeout(freshTimer)
    freshTimer = setTimeout(() => { isFresh.value = false }, 5000)
  },
  { immediate: true }
)
</script>

<style scoped>
.reflection-panel {
  position: absolute;
  bottom: var(--sp-lg);
  left: var(--sp-lg);
  z-index: 5;

  background: rgba(253, 240, 216, 0.72);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);

  border: 1px solid rgba(242, 176, 53, 0.40);
  border-radius: var(--radius-lg);
  padding: var(--sp-md);
  max-width: 340px;

  box-shadow:
    0 8px 24px rgba(242, 176, 53, 0.16),
    inset 0 1px 0 rgba(255, 255, 255, 0.55);

  animation: fade-in 0.4s ease;
  transition: box-shadow 0.5s ease, border-color 0.5s ease;
}

.reflection-panel.is-fresh {
  box-shadow:
    0 8px 32px rgba(242, 176, 53, 0.35),
    inset 0 1px 0 rgba(255, 255, 255, 0.55);
  border-color: rgba(242, 176, 53, 0.65);
}

.reflection-panel.is-empty {
  opacity: 0.62;
}

.reflection-header {
  display: flex;
  align-items: center;
  gap: 7px;
  font-family: var(--font-display);
  font-size: 11px;
  font-weight: 700;
  color: var(--brand-navy);
  text-transform: uppercase;
  letter-spacing: 1.3px;
  margin-bottom: var(--sp-sm);
}

.live-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--brand-navy-light);
  flex-shrink: 0;
  transition: background 0.4s ease;
}

.live-dot.pulse {
  background: var(--brand-golden);
  animation: pulse-dot 1.2s ease-in-out infinite;
}

.reflection-text {
  font-family: var(--font-base);
  font-size: 13px;
  line-height: 1.58;
  color: var(--brand-navy);
}

.reflection-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: var(--sp-sm);
  gap: var(--sp-sm);
}

.reflection-time {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--brand-navy-muted);
}

.reflection-tag {
  font-family: var(--font-base);
  font-size: 9px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  background: rgba(242, 176, 53, 0.18);
  color: var(--brand-navy);
  padding: 2px 9px;
  border-radius: var(--radius-xl);
}

@media (prefers-reduced-motion: reduce) {
  .live-dot.pulse       { animation: none !important; }
  .reflection-panel     { animation: none !important; }
}
</style>
