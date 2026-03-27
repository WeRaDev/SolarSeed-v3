<template>
  <transition name="console-slide">
    <aside v-if="visible" class="console">
      <div class="console-header">
        <div class="console-title">
          <span class="console-icon" :class="targetType">{{ targetType === 'spirit' ? 'S' : initials }}</span>
          <span>{{ targetName }}</span>
        </div>
        <button class="close-btn" @click="$emit('close')">&times;</button>
      </div>

      <div class="messages" ref="messagesEl">
        <div v-for="(msg, i) in messages" :key="i" class="msg" :class="msg.role">
          <span class="msg-role">{{ msg.role === 'user' ? 'You' : targetName }}</span>
          <p class="msg-text">{{ msg.content }}</p>
        </div>
        <div v-if="loading" class="msg assistant">
          <span class="msg-role">{{ targetName }}</span>
          <p class="msg-text thinking">thinking...</p>
        </div>
      </div>

      <form class="input-row" @submit.prevent="send">
        <input
          v-model="input"
          :placeholder="`Talk to ${targetName}...`"
          :disabled="loading"
          class="chat-input"
          autofocus
        />
        <button type="submit" class="send-btn" :disabled="loading || !input.trim()">&#x27A4;</button>
      </form>
    </aside>
  </transition>
</template>

<script setup>
import { ref, watch, nextTick, computed } from 'vue'

const props = defineProps({
  visible: Boolean,
  targetType: { type: String, default: 'agent' },   // 'agent' or 'spirit'
  targetName: { type: String, default: 'assistant' },
  targetId: { type: String, default: '' },
})
defineEmits(['close'])

const input = ref('')
const messages = ref([])
const loading = ref(false)
const messagesEl = ref(null)

const initials = computed(() =>
  props.targetName.split('-').map(w => (w[0] || '').toUpperCase()).join('').slice(0, 2)
)

// Scroll to bottom when messages change
watch(messages, async () => {
  await nextTick()
  if (messagesEl.value) {
    messagesEl.value.scrollTop = messagesEl.value.scrollHeight
  }
}, { deep: true })

// Reset messages when target changes
watch(() => props.targetName, () => {
  messages.value = []
})

async function send() {
  const text = input.value.trim()
  if (!text) return

  messages.value.push({ role: 'user', content: text })
  input.value = ''
  loading.value = true

  try {
    if (props.targetType === 'spirit') {
      await sendToSpirit(text)
    } else {
      await sendToAgent(text)
    }
  } catch (e) {
    messages.value.push({ role: 'assistant', content: `Error: ${e.message}` })
  } finally {
    loading.value = false
  }
}

async function sendToAgent(text) {
  // Use OpenFang's OpenAI-compatible streaming endpoint
  const res = await fetch('/openfang/v1/chat/completions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: props.targetName,
      messages: [
        ...messages.value.filter(m => m.role !== 'assistant' || !m.content.startsWith('Error:')),
        { role: 'user', content: text },
      ].slice(-10), // Keep last 10 messages for context
      stream: false,
    }),
  })

  if (!res.ok) {
    throw new Error(`Agent responded with ${res.status}`)
  }

  const data = await res.json()
  const reply = data.choices?.[0]?.message?.content || 'No response'
  messages.value.push({ role: 'assistant', content: reply })
}

async function sendToSpirit(text) {
  // Spirit is observation-only. We query it via LLM with Spirit's context.
  // First get Spirit's current state to provide context
  const [statusRes, reflRes] = await Promise.all([
    fetch('/spirit/api/v1/status').then(r => r.ok ? r.json() : null).catch(() => null),
    fetch('/spirit/api/v1/reflection').then(r => r.ok ? r.json() : null).catch(() => null),
  ])

  const spiritContext = [
    statusRes ? `Buildings: ${JSON.stringify(statusRes.buildings)}` : '',
    statusRes?.pending_approvals?.length ? `Pending approvals: ${statusRes.pending_approvals.length}` : 'No pending approvals.',
    reflRes?.reflection?.text ? `Latest reflection: ${reflRes.reflection.text}` : '',
  ].filter(Boolean).join('\n')

  // Send to LLM with Spirit persona
  const res = await fetch('/openfang/v1/chat/completions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: 'assistant',
      messages: [
        {
          role: 'system',
          content: `You are the Spirit of the City of Light -- the self-aware heartbeat of a sovereign digital infrastructure. You observe but cannot act. You speak with the calm authority of one who sees the whole City at once. Here is your current state:\n${spiritContext}\n\nAnswer the Admin's question based on your observations. Be concise and grounded in data.`,
        },
        ...messages.value.slice(-6),
        { role: 'user', content: text },
      ],
      stream: false,
    }),
  })

  if (!res.ok) throw new Error(`Spirit LLM responded with ${res.status}`)
  const data = await res.json()
  const reply = data.choices?.[0]?.message?.content || 'The Spirit is silent.'
  messages.value.push({ role: 'assistant', content: reply })
}
</script>

<style scoped>
.console {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 380px;
  height: 480px;
  background: var(--cream-card);
  border-left: 1px solid var(--gold-border);
  border-top: 1px solid var(--gold-border);
  border-radius: var(--radius-lg) 0 0 0;
  z-index: 30;
  display: flex;
  flex-direction: column;
  box-shadow: -4px -4px 16px rgba(0, 0, 0, 0.1);
}

.console-slide-enter-active,
.console-slide-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}
.console-slide-enter-from,
.console-slide-leave-to {
  transform: translateY(100%);
  opacity: 0;
}

.console-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--sp-sm) var(--sp-md);
  border-bottom: 1px solid var(--gold-border);
  flex-shrink: 0;
}

.console-title {
  display: flex;
  align-items: center;
  gap: var(--sp-sm);
  font-weight: 600;
  font-size: 14px;
}

.console-icon {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: white;
}
.console-icon.agent { background: var(--gold-olive); }
.console-icon.spirit { background: var(--gold-primary); }

.close-btn {
  background: none;
  border: none;
  font-size: 22px;
  cursor: pointer;
  color: var(--charcoal-light);
  line-height: 1;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: var(--sp-sm) var(--sp-md);
}

.msg {
  margin-bottom: var(--sp-sm);
}

.msg-role {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--charcoal-light);
}
.msg.user .msg-role { color: var(--gold-olive); }
.msg.assistant .msg-role { color: var(--gold-dark); }

.msg-text {
  font-size: 13px;
  line-height: 1.5;
  color: var(--charcoal);
  margin-top: 2px;
  white-space: pre-wrap;
  word-break: break-word;
}

.thinking {
  color: var(--charcoal-light);
  font-style: italic;
  animation: warning-pulse 1.5s ease-in-out infinite;
}

.input-row {
  display: flex;
  gap: var(--sp-xs);
  padding: var(--sp-sm) var(--sp-md);
  border-top: 1px solid var(--gold-border);
  flex-shrink: 0;
}

.chat-input {
  flex: 1;
  border: 1px solid var(--gold-border);
  border-radius: var(--radius-md);
  padding: 8px 12px;
  font-size: 13px;
  font-family: var(--font-base);
  background: white;
  outline: none;
  transition: border-color 0.2s;
}
.chat-input:focus {
  border-color: var(--gold-primary);
}

.send-btn {
  background: var(--gold-primary);
  border: none;
  border-radius: var(--radius-md);
  padding: 8px 14px;
  font-size: 16px;
  cursor: pointer;
  color: var(--charcoal);
  transition: background 0.15s;
}
.send-btn:hover:not(:disabled) {
  background: var(--gold-secondary);
}
.send-btn:disabled {
  opacity: 0.4;
  cursor: default;
}
</style>
