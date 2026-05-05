<template>
  <!-- Outer group: POSITION ONLY -->
  <g :transform="`translate(${x}, ${y})`">

    <!-- Inner group: HEARTBEAT ANIMATION -->
    <g class="spirit-orb-anim">

      <!-- Pulse aura rings -->
      <circle r="36" class="pulse-ring r1" />
      <circle r="36" class="pulse-ring r2" />

      <!-- Outer mood glow -->
      <circle r="24" :class="['orb-glow', city.skyMood]" />

      <!-- 6 living petals rotating around the seed core -->
      <path
        v-for="i in 6"
        :key="'petal-' + i"
        d="M 0,0 Q 5,-10 0,-18 Q -5,-10 0,0"
        class="orb-petal"
        :class="city.skyMood"
        :transform="`rotate(${(i - 1) * 60})`"
      />

      <!-- Seed-pod core gradient -->
      <circle r="11" class="orb-core"
        :fill="city.skyMood === 'healthy'  ? 'url(#spiritGradHealthy)'
             : city.skyMood === 'critical' ? 'url(#spiritGradCritical)'
             : 'url(#spiritGrad)'" />

      <!-- Inner light nucleus -->
      <circle r="5" class="orb-inner" />

      <!-- Bioluminescent center dot -->
      <circle r="2" class="orb-nucleus" :class="city.skyMood" />

    </g>

    <!-- Label stays outside animation group -->
    <text y="48" text-anchor="middle" class="label">Spirit</text>
  </g>
</template>

<script setup>
import { useCityStore } from '../stores/city.js'
defineProps({ x: { type: Number, default: 480 }, y: { type: Number, default: 300 } })
const city = useCityStore()
</script>

<style scoped>
/* Inner group animates — position is on the outer group */
.spirit-orb-anim {
  transform-origin: 0 0;
  animation: heartbeat 4s ease-in-out infinite;
}

/* ── Pulse rings ─────────────────────────────────── */
.pulse-ring {
  fill: none;
  stroke: var(--brand-golden);
  stroke-width: 1.5;
  opacity: 0;
  transform-origin: 0 0;
}
.pulse-ring.r1 { animation: pulse-ring 4s ease-out infinite; }
.pulse-ring.r2 { animation: pulse-ring 4s ease-out 2s infinite; }

/* ── Mood-keyed outer glow ───────────────────────── */
.orb-glow               { fill: var(--gold-shadow);             transition: fill 2s ease; }
.orb-glow.healthy       { fill: rgba(4,  191, 138, 0.18); }
.orb-glow.warning       { fill: rgba(242, 176,  53, 0.25); }
.orb-glow.critical      { fill: rgba(217, 105,  65, 0.30); }

/* ── Living petals ───────────────────────────────── */
.orb-petal {
  fill: var(--brand-golden-soft);
  stroke: var(--brand-golden-mid);
  stroke-width: 0.5;
  opacity: 0.72;
  transform-origin: 0 0;
  transition: fill 2s ease, stroke 2s ease;
}
.orb-petal.healthy {
  fill: var(--brand-green-soft);
  stroke: var(--brand-green-mid);
}
.orb-petal.warning {
  fill: var(--brand-golden-soft);
  stroke: var(--brand-golden-mid);
}
.orb-petal.critical {
  fill: var(--brand-terra-soft);
  stroke: var(--brand-terra-mid);
}

/* ── Seed core — fill set via :fill binding ──────── */
/* (no fill rule here so the SVG presentation attr wins) */

/* ── Inner nucleus ───────────────────────────────── */
.orb-inner   { fill: #FFFCF7; opacity: 0.88; }
.orb-nucleus { transition: fill 2s ease; }
.orb-nucleus.healthy  { fill: var(--brand-green); }
.orb-nucleus.warning  { fill: var(--brand-golden); }
.orb-nucleus.critical { fill: var(--brand-terra); }

/* ── Label ───────────────────────────────────────── */
.label {
  font-size: 12px;
  font-weight: 700;
  font-family: 'Josefin Sans', sans-serif;
  letter-spacing: 0.5px;
  fill: var(--brand-navy);
}
</style>
