<template>
  <div class="city-viewport">
    <StatusBar />
    <div class="city-canvas">
      <SkyLayer />
      <CityScene @open-agent="openAgent" @open-spirit="openSpirit" />
      <ReflectionPanel />
      <ConnectionPanel />
    </div>
    <ApprovalQueue />
    <ChatConsole
      :visible="consoleOpen"
      :targetType="consoleTarget.type"
      :targetName="consoleTarget.name"
      :targetId="consoleTarget.id"
      @close="consoleOpen = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useCityStore } from '../stores/city.js'
import { usePolling } from '../composables/usePolling.js'
import StatusBar from '../components/StatusBar.vue'
import SkyLayer from '../components/SkyLayer.vue'
import CityScene from '../components/CityScene.vue'
import ReflectionPanel from '../components/ReflectionPanel.vue'
import ApprovalQueue from '../components/ApprovalQueue.vue'
import ChatConsole from '../components/ChatConsole.vue'
import ConnectionPanel from '../components/ConnectionPanel.vue'

const city = useCityStore()
const { start } = usePolling(() => city.poll(), 10000)

onMounted(start)
onMounted(() => city.refreshConnectionStatus())

const consoleOpen = ref(false)
const consoleTarget = ref({ type: 'agent', name: 'assistant', id: '' })

function openAgent(agent) {
  consoleTarget.value = { type: 'agent', name: agent.name, id: agent.id || '' }
  consoleOpen.value = true
}

function openSpirit() {
  consoleTarget.value = { type: 'spirit', name: 'Spirit', id: '' }
  consoleOpen.value = true
}
</script>

<style scoped>
.city-viewport {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  position: relative;
  overflow: hidden;
}

.city-canvas {
  flex: 1;
  position: relative;
  overflow: hidden;
}
</style>
