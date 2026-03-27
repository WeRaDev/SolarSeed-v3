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
.building { transition: filter 0.4s ease; }

.building.up .wall { fill: var(--cream-card); stroke: var(--gold-olive); stroke-width: 1.5; }
.building.up .roof { fill: var(--gold-primary); stroke: var(--gold-dark); stroke-width: 1; }
.building.up .turret { fill: var(--gold-secondary); stroke: var(--gold-olive); stroke-width: 1; }
.building.up .door { fill: var(--gold-dark); }
.building.up .door-handle { fill: var(--gold-secondary); }
.building.up .window { fill: var(--weather-blue); opacity: 0.6; stroke: var(--gold-olive); stroke-width: 0.5; }
.building.up .chimney { fill: var(--charcoal-light); }
.building.up .dome-top { fill: var(--gold-secondary); stroke: var(--gold-olive); stroke-width: 1; }
.building.up { animation: glow 3s ease-in-out infinite; }

.building.down .wall { fill: #d0d0d0; stroke: #999; stroke-width: 1.5; }
.building.down .roof { fill: #aaa; stroke: #888; stroke-width: 1; }
.building.down .turret { fill: #bbb; stroke: #999; stroke-width: 1; }
.building.down .door { fill: #777; }
.building.down .door-handle { fill: #999; }
.building.down .window { fill: #888; opacity: 0.4; }
.building.down .chimney { fill: #777; }
.building.down .dome-top { fill: #bbb; stroke: #999; stroke-width: 1; }
.building.down { filter: grayscale(0.8) brightness(0.7); }

.building.unknown .wall { fill: #e8e8e8; stroke: #ccc; stroke-width: 1; }
.building.unknown .roof { fill: #ccc; }
.building.unknown .turret { fill: #ddd; }
.building.unknown .door { fill: #aaa; }
.building.unknown .window { fill: #bbb; opacity: 0.3; }
.building.unknown .chimney { fill: #aaa; }
.building.unknown .dome-top { fill: #ddd; stroke: #ccc; stroke-width: 1; }

.building.selected { filter: drop-shadow(0 0 12px var(--gold-glow)) !important; }

.shadow { fill: rgba(0, 0, 0, 0.1); }

.label {
  font-size: 11px;
  font-weight: 600;
  fill: var(--charcoal);
}

.health-badge { stroke: white; stroke-width: 1.5; }
.building.up .health-badge { fill: var(--status-up); }
.building.down .health-badge { fill: var(--status-down); }
.building.unknown .health-badge { fill: #ccc; }

.health-icon { fill: white; font-weight: 700; }

.smoke-puff { fill: #ccc; opacity: 0; }
.smoke-puff.s1 { animation: smoke 2.5s ease-out infinite; }
.smoke-puff.s2 { animation: smoke 2.5s ease-out 0.8s infinite; }
</style>
