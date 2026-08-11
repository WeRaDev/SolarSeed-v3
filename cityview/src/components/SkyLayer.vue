<template>
  <div class="sky" :class="city.skyMood" role="img" :aria-label="`Sky mood: ${city.skyMood}`">

    <!-- Drifting cloud layer -->
    <div class="cloud-layer" aria-hidden="true">
      <div class="cloud cloud-1" />
      <div class="cloud cloud-2" />
      <div class="cloud cloud-3" />
    </div>

    <!-- Floating pollen / spore particles (always present, mood-coloured) -->
    <div class="pollen-layer" aria-hidden="true">
      <div
        v-for="i in 18"
        :key="'pollen-' + i"
        class="pollen"
        :style="pollenStyle(i)"
      />
    </div>

    <!-- Stars — only in critical mode -->
    <div v-if="city.skyMood === 'critical'" class="stars-layer" aria-hidden="true">
      <div
        v-for="i in 32"
        :key="i"
        class="star"
        :style="starStyle(i)"
      />
    </div>

  </div>
</template>

<script setup>
import { useCityStore } from '../stores/city.js'

const city = useCityStore()

/** Deterministic star positions using golden-angle distribution */
function starStyle(i) {
  const seed = i * 137.508
  return {
    left:              ((seed * 13) % 100) + '%',
    top:               ((seed *  7) % 68)  + '%',
    animationDelay:    ((seed * 0.3) % 3).toFixed(2) + 's',
    animationDuration: (1.4 + (seed % 1.8)).toFixed(2) + 's',
    width:             (1 + (i % 2)) + 'px',
    height:            (1 + (i % 2)) + 'px',
  }
}

/** Deterministic floating pollen positions */
function pollenStyle(i) {
  const seed = i * 83.14
  return {
    left:              ((seed * 7.3)  % 100) + '%',
    top:               ((seed * 4.1)  % 80)  + '%',
    animationDelay:    ((seed * 0.21) % 5).toFixed(2) + 's',
    animationDuration: (3.5 + (seed % 4)).toFixed(2) + 's',
    width:             (2 + (i % 3))  + 'px',
    height:            (2 + (i % 3))  + 'px',
  }
}
</script>

<style scoped>
/* ── Base sky ─────────────────────────────────────── */
.sky {
  position: absolute;
  inset: 0;
  z-index: 0;
  overflow: hidden;
  transition: background 3s ease;
}

.sky.healthy  { background: var(--sky-healthy); }
.sky.warning  { background: var(--sky-warning); }
.sky.critical { background: var(--sky-critical); }

/* ── Clouds ───────────────────────────────────────── */
.cloud-layer {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.cloud {
  position: absolute;
  border-radius: 60px;
  transition: background 3s ease, opacity 2s ease;
}

.sky.healthy  .cloud { background: rgba(255, 255, 255, 0.68); opacity: 1; }
.sky.warning  .cloud { background: rgba(245, 192,  93, 0.45); opacity: 0.9; }
.sky.critical .cloud { background: rgba( 53,  62,  92, 0.50); opacity: 0.75; }

.cloud-1 {
  width: 180px; height: 44px;
  top: 16%;
  animation: drift 24s linear infinite;
}
.cloud-2 {
  width: 108px; height: 28px;
  top: 30%;
  animation: drift 32s linear infinite;
  animation-delay: -11s;
}
.cloud-3 {
  width: 140px; height: 34px;
  top: 10%;
  animation: drift 19s linear infinite;
  animation-delay: -17s;
}

@keyframes drift {
  from { transform: translateX(-22%); }
  to   { transform: translateX(112%); }
}

/* ── Pollen / spore particles ─────────────────────── */
.pollen-layer {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.pollen {
  position: absolute;
  border-radius: 50%;
  animation: pollen-float linear infinite;
  transition: background 3s ease;
}

.sky.healthy  .pollen { background: rgba(4, 191, 138, 0.55); }
.sky.warning  .pollen { background: rgba(242, 176, 53, 0.60); }
.sky.critical .pollen { background: rgba(255, 255, 255, 0.35); }

@keyframes pollen-float {
  0%   { transform: translateY(0)   translateX(0)    scale(1);   opacity: 0; }
  15%  { opacity: 0.9; }
  85%  { opacity: 0.7; }
  100% { transform: translateY(-80px) translateX(20px) scale(0.4); opacity: 0; }
}

/* ── Stars (critical only) ────────────────────────── */
.stars-layer {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.star {
  position: absolute;
  border-radius: 50%;
  background: #FFFFFF;
  opacity: 0;
  animation: twinkle 2s ease-in-out infinite;
}

@keyframes twinkle {
  0%, 100% { opacity: 0.12; }
  50%       { opacity: 0.85; }
}

/* ── Reduced motion ───────────────────────────────── */
@media (prefers-reduced-motion: reduce) {
  .cloud  { animation: none !important; }
  .star   { animation: none !important; opacity: 0.4; }
  .pollen { animation: none !important; opacity: 0.5; }
}
</style>
