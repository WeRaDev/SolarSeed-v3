<template>
  <!-- Outer group: POSITION ONLY (not animated, so CSS can't break it) -->
  <g :transform="`translate(${x}, ${y})`">
    <!-- Inner group: ANIMATION (scale happens at local origin 0,0) -->
    <g class="spirit-orb-anim">
      <!-- Pulse rings -->
      <circle r="30" class="pulse-ring r1" />
      <circle r="30" class="pulse-ring r2" />

      <!-- Outer glow -->
      <circle r="22" :class="['orb-glow', city.skyMood]" />

      <!-- Core orb -->
      <circle r="14" class="orb-core" />

      <!-- Inner light -->
      <circle r="6" class="orb-inner" />
    </g>

    <!-- Label outside animation group so it doesn't scale -->
    <text y="40" text-anchor="middle" class="label">Spirit</text>
  </g>
</template>

<script setup>
import { useCityStore } from '../stores/city.js'
defineProps({ x: { type: Number, default: 480 }, y: { type: Number, default: 300 } })
const city = useCityStore()
</script>

<style scoped>
/* Animation on the INNER group only -- position is on the outer group */
.spirit-orb-anim {
  transform-origin: 0 0;
  animation: heartbeat 4s ease-in-out infinite;
}

.pulse-ring {
  fill: none;
  stroke: var(--gold-primary);
  stroke-width: 1.5;
  opacity: 0;
  transform-origin: 0 0;
}

.pulse-ring.r1 { animation: pulse-ring 4s ease-out infinite; }
.pulse-ring.r2 { animation: pulse-ring 4s ease-out 2s infinite; }

.orb-glow { fill: var(--gold-shadow); }
.orb-glow.healthy { fill: rgba(196, 181, 82, 0.25); }
.orb-glow.warning { fill: rgba(232, 169, 75, 0.25); }
.orb-glow.critical { fill: rgba(244, 67, 54, 0.25); }

.orb-core { fill: url(#spiritGrad); }
.orb-inner { fill: #FFF9E6; opacity: 0.8; }

.label {
  font-size: 12px;
  font-weight: 700;
  fill: var(--gold-dark);
}
</style>
