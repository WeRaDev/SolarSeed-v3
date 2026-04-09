<template>
  <g :transform="`translate(${panelX}, ${panelY})`">
    <rect x="0" y="0" width="200" :height="panelHeight" rx="8" class="panel" />

    <!-- Title -->
    <text x="12" y="20" class="detail-title">{{ building.label }}</text>

    <!-- Description -->
    <text x="12" y="36" class="detail-desc">{{ building.desc }}</text>

    <!-- Status -->
    <text x="12" y="54" class="detail-status" :class="building.health">
      {{ building.health === 'up' ? 'Healthy' : building.health === 'down' ? 'DOWN' : 'Unknown' }}
    </text>

    <!-- Resources -->
    <text x="12" y="70" class="detail-resource">
      Port {{ building.port }} | {{ building.mem }}
    </text>

    <!-- Open App link -->
    <text
      v-if="building.appUrl"
      x="12" y="88"
      class="open-link"
      @click.stop="openApp"
      style="cursor: pointer"
    >
      {{ building.appLabel || 'Open App →' }}
    </text>

    <!-- Close hint -->
    <text :x="184" y="16" text-anchor="end" class="close-hint" style="cursor:pointer"
      @click.stop="city.selectBuilding(null)">
      &#xd7;
    </text>
  </g>
</template>

<script setup>
import { computed } from 'vue'
import { useCityStore } from '../stores/city.js'

const props = defineProps({ building: Object })
const city = useCityStore()

// Position panel so it doesn't overflow SVG edges
const panelX = computed(() => {
  const bx = props.building.x
  return bx > 700 ? bx - 220 : bx + 50
})
const panelY = computed(() => {
  const by = props.building.y
  return by > 400 ? by - 110 : by - 50
})

const panelHeight = computed(() => props.building.appUrl ? 100 : 82)

function openApp() {
  if (props.building.appUrl) {
    window.open(props.building.appUrl, '_blank')
  }
}
</script>

<style scoped>
.panel {
  fill: var(--cream-card);
  stroke: var(--gold-border);
  stroke-width: 1;
  filter: drop-shadow(0 2px 6px rgba(0,0,0,0.15));
}

.detail-title {
  font-size: 13px;
  font-weight: 700;
  fill: var(--charcoal);
}

.detail-desc {
  font-size: 10px;
  fill: var(--charcoal-light);
}

.detail-status {
  font-size: 11px;
  font-weight: 600;
}

.detail-status.up { fill: var(--status-up); }
.detail-status.down { fill: var(--status-down); }
.detail-status.unknown { fill: #999; }

.detail-resource {
  font-size: 10px;
  fill: var(--charcoal-light);
}

.open-link {
  font-size: 12px;
  font-weight: 600;
  fill: var(--gold-primary);
  text-decoration: underline;
  transition: fill 0.2s ease;
}
.open-link:hover {
  fill: var(--gold-secondary);
}

.close-hint {
  font-size: 14px;
  fill: var(--charcoal-light);
}
.close-hint:hover {
  fill: var(--status-down);
}
</style>
