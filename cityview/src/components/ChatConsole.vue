<template>
  <Transition name="slide-right">
    <div v-if="visible" class="chat-console" role="dialog" aria-modal="true" :aria-label="`${targetName} console`">
      <div class="console-header">
        <div class="console-title">
          <span class="console-dot" :class="targetType" />
          {{ targetName }}
        </div>
        <button class="close-btn" @click="$emit('close')" aria-label="Close console">✕</button>
      </div>

      <div class="console-body" ref="bodyEl">
        <div v-for="(msg, i) in messages" :key="i" class="msg" :class="msg.role">
          <span class="msg-role">{{ msg.role === 'assistant' ? targetName : 'You' }}</span>
          <p class="msg-text">{{ msg.content }}</p>
        </div>
        <div v-if="messages.length === 0" class="console-empty">
          Commune with {{ targetName }}…
        </div>
      </div>

      <form class="console-input" @submit.prevent="send">
        <input
          v-model="draft"
          class="input-field"
          :placeholder="`Message ${targetName}…`"
          :disabled="sending"
          autocomplete="off"
        />
        <button type="submit" class="send-btn" :disabled="!draft.trim() || sending">
          {{ sending ? '…' : '↑' }}
        </button>
      </form>
    </div>
  </Transition>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  visible:    { type: Boolean, default: false },
  targetType: { type: String,  default: 'spirit' },
  targetName: { type: String,  default: 'Spirit' },
  targetId:   { type: String,  default: '' },
})
defineEmits(['close'])

const messages = ref([])
const draft    = ref('')
const sending  = ref(false)
const bodyEl   = ref(null)

// Clear conversation when target changes
watch(() => props.targetName, () => { messages.value = [] })

async function send() {
  const text = draft.value.trim()
  if (!text) return
  draft.value = ''
  messages.value.push({ role: 'user', content: text })
  sending.value = true
  try {
    const endpoint = props.targetType === 'spirit'
      ? '/spirit/api/v1/chat'
      : `/openfang/api/agents/${props.targetId}/chat`
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text }),
    })
    const data = res.ok ? await res.json() : null
    messages.value.push({
      role: 'assistant',
      content: data?.reply || data?.message || '(no response)',
    })
  } catch {
    messages.value.push({ role: 'assistant', content: '(connection error)' })
  } finally {
    sending.value = false
    setTimeout(() => {
      if (bodyEl.value) bodyEl.value.scrollTop = bodyEl.value.scrollHeight
    }, 50)
  }
}
</script>

<style scoped>
.chat-console {
  position: fixed;
  right: 0;
  top: 56px;
  bottom: 0;
  width: 380px;
  display: flex;
  flex-direction: column;
  background: rgba(253, 240, 216, 0.92);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-left: 1px solid var(--gold-border);
  z-index: 20;
  box-shadow: -4px 0 24px var(--navy-shadow);
}

.console-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--sp-md) var(--sp-lg);
  border-bottom: 1px solid var(--gold-border);
  flex-shrink: 0;
}

.console-title {
  display: flex;
  align-items: center;
  gap: var(--sp-sm);
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 14px;
  color: var(--brand-navy);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.console-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.console-dot.spirit { background: var(--brand-golden); }
.console-dot.agent  { background: var(--brand-green); }

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 18px;
  color: var(--brand-navy-muted);
  line-height: 1;
  padding: 4px;
}
.close-btn:hover { color: var(--brand-navy); }

.console-body {
  flex: 1;
  overflow-y: auto;
  padding: var(--sp-md) var(--sp-lg);
  display: flex;
  flex-direction: column;
  gap: var(--sp-md);
}

.console-empty {
  color: var(--brand-navy-muted);
  font-style: italic;
  font-size: 13px;
  text-align: center;
  margin-top: var(--sp-xl);
}

.msg { display: flex; flex-direction: column; gap: 2px; }
.msg-role {
  font-family: var(--font-display);
  font-size: 9px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--brand-navy-muted);
}
.msg.user .msg-role { color: var(--brand-golden); }
.msg-text {
  font-size: 13px;
  line-height: 1.55;
  color: var(--brand-navy);
}

.console-input {
  display: flex;
  gap: var(--sp-sm);
  padding: var(--sp-md) var(--sp-lg);
  border-top: 1px solid var(--gold-border);
  flex-shrink: 0;
}

.input-field {
  flex: 1;
  border: 1px solid var(--gold-border);
  border-radius: var(--radius-md);
  background: rgba(255,255,255,0.6);
  padding: 8px 12px;
  font-size: 13px;
  font-family: var(--font-base);
  color: var(--brand-navy);
  outline: none;
}
.input-field:focus { border-color: var(--brand-golden); }

.send-btn {
  border: none;
  background: var(--brand-golden);
  color: white;
  border-radius: var(--radius-md);
  width: 36px;
  height: 36px;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.send-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.send-btn:not(:disabled):hover { background: var(--brand-golden-mid); }

.slide-right-enter-active { animation: slide-in-right 0.25s ease; }
.slide-right-leave-active { animation: slide-in-right 0.2s ease reverse; }
</style>
