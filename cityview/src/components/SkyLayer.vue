<template>
  <div class="sky" :class="city.skyMood" />
</template>

<script setup>
import { useCityStore } from '../stores/city.js'
const city = useCityStore()
</script>

<style scoped>
.sky {
  position: absolute;
  inset: 0;
  z-index: 0;
  transition: background 2s ease;
}

.sky.healthy {
  background: linear-gradient(180deg, #87CEEB 0%, #FDF5D6 60%, #FDFBF5 100%);
}

.sky.warning {
  background: linear-gradient(180deg, #B8860B 0%, #DAA520 40%, #F5DEB3 100%);
}

.sky.critical {
  background: linear-gradient(180deg, #2C2C2C 0%, #4A3030 40%, #6B4040 100%);
}
</style>
