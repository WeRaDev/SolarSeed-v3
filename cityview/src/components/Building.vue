<template>
  <g
    class="building"
    :class="[building.health, { selected: isSelected }]"
    :transform="`translate(${building.x}, ${building.y})`"
    @click="city.selectBuilding(building.id)"
    style="cursor: pointer"
  >
    <!-- Ground shadow -->
    <ellipse cx="0" cy="36" rx="30" ry="7" class="shadow" />

    <!-- ── Living Stone Fortress (Nextcloud) ──────────── -->
    <template v-if="building.icon === 'castle'">
      <!-- Earth mound base -->
      <ellipse cx="0" cy="24" rx="30" ry="9" class="earth" />
      <!-- Organic rock body -->
      <path d="M-26,24 C-30,12 -30,-4 -22,-22 C-16,-36 16,-36 22,-22 C30,-4 30,12 26,24 Z" class="wall" />
      <!-- Left crystal turret -->
      <path d="M-20,-20 C-23,-28 -21,-38 -16,-44 C-11,-38 -9,-28 -12,-20 Z" class="turret" />
      <path d="M-18,-44 L-16,-52 L-14,-44 Z" class="roof" />
      <!-- Right crystal turret -->
      <path d="M12,-20 C9,-28 11,-38 16,-44 C21,-38 23,-28 20,-20 Z" class="turret" />
      <path d="M14,-44 L16,-52 L18,-44 Z" class="roof" />
      <!-- Left vine tendril -->
      <path d="M-22,18 Q-28,6 -20,-14 Q-18,-22 -16,-24" class="vine" stroke-width="1.5" stroke-linecap="round" />
      <path d="M-24,8 Q-26,0 -20,-10" class="vine" stroke-width="0.8" stroke-linecap="round" />
      <!-- Right vine tendril -->
      <path d="M20,14 Q26,2 18,-16 Q16,-22 14,-24" class="vine" stroke-width="1.5" stroke-linecap="round" />
      <!-- Cave-arch gate -->
      <path d="M-9,24 C-10,12 -7,5 0,4 C7,5 10,12 9,24 Z" class="door" />
      <!-- Arrow-slit windows -->
      <rect x="-13" y="-12" width="4" height="9" rx="2" class="window" />
      <rect x="9"   y="-12" width="4" height="9" rx="2" class="window" />
    </template>

    <!-- ── Crystal Spire (Prometheus) ─────────────────── -->
    <template v-if="building.icon === 'observatory'">
      <!-- Earth platform -->
      <ellipse cx="0" cy="24" rx="22" ry="7" class="earth" />
      <!-- Faceted crystal body -->
      <path d="M-19,24 C-21,14 -20,-2 -14,-18 C-8,-30 -4,-34 0,-36 C4,-34 8,-30 14,-18 C20,-2 21,14 19,24 Z" class="wall" />
      <!-- Crystal peak -->
      <path d="M-7,-32 C-3,-40 3,-40 7,-32 L0,-48 Z" class="roof" />
      <!-- Facet seam lines -->
      <path d="M0,-36 L0,8" class="vine" stroke-width="0.7" opacity="0.25" />
      <path d="M-14,-18 Q0,-24 14,-18" class="vine" stroke-width="0.7" opacity="0.25" />
      <!-- Side crystal outcroppings -->
      <path d="M-19,2 L-29,-10 L-23,-18 Z" class="turret" />
      <path d="M19,2 L29,-10 L23,-18 Z" class="turret" />
      <!-- Central lens eye -->
      <circle cx="0" cy="-14" r="7" class="window" />
      <circle cx="0" cy="-14" r="3" class="glow" />
      <!-- Organic branch wraps -->
      <path d="M-18,10 C-24,4 -26,-2 -22,-8" class="vine" stroke-width="1.5" stroke-linecap="round" />
      <path d="M18,10 C24,4 26,-2 22,-8" class="vine" stroke-width="1.5" stroke-linecap="round" />
    </template>

    <!-- ── Bio-Forge (Poly-Robot) ──────────────────────── -->
    <template v-if="building.icon === 'factory'">
      <!-- Wide mound body -->
      <path d="M-28,24 C-32,14 -30,-2 -20,-14 C-12,-22 12,-22 20,-14 C30,-2 32,14 28,24 Z" class="wall" />
      <!-- Left mushroom stalk -->
      <rect x="-21" y="-34" width="9" height="26" rx="4" class="chimney" />
      <!-- Left mushroom cap -->
      <path d="M-30,-36 C-30,-44 -8,-46 -8,-36 C-8,-28 -30,-28 -30,-36 Z" class="dome-top" />
      <!-- Right mushroom stalk -->
      <rect x="12"  y="-34" width="9" height="26" rx="4" class="chimney" />
      <!-- Right mushroom cap -->
      <path d="M8,-36 C8,-46 30,-46 30,-36 C30,-28 8,-28 8,-36 Z" class="dome-top" />
      <!-- Spore puffs when healthy -->
      <template v-if="building.health === 'up'">
        <circle cx="-16" cy="-48" r="4"  class="smoke-puff s1" />
        <circle cx="-13" cy="-54" r="3"  class="smoke-puff s2" />
        <circle cx="16"  cy="-48" r="4"  class="smoke-puff s1" style="animation-delay:0.4s" />
        <circle cx="19"  cy="-54" r="3"  class="smoke-puff s2" style="animation-delay:1.2s" />
      </template>
      <!-- Forge windows (bioluminescent) -->
      <ellipse cx="-8" cy="4" rx="5" ry="4" class="window" />
      <ellipse cx="8"  cy="4" rx="5" ry="4" class="window" />
      <!-- Vent line -->
      <path d="M-4,-4 Q0,-8 4,-4" class="vine" stroke-width="1" fill="none" opacity="0.5" />
    </template>

    <!-- ── Mycorrhizal Temple (llama.cpp) ──────────────── -->
    <template v-if="building.icon === 'dome'">
      <!-- Root tendrils -->
      <path d="M-6,24 C-10,30 -20,28 -26,18" class="vine" stroke-width="2"   stroke-linecap="round" />
      <path d="M6,24  C10,30  20,28  26,18"  class="vine" stroke-width="2"   stroke-linecap="round" />
      <path d="M-2,24 C-4,30 -3,34 0,36"    class="vine" stroke-width="1.5" stroke-linecap="round" />
      <path d="M2,24  C4,30  3,34  0,36"    class="vine" stroke-width="1.5" stroke-linecap="round" />
      <!-- Stalk trunk -->
      <path d="M-10,24 C-12,12 -10,2 0,0 C10,2 12,12 10,24 Z" class="chimney" />
      <!-- Great mushroom cap -->
      <path d="M-27,-6 C-29,-24 -18,-38 0,-40 C18,-38 29,-24 27,-6 C20,8 -20,8 -27,-6 Z" class="dome-top" />
      <!-- Gill lines under cap edge -->
      <line x1="-19" y1="2"  x2="-8"  y2="-4" class="vine" stroke-width="0.8" opacity="0.45" />
      <line x1="-10" y1="6"  x2="-2"  y2="0"  class="vine" stroke-width="0.8" opacity="0.45" />
      <line x1="10"  y1="6"  x2="2"   y2="0"  class="vine" stroke-width="0.8" opacity="0.45" />
      <line x1="19"  y1="2"  x2="8"   y2="-4" class="vine" stroke-width="0.8" opacity="0.45" />
      <!-- Portal under cap -->
      <path d="M-6,24 C-7,14 -4,10 0,10 C4,10 7,14 6,24 Z" class="door" />
      <!-- Bioluminescent spots on cap -->
      <circle cx="-13" cy="-16" r="2.5" class="glow" />
      <circle cx="10"  cy="-22" r="2"   class="glow" />
      <circle cx="-2"  cy="-30" r="1.5" class="glow" />
    </template>

    <!-- ── Ancient Treehouse (PostgreSQL / Gitea) ─────── -->
    <template v-if="building.icon === 'house'">
      <!-- Surface roots -->
      <path d="M-10,24 C-14,30 -22,26 -26,16" class="vine" stroke-width="2.5" stroke-linecap="round" />
      <path d="M10,24  C14,30  22,26  26,16"  class="vine" stroke-width="2.5" stroke-linecap="round" />
      <!-- Main trunk -->
      <path d="M-10,24 C-12,12 -10,2 -6,-2 C-2,-6 2,-6 6,-2 C10,2 12,12 10,24 Z" class="wall" />
      <!-- Left thick branch -->
      <path d="M-6,0 C-12,-6 -20,-12 -22,-22" class="bough" stroke-width="6" stroke-linecap="round" />
      <!-- Left leaf crown -->
      <ellipse cx="-22" cy="-24" rx="9" ry="6" class="roof" />
      <!-- Right thick branch -->
      <path d="M6,0 C12,-6 20,-12 22,-22" class="bough" stroke-width="6" stroke-linecap="round" />
      <!-- Right leaf crown -->
      <ellipse cx="22" cy="-24" rx="9" ry="6" class="roof" />
      <!-- House nestled in the tree canopy -->
      <rect x="-14" y="-22" width="28" height="14" rx="2" class="turret" />
      <path d="M-17,-22 L0,-36 L17,-22 Z" class="roof" />
      <!-- Round knothole windows -->
      <ellipse cx="-6" cy="-16" rx="4" ry="4.5" class="window" />
      <ellipse cx="6"  cy="-16" rx="4" ry="4.5" class="window" />
      <!-- Door in trunk base -->
      <path d="M-5,24 C-5,14 -3,8 0,8 C3,8 5,14 5,24 Z" class="door" />
    </template>

    <!-- ── Sacred Grove Hall (OpenFang Agency) ─────────── -->
    <template v-if="building.icon === 'barracks'">
      <!-- Left trunk -->
      <path d="M-28,24 C-30,12 -28,-4 -24,-14 C-21,-22 -19,-22 -17,-16 C-15,-8 -16,8 -18,24 Z" class="wall" />
      <!-- Centre trunk -->
      <path d="M-7,24 C-9,10 -8,-6 -4,-16 C-2,-22 2,-22 4,-16 C8,-6 9,10 7,24 Z" class="wall" />
      <!-- Right trunk -->
      <path d="M17,24 C15,8 16,-8 18,-16 C20,-22 22,-22 24,-14 C28,-4 30,12 28,24 Z" class="wall" />
      <!-- Woven branch canopy -->
      <path d="M-20,-12 C-14,-22 -8,-28 0,-30 C8,-28 14,-22 20,-12" class="bough" stroke-width="5" stroke-linecap="round" fill="none" />
      <!-- Leaf clusters on canopy -->
      <ellipse cx="-22" cy="-22" rx="10" ry="7" class="roof" />
      <ellipse cx="0"   cy="-34" rx="10" ry="7" class="roof" />
      <ellipse cx="22"  cy="-22" rx="10" ry="7" class="roof" />
      <!-- Arch doorways between trunks -->
      <path d="M-18,24 C-19,14 -17,8 -13,6 C-9,8 -9,14 -11,24 Z" class="door" />
      <path d="M5,24  C3,14  5,8   9,6  C13,8  13,14  11,24 Z"  class="door" />
    </template>

    <!-- ── World Pillar (Redis Event Bus) ─────────────── -->
    <template v-if="building.icon === 'tower'">
      <!-- Earth base -->
      <ellipse cx="0" cy="24" rx="16" ry="6" class="earth" />
      <!-- Pillar body -->
      <path d="M-11,24 C-13,14 -12,-8 -10,-28 C-8,-40 8,-40 10,-28 C12,-8 13,14 11,24 Z" class="wall" />
      <!-- Crystal crown tips -->
      <path d="M-10,-28 C-6,-38 6,-38 10,-28 L6,-46 L0,-54 L-6,-46 Z" class="roof" />
      <!-- Data channel light streams -->
      <line x1="-4" y1="20" x2="-4" y2="-26" class="window" stroke-width="1.5" opacity="0.55" />
      <line x1="0"  y1="20" x2="0"  y2="-26" class="window" stroke-width="1.5" opacity="0.55" />
      <line x1="4"  y1="20" x2="4"  y2="-26" class="window" stroke-width="1.5" opacity="0.55" />
      <!-- Vine wrapping left -->
      <path d="M-10,16 Q-14,6 -8,-6 Q-4,-16 -8,-24" class="vine" stroke-width="1.5" stroke-linecap="round" />
      <!-- Vine wrapping right -->
      <path d="M10,12 Q14,2 8,-10 Q4,-20 8,-26" class="vine" stroke-width="1.5" stroke-linecap="round" />
      <!-- Node circles (data flow points) -->
      <circle cx="-10" cy="-8"  r="3" class="window" />
      <circle cx="10"  cy="-16" r="3" class="window" />
      <circle cx="-10" cy="-22" r="2.5" class="window" opacity="0.6" />
    </template>

    <!-- Label -->
    <text y="52" text-anchor="middle" class="label">{{ building.label }}</text>

    <!-- Health badge -->
    <circle cx="28" cy="-36" r="8" class="health-badge" />
    <text x="28" y="-33" text-anchor="middle" class="health-icon" font-size="10">
      {{ building.health === 'up' ? '✓' : building.health === 'down' ? '✗' : '?' }}
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

/* ── Healthy / Up ──────────────────────────────────────── */
.building.up .wall      { fill: var(--brand-golden-pale);  stroke: var(--brand-golden-mid);  stroke-width: 1.5; }
.building.up .roof      { fill: var(--brand-golden);       stroke: var(--brand-navy);         stroke-width: 1;   }
.building.up .turret    { fill: var(--brand-golden-mid);   stroke: var(--brand-golden);       stroke-width: 1;   }
.building.up .door      { fill: var(--brand-navy); }
.building.up .window    { fill: var(--brand-green-soft);   stroke: var(--brand-green-mid);    stroke-width: 0.5; opacity: 0.85; }
.building.up .chimney   { fill: var(--brand-navy-mid); }
.building.up .dome-top  { fill: var(--brand-golden-mid);   stroke: var(--brand-golden);       stroke-width: 1;   }
.building.up .earth     { fill: var(--brand-terra-pale);   stroke: none; }
.building.up .vine      { stroke: var(--brand-green-mid);  fill: none; }
.building.up .bough     { stroke: var(--brand-navy-mid);   fill: none; }
.building.up .glow      { fill: var(--brand-green-soft);   opacity: 0.9; }
.building.up            { animation: glow 3s ease-in-out infinite; }

/* ── Down ──────────────────────────────────────────────── */
.building.down .wall     { fill: var(--brand-terra-pale);  stroke: var(--brand-terra-mid);   stroke-width: 1.5; }
.building.down .roof     { fill: var(--brand-terra-soft);  stroke: var(--brand-terra);        stroke-width: 1;   }
.building.down .turret   { fill: var(--brand-terra-soft);  stroke: var(--brand-terra-mid);   stroke-width: 1;   }
.building.down .door     { fill: var(--brand-navy-muted); }
.building.down .window   { fill: var(--brand-navy-pale);   opacity: 0.3; }
.building.down .chimney  { fill: var(--brand-navy-light); }
.building.down .dome-top { fill: var(--brand-terra-soft);  stroke: var(--brand-terra-mid);   stroke-width: 1;   }
.building.down .earth    { fill: var(--brand-navy-pale);   stroke: none; }
.building.down .vine     { stroke: var(--brand-navy-light); fill: none; }
.building.down .bough    { stroke: var(--brand-navy-light); fill: none; }
.building.down .glow     { fill: none; }
.building.down           { filter: grayscale(0.55) brightness(0.75); animation: warning-pulse 2s ease-in-out infinite; }

/* ── Unknown / dormant ─────────────────────────────────── */
.building.unknown .wall     { fill: var(--brand-navy-pale);  stroke: var(--brand-navy-light); stroke-width: 1; }
.building.unknown .roof     { fill: var(--brand-navy-light); }
.building.unknown .turret   { fill: var(--brand-navy-light); }
.building.unknown .door     { fill: var(--brand-navy-muted); }
.building.unknown .window   { fill: var(--brand-navy-light); opacity: 0.2; }
.building.unknown .chimney  { fill: var(--brand-navy-light); }
.building.unknown .dome-top { fill: var(--brand-navy-light);  stroke: var(--brand-navy-pale); stroke-width: 1; }
.building.unknown .earth    { fill: var(--brand-navy-pale);   stroke: none; }
.building.unknown .vine     { stroke: var(--brand-navy-light); fill: none; opacity: 0.4; }
.building.unknown .bough    { stroke: var(--brand-navy-light); fill: none; opacity: 0.4; }
.building.unknown .glow     { fill: none; }
.building.unknown           { opacity: 0.5; }

/* ── Selected highlight ────────────────────────────────── */
.building.selected { filter: drop-shadow(0 0 14px var(--gold-glow)) !important; }

/* ── Shared elements ───────────────────────────────────── */
.shadow { fill: rgba(24, 37, 64, 0.10); }

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

/* Spore / smoke (factory chimneys) */
.smoke-puff { fill: var(--brand-golden-soft); opacity: 0; }
.smoke-puff.s1 { animation: smoke 2.8s ease-out infinite; }
.smoke-puff.s2 { animation: smoke 2.8s ease-out 0.9s infinite; }
</style>
