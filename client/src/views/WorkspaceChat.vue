<template>
  <div class="chat-workspace">
    <div class="chat-header">
      <h2 class="chat-title">创作工作台</h2>
      <div class="agent-selector">
        <button
          v-for="a in agents"
          :key="a.key"
          :class="['agent-btn', { active: currentAgent === a.key }]"
          @click="currentAgent = a.key"
        >
          {{ a.icon }} {{ a.label }}
        </button>
      </div>
    </div>

    <div class="chat-messages" ref="messagesEl">
      <div v-if="messages.length === 0" class="chat-empty">
        <div class="chat-empty-icon">🖊️</div>
        <div class="chat-empty-text">选择Agent，开始创作对话</div>
        <div class="chat-empty-hints">
          <button v-for="h in hints" :key="h" class="hint-btn" @click="sendMessage(h)">{{ h }}</button>
        </div>
      </div>

      <div v-for="(msg, i) in messages" :key="i" :class="['message', msg.role]">
        <div class="message-avatar">{{ msg.role === 'user' ? '🧑' : '🤖' }}</div>
        <div class="message-content">
          <div class="message-agent" v-if="msg.role === 'assistant'">{{ msg.agent }}</div>
          <div class="message-text" v-html="formatText(msg.content)"></div>
          <div class="message-actions" v-if="msg.role === 'assistant' && msg.content">
            <button class="btn btn-sm btn-secondary" @click="copyText(msg.content)">复制</button>
            <button class="btn btn-sm btn-secondary" @click="sendMessage('请重新生成')">重新生成</button>
          </div>
        </div>
      </div>

      <div v-if="streaming" class="message assistant">
        <div class="message-avatar">🤖</div>
        <div class="message-content">
          <div class="message-agent">{{ currentAgentLabel }}</div>
          <div class="message-text streaming-text">
            {{ streamingContent }}<span class="cursor">▌</span>
          </div>
        </div>
      </div>
    </div>

    <div class="chat-input-area">
      <div class="chat-input-wrapper">
        <textarea
          v-model="inputText"
          @keydown.enter.exact.prevent="handleSend"
          placeholder="输入创作需求或指令..."
          rows="1"
          ref="inputEl"
        ></textarea>
        <button class="btn btn-primary send-btn" @click="handleSend" :disabled="!inputText.trim() || streaming">
          {{ streaming ? '生成中...' : '发送' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { createChatStream } from '../../api'

const route = useRoute()
const projectId = computed(() => route.params.id)

const agents = [
  { key: 'planner', label: '规划', icon: '🧠' },
  { key: 'writer', label: '写作', icon: '✍️' },
  { key: 'reviewer', label: '审查', icon: '🔍' },
  { key: 'character', label: '角色', icon: '🎭' },
]

const hints = [
  '帮我规划一个悬疑小说的大纲',
  '写一段主角发现真相的场景',
  '审查最新章节的一致性',
  '设计一个反派角色',
]

const currentAgent = ref('writer')
const currentAgentLabel = computed(() => agents.find(a => a.key === currentAgent.value)?.label || '写作')
const messages = ref([])
const inputText = ref('')
const streaming = ref(false)
const streamingContent = ref('')
const messagesEl = ref(null)
const inputEl = ref(null)

watch(currentAgent, () => {
  messages.value = []
})

async function sendMessage(text) {
  if (!text.trim()) return
  const userMsg = text.trim()
  inputText.value = ''
  messages.value.push({ role: 'user', content: userMsg })
  streaming.value = true
  streamingContent.value = ''

  await nextTick()
  scrollToBottom()

  try {
    const res = await createChatStream(projectId.value, {
      message: userMsg,
      agent: currentAgent.value,
    })

    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data:')) {
          const data = line.slice(5).trim()
          if (data === '__done__') continue
          if (data) {
            streamingContent.value += data
            scrollToBottom()
          }
        }
      }
    }

    messages.value.push({
      role: 'assistant',
      content: streamingContent.value,
      agent: currentAgentLabel.value,
    })
  } catch (e) {
    messages.value.push({
      role: 'assistant',
      content: `生成失败: ${e.message}`,
      agent: currentAgentLabel.value,
    })
  } finally {
    streaming.value = false
    streamingContent.value = ''
    scrollToBottom()
  }
}

function handleSend() {
  sendMessage(inputText.value)
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesEl.value) {
      messagesEl.value.scrollTop = messagesEl.value.scrollHeight
    }
  })
}

function formatText(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n/g, '<br>')
}

function copyText(text) {
  navigator.clipboard.writeText(text)
}
</script>

<style scoped>
.chat-workspace {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chat-header {
  padding: 16px 24px;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg-secondary);
}

.chat-title {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 600;
}

.agent-selector {
  display: flex;
  gap: 4px;
}

.agent-btn {
  padding: 6px 12px;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--text-secondary);
  font-size: 12px;
  border: 1px solid transparent;
  transition: all var(--transition);
}

.agent-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.agent-btn.active {
  background: var(--accent-soft);
  color: var(--accent);
  border-color: var(--accent);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
}

.chat-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-muted);
}

.chat-empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

.chat-empty-text {
  font-size: 14px;
  margin-bottom: 24px;
}

.chat-empty-hints {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  max-width: 500px;
}

.hint-btn {
  padding: 8px 14px;
  border-radius: 20px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-size: 12px;
  border: 1px solid var(--border);
  transition: all var(--transition);
}

.hint-btn:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  animation: fadeIn 0.3s ease;
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
  background: var(--bg-tertiary);
}

.message.user .message-avatar {
  background: var(--accent-soft);
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-agent {
  font-size: 11px;
  color: var(--accent);
  margin-bottom: 4px;
  font-weight: 600;
}

.message-text {
  font-size: 14px;
  line-height: 1.8;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-word;
}

.message-actions {
  display: flex;
  gap: 6px;
  margin-top: 8px;
  opacity: 0;
  transition: opacity var(--transition);
}

.message:hover .message-actions {
  opacity: 1;
}

.streaming-text .cursor {
  animation: pulse 1s infinite;
  color: var(--accent);
}

.chat-input-area {
  padding: 16px 24px;
  border-top: 1px solid var(--border);
  background: var(--bg-secondary);
}

.chat-input-wrapper {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.chat-input-wrapper textarea {
  flex: 1;
  min-height: 40px;
  max-height: 120px;
  padding: 10px 14px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  font-size: 14px;
  line-height: 1.5;
}

.send-btn {
  height: 40px;
  padding: 0 20px;
  white-space: nowrap;
}
</style>
