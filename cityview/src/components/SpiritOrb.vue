<template>
  <!-- Outer group: POSITION ONLY (not animated, so CSS can't break it) -->
  <g :transform="`translate(${x}, ${y})`">
    <!-- Inner group: ANIMATION (scale happens at local origin 0,0) -->
    <g class="spirit-orb-anim">
      <!-- Pulse rings -->
      <circle r="30" class="pulse-ring r1" />
      <circle r="30" class="pulse-ring r2" />

      <!-- Outer glow — mood-keyed -->
      <circle r="22" :class="['orb-glow', city.skyMood]" />

      <!-- Core orb — gradient switches with mood -->
      <circle r="14" class="orb-core"
        :fill="city.skyMood === 'healthy' ? 'url(#spiritGradHealthy)'
             : city.skyMood === 'critical' ? 'url(#spiritGradCritical)'
             : 'url(#spiritGrad)'" />

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
  stroke: var(--brand-golden);
  stroke-width: 1.5;
  opacity: 0;
  transform-origin: 0 0;
}
.pulse-ring.r1 { animation: pulse-ring 4s ease-out infinite; }
.pulse-ring.r2 { animation: pulse-ring 4s ease-out 2s infinite; }

/* Mood-keyed outer glow */
.orb-glow               { fill: var(--gold-shadow); transition: fill 2s ease; }
.orb-glow.healthy       { fill: rgba(4,  191, 138, 0.18); }
.orb-glow.warning       { fill: rgba(242, 176,  53, 0.25); }
.orb-glow.critical      { fill: rgba(217, 105,  65, 0.30); }

/* orb-core fill set dynamically in template via :fill binding */
.orb-inner { fill: #FFFCF7; opacity: 0.85; }

.label {
  font-size: 12px;
  font-weight: 700;
  font-family: 'Josefin Sans', sans-serif;
  letter-spacing: 0.5px;
  fill: var(--brand-navy);
}
</style>
