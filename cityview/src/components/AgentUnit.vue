<template>
  <!-- Outer group: POSITION -->
  <g :transform="`translate(${x}, ${y})`">

    <!-- Inner group: BOB ANIMATION -->
    <g class="agent-bob" :style="{ animationDelay: `${delay}s` }">

      <!-- Aura ring — mood-keyed to running/stopped state -->
      <circle r="16" class="aura-ring" :class="agent.state === 'Running' ? 'running' : 'stopped'" />

      <!-- Teardrop body — a spirit emerging from the earth -->
      <path
        d="M 0,-13 C 6,-13 10,-7 10,0 C 10,8 6,14 0,18 C -6,14 -10,8 -10,0 C -10,-7 -6,-13 0,-13 Z"
        class="body"
        :class="agent.state === 'Running' ? 'running' : 'stopped'"
      />

      <!-- Inner glow orb -->
      <circle r="5" class="inner-glow" :class="agent.state === 'Running' ? 'running' : 'stopped'" />

      <!-- Spirit eye (a tiny knothole) -->
      <ellipse cx="0" cy="-2" rx="2.5" ry="3" class="spirit-eye" :class="agent.state === 'Running' ? 'running' : 'stopped'" />

      <!-- Wisp tail (trailing light beneath teardrop) -->
      <path
        d="M 0,18 Q 3,24 0,28 Q -2,32 0,36"
        class="wisp"
        :class="agent.state === 'Running' ? 'running' : 'stopped'"
        stroke-linecap="round"
        fill="none"
      />

    </g>

    <!-- Name label — stays stable outside animation group -->
    <text y="32" text-anchor="middle" class="name">{{ shortName }}</text>
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

const shortName = computed(() => {
  const n = props.agent.name || ''
  return n.replace('spirit-', 'S.').replace('agent-', 'A.')
})
</script>

<style scoped>
/* ── Bob animation on inner group ────────────────── */
.agent-bob {
  transform-origin: 0 0;
  animation: bob 3s ease-in-out infinite;
}

/* ── Aura ring ───────────────────────────────────── */
.aura-ring {
  fill: none;
  stroke-width: 1.5;
  opacity: 0.6;
}
.aura-ring.running {
  stroke: var(--brand-green);
  animation: pulse-ring 3s ease-out infinite;
  transform-origin: 0 0;
}
.aura-ring.stopped {
  stroke: var(--brand-navy-light);
  opacity: 0.3;
}

/* ── Teardrop body ───────────────────────────────── */
.body {
  stroke-width: 1;
  transition: fill 0.8s ease, stroke 0.8s ease;
}
.body.running {
  fill: var(--brand-golden-pale);
  stroke: var(--brand-golden-mid);
}
.body.stopped {
  fill: var(--brand-navy-pale);
  stroke: var(--brand-navy-light);
}

/* ── Inner glow ──────────────────────────────────── */
.inner-glow {
  transition: fill 0.8s ease;
}
.inner-glow.running {
  fill: var(--brand-green-soft);
  opacity: 0.9;
}
.inner-glow.stopped {
  fill: var(--brand-navy-light);
  opacity: 0.3;
}

/* ── Spirit eye ──────────────────────────────────── */
.spirit-eye {
  transition: fill 0.8s ease;
}
.spirit-eye.running {
  fill: var(--brand-green);
  opacity: 0.85;
}
.spirit-eye.stopped {
  fill: var(--brand-navy-muted);
  opacity: 0.4;
}

/* ── Wisp tail ───────────────────────────────────── */
.wisp {
  stroke-width: 1.5;
  transition: stroke 0.8s ease, opacity 0.8s ease;
}
.wisp.running {
  stroke: var(--brand-golden-soft);
  opacity: 0.7;
  animation: wisp-flicker 2.5s ease-in-out infinite;
}
.wisp.stopped {
  stroke: var(--brand-navy-light);
  opacity: 0.2;
}

@keyframes wisp-flicker {
  0%, 100% { opacity: 0.4; stroke-dashoffset: 0; }
  50%       { opacity: 0.9; stroke-dashoffset: 4; }
}

/* ── Name label ──────────────────────────────────── */
.name {
  font-size: 8px;
  font-family: 'Josefin Sans', sans-serif;
  fill: var(--brand-navy-muted);
  letter-spacing: 0.3px;
}
</style>
