<template>
  <g
    class="building"
    :class="[building.health, { selected: isSelected }]"
    :transform="`translate(${building.x}, ${building.y})`"
    @click="city.selectBuilding(building.id)"
    style="cursor: pointer"
  >
    <!-- Shadow -->
    <ellipse cx="0" cy="38" rx="32" ry="8" class="shadow" />

    <!-- Castle / Fortress -->
    <template v-if="building.icon === 'castle'">
      <rect x="-28" y="-30" width="56" height="60" rx="4" class="wall" />
      <rect x="-22" y="-42" width="12" height="16" rx="2" class="turret" />
      <rect x="10" y="-42" width="12" height="16" rx="2" class="turret" />
      <rect x="-6" y="-10" width="12" height="20" rx="1" class="door" />
      <rect x="-4" y="8" width="8" height="2" class="door-handle" />
    </template>

    <!-- Observatory / Library -->
    <template v-if="building.icon === 'observatory'">
      <rect x="-22" y="-20" width="44" height="50" rx="4" class="wall" />
      <polygon points="-22,-20 0,-46 22,-20" class="roof" />
      <circle cx="0" cy="-26" r="6" class="window" />
      <rect x="-4" y="6" width="8" height="14" rx="1" class="door" />
    </template>

    <!-- Factory -->
    <template v-if="building.icon === 'factory'">
      <rect x="-28" y="-16" width="56" height="46" rx="3" class="wall" />
      <rect x="14" y="-40" width="10" height="28" rx="2" class="chimney" />
      <!-- Smoke puffs when healthy -->
      <template v-if="building.health === 'up'">
        <circle cx="19" cy="-46" r="4" class="smoke-puff s1" />
        <circle cx="21" cy="-52" r="3" class="smoke-puff s2" />
      </template>
      <rect x="-20" y="2" width="14" height="14" rx="1" class="window" />
      <rect x="6" y="2" width="14" height="14" rx="1" class="window" />
    </template>

    <!-- Dome / University -->
    <template v-if="building.icon === 'dome'">
      <rect x="-24" y="-10" width="48" height="40" rx="4" class="wall" />
      <ellipse cx="0" cy="-10" rx="24" ry="18" class="dome-top" />
      <rect x="-4" y="6" width="8" height="14" rx="1" class="door" />
    </template>

    <!-- House -->
    <template v-if="building.icon === 'house'">
      <rect x="-22" y="-10" width="44" height="40" rx="3" class="wall" />
      <polygon points="-26,-10 0,-36 26,-10" class="roof" />
      <rect x="-4" y="6" width="8" height="14" rx="1" class="door" />
      <rect x="-16" y="-2" width="8" height="8" rx="1" class="window" />
      <rect x="8" y="-2" width="8" height="8" rx="1" class="window" />
    </template>

    <!-- Barracks / Agency -->
    <template v-if="building.icon === 'barracks'">
      <rect x="-30" y="-14" width="60" height="44" rx="3" class="wall" />
      <polygon points="-30,-14 0,-32 30,-14" class="roof" />
      <rect x="-20" y="2" width="10" height="12" rx="1" class="door" />
      <rect x="-4" y="2" width="10" height="12" rx="1" class="door" />
      <rect x="12" y="2" width="10" height="12" rx="1" class="door" />
    </template>

    <!-- Tower / Event Bus (Redis) -->
    <template v-if="building.icon === 'tower'">
      <rect x="-12" y="-40" width="24" height="70" rx="3" class="wall" />
      <rect x="-16" y="-44" width="32" height="8" rx="2" class="roof" />
      <rect x="-6" y="-30" width="12" height="8" rx="1" class="window" />
      <rect x="-6" y="-16" width="12" height="8" rx="1" class="window" />
      <rect x="-6" y="-2" width="12" height="8" rx="1" class="window" />
      <rect x="-4" y="14" width="8" height="12" rx="1" class="door" />
    </template>

    <!-- Label -->
    <text y="52" text-anchor="middle" class="label">{{ building.label }}</text>

    <!-- Health badge -->
    <circle cx="28" cy="-36" r="8" class="health-badge" />
    <text x="28" y="-33" text-anchor="middle" class="health-icon" font-size="10">
      {{ building.health === 'up' ? '\u2713' : building.health === 'down' ? '\u2717' : '?' }}
    </text>
  </g>
</template>

<script setup>
import { computed } from 'vue'
import { useCityStore } from '../stores/city.js'

const props = defineProps({ building: Object })
const city = useCityStore()
const isSelected = computed(() => city.selectedBuildingId === props.building.id)
</script>

<style scoped>
.building { transition: filter 0.5s ease; }

/* ── Healthy / Up ──────────────────────────────────── */
.building.up .wall     { fill: var(--brand-golden-pale); stroke: var(--brand-golden-mid); stroke-width: 1.5; }
.building.up .roof     { fill: var(--brand-golden);      stroke: var(--brand-navy);       stroke-width: 1; }
.building.up .turret   { fill: var(--brand-golden-mid);  stroke: var(--brand-golden);     stroke-width: 1; }
.building.up .door     { fill: var(--brand-navy); }
.building.up .door-handle { fill: var(--brand-golden-mid); }
/* Windows glow WeRa emerald green — the city is alive */
.building.up .window   { fill: var(--brand-green-soft);  opacity: 0.75; stroke: var(--brand-green-mid); stroke-width: 0.5; }
.building.up .chimney  { fill: var(--brand-navy-mid); }
.building.up .dome-top { fill: var(--brand-golden-mid);  stroke: var(--brand-golden);     stroke-width: 1; }
.building.up { animation: glow 3s ease-in-out infinite; }

/* ── Down ──────────────────────────────────────────── */
.building.down .wall     { fill: var(--brand-terra-pale); stroke: var(--brand-terra-mid); stroke-width: 1.5; }
.building.down .roof     { fill: var(--brand-terra-soft); stroke: var(--brand-terra);     stroke-width: 1; }
.building.down .turret   { fill: var(--brand-terra-soft); stroke: var(--brand-terra-mid); stroke-width: 1; }
.building.down .door     { fill: var(--brand-navy-muted); }
.building.down .door-handle { fill: var(--brand-terra-soft); }
.building.down .window   { fill: var(--brand-navy-pale); opacity: 0.35; }
.building.down .chimney  { fill: var(--brand-navy-light); }
.building.down .dome-top { fill: var(--brand-terra-soft); stroke: var(--brand-terra-mid); stroke-width: 1; }
.building.down { filter: grayscale(0.55) brightness(0.75); animation: warning-pulse 2s ease-in-out infinite; }

/* ── Unknown / loading ─────────────────────────────── */
.building.unknown .wall     { fill: var(--brand-navy-pale); stroke: var(--brand-navy-light); stroke-width: 1; }
.building.unknown .roof     { fill: var(--brand-navy-light); }
.building.unknown .turret   { fill: var(--brand-navy-light); }
.building.unknown .door     { fill: var(--brand-navy-muted); }
.building.unknown .window   { fill: var(--brand-navy-light); opacity: 0.25; }
.building.unknown .chimney  { fill: var(--brand-navy-light); }
.building.unknown .dome-top { fill: var(--brand-navy-light); stroke: var(--brand-navy-pale); stroke-width: 1; }
.building.unknown           { opacity: 0.5; }

/* ── Selected highlight ────────────────────────────── */
.building.selected { filter: drop-shadow(0 0 14px var(--gold-glow)) !important; }

.shadow { fill: rgba(24, 37, 64, 0.12); }

.label {
  font-size: 11px;
  font-weight: 600;
  font-family: 'Josefin Sans', sans-serif;
  letter-spacing: 0.3px;
  fill: var(--brand-navy);
}

.health-badge { stroke: white; stroke-width: 1.5; }
.building.up      .health-badge { fill: var(--status-up); }
.building.down    .health-badge { fill: var(--status-down); }
.building.unknown .health-badge { fill: var(--brand-navy-light); }

.health-icon { fill: white; font-weight: 700; }

/* Smoke colour matches brand navy-mid */
.smoke-puff { fill: var(--brand-navy-light); opacity: 0; }
.smoke-puff.s1 { animation: smoke 2.5s ease-out infinite; }
.smoke-puff.s2 { animation: smoke 2.5s ease-out 0.8s infinite; }
</style>
