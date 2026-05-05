<template>
  <svg class="city-scene" viewBox="0 0 960 600" preserveAspectRatio="xMidYMid meet">
    <defs>
      <!-- Spirit orb gradients — mood-keyed -->
      <radialGradient id="spiritGrad" cx="38%" cy="32%">
        <stop offset="0%"   stop-color="#FFFCF7" />
        <stop offset="48%"  stop-color="#F5C05D" />
        <stop offset="100%" stop-color="#F2B035" />
      </radialGradient>
      <radialGradient id="spiritGradHealthy" cx="38%" cy="32%">
        <stop offset="0%"   stop-color="#D7F5EC" />
        <stop offset="55%"  stop-color="#36CCA1" />
        <stop offset="100%" stop-color="#04BF8A" />
      </radialGradient>
      <radialGradient id="spiritGradCritical" cx="38%" cy="32%">
        <stop offset="0%"   stop-color="#F7E1D9" />
        <stop offset="55%"  stop-color="#E18767" />
        <stop offset="100%" stop-color="#D96941" />
      </radialGradient>

      <!-- Forest floor radial glow -->
      <radialGradient id="forestFloor" cx="50%" cy="85%" r="55%">
        <stop offset="0%"   stop-color="rgba(4,191,138,0.10)" />
        <stop offset="50%"  stop-color="rgba(242,176,53,0.06)" />
        <stop offset="100%" stop-color="rgba(0,0,0,0)" />
      </radialGradient>
    </defs>

    <!-- Forest floor — earth glow beneath the city -->
    <ellipse cx="480" cy="530" rx="450" ry="110" fill="url(#forestFloor)" />

    <!-- Mycorrhizal root network — data flows like nutrients through mycelium -->
    <!-- Primary roots: arc underground (control points pulled to y≈400) before rising -->
    <path
      v-for="b in city.buildings"
      :key="'root-' + b.id"
      :d="`M 480,300 C 480,${rootCtrl(b).c1y} ${b.x},${rootCtrl(b).c2y} ${b.x},${b.y}`"
      stroke="var(--brand-green-soft)"
      stroke-width="1.8"
      stroke-linecap="round"
      fill="none"
      opacity="0.38"
    />
    <!-- Secondary fine veins — offset for organic texture -->
    <path
      v-for="b in city.buildings"
      :key="'vein-' + b.id"
      :d="`M 480,300 Q ${(480 + b.x) / 2 + 20},${(300 + b.y) / 2 + 28} ${b.x + 5},${b.y}`"
      stroke="var(--brand-golden-soft)"
      stroke-width="0.9"
      stroke-linecap="round"
      fill="none"
      opacity="0.20"
    />

    <!-- Buildings -->
    <Building v-for="b in city.buildings" :key="b.id" :building="b" />

    <!-- Spirit Heart (clickable → opens Spirit console) -->
    <g style="cursor:pointer" @click.stop="$emit('open-spirit')">
      <SpiritOrb :x="480" :y="300" />
    </g>

    <!-- Nature spirit agents orbiting the Spirit heart -->
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

// Root network control points — roots dip toward the earth (y≈400) before rising
function rootCtrl(b) {
  const underEarth = 400
  return {
    c1y: underEarth,
    c2y: Math.max(underEarth - 20, (b.y + underEarth) / 2),
  }
}

// Agent positions in a circle around Spirit at (480, 300)
const SPIRIT_X = 480
const SPIRIT_Y = 300
const ORBIT_RADIUS = 82

function agentPos(index, total) {
  if (total === 0) return { x: SPIRIT_X, y: SPIRIT_Y }
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
