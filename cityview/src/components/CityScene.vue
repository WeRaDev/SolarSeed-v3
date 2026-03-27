<template>
  <svg class="city-scene" viewBox="0 0 960 600" preserveAspectRatio="xMidYMid meet">
    <defs>
      <radialGradient id="spiritGrad" cx="40%" cy="35%">
        <stop offset="0%" stop-color="#FFF9E6" />
        <stop offset="50%" stop-color="#D4C563" />
        <stop offset="100%" stop-color="#C4B552" />
      </radialGradient>
    </defs>

    <!-- Ground plane -->
    <ellipse cx="480" cy="500" rx="420" ry="80" fill="rgba(168,157,63,0.08)" />

    <!-- Road paths connecting buildings to center -->
    <line
      v-for="b in city.buildings"
      :key="'road-' + b.id"
    :x1="480" :y1="300"
      :x2="b.x" :y2="b.y"
      stroke="var(--gold-border)"
      stroke-width="2"
      stroke-dasharray="6 4"
    />

    <!-- Buildings -->
    <Building v-for="b in city.buildings" :key="b.id" :building="b" />

    <!-- Spirit Orb (clickable -> opens Spirit console) -->
    <g style="cursor:pointer" @click.stop="$emit('open-spirit')">
      <SpiritOrb :x="480" :y="300" />
    </g>

    <!-- Agent units orbiting the Spirit orb (clickable -> opens agent console) -->
    <g
      v-for="(agent, i) in city.agents"
      :key="agent.id || agent.name"
      style="cursor:pointer"
      @click.stop="$emit('open-agent', agent)"
    >
      <AgentUnit
        :agent="agent"
        :x="agentPos(i, city.agents.length).x"
        :y="agentPos(i, city.agents.length).y"
        :delay="i * 0.5"
      />
    </g>

    <!-- Building detail overlay -->
    <BuildingDetail v-if="selectedBuilding" :building="selectedBuilding" />
  </svg>
</template>

<script setup>
import { computed } from 'vue'
import { useCityStore } from '../stores/city.js'
import Building from './Building.vue'
import SpiritOrb from './SpiritOrb.vue'
import AgentUnit from './AgentUnit.vue'
import BuildingDetail from './BuildingDetail.vue'

defineEmits(['open-agent', 'open-spirit'])

const city = useCityStore()
const selectedBuilding = computed(() =>
  city.selectedBuildingId ? city.buildings.find(b => b.id === city.selectedBuildingId) : null
)

// Position agents in a circle around Spirit at (480, 300)
const SPIRIT_X = 480
const SPIRIT_Y = 300
const ORBIT_RADIUS = 80

function agentPos(index, total) {
  if (total === 0) return { x: SPIRIT_X, y: SPIRIT_Y }
  // Distribute evenly starting from top (-PI/2) going clockwise
  const angle = -Math.PI / 2 + (2 * Math.PI * index) / Math.max(total, 1)
  return {
    x: Math.round(SPIRIT_X + ORBIT_RADIUS * Math.cos(angle)),
    y: Math.round(SPIRIT_Y + ORBIT_RADIUS * Math.sin(angle)),
  }
}
</script>

<style scoped>
.city-scene {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}
</style>
