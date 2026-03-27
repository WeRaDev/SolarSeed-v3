<template>
  <!-- Outer group: POSITION (not animated) -->
  <g :transform="`translate(${x}, ${y})`">
    <!-- Inner group: BOB ANIMATION -->
    <g class="agent-bob" :style="{ animationDelay: `${delay}s` }">
      <!-- Status ring -->
      <circle r="14" class="ring" :class="agent.state === 'Running' ? 'running' : 'stopped'" />
      <!-- Body -->
      <circle r="11" class="body" />
      <!-- Initials -->
      <text y="4" text-anchor="middle" class="initials">{{ initials }}</text>
    </g>
    <!-- Name outside animation so it stays stable -->
    <text y="24" text-anchor="middle" class="name">{{ shortName }}</text>
  </g>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  agent: Object,
  x: Number,
  y: Number,
  delay: { type: Number, default: 0 },
})

const initials = computed(() => {
  const n = props.agent.name || ''
  return n.split('-').map(w => w[0]?.toUpperCase() || '').join('').slice(0, 2)
})

const shortName = computed(() => {
  const n = props.agent.name || ''
  return n.replace('spirit-', 'S.')
})
</script>

<style scoped>
.agent-bob {
  transform-origin: 0 0;
  animation: bob 3s ease-in-out infinite;
}

.ring { fill: none; stroke-width: 2; }
.ring.running { stroke: var(--status-up); }
.ring.stopped { stroke: #999; }

.body { fill: var(--cream-card); stroke: var(--gold-olive); stroke-width: 1; }

.initials {
  font-size: 10px;
  font-weight: 700;
  fill: var(--gold-dark);
}

.name {
  font-size: 8px;
  fill: var(--charcoal-light);
}
</style>
