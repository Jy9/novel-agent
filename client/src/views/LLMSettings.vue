<template>
  <div class="llm-settings-page">
    <div class="page-header">
      <h1 class="page-title">🤖 LLM 模型配置</h1>
    </div>

    <div class="settings-grid">
      <div class="card providers-card">
        <div class="card-header">
          <h3 class="card-title">已配置的模型</h3>
          <button class="btn btn-primary btn-sm" @click="openForm()">+ 添加模型</button>
        </div>

        <div class="provider-list" v-if="providers.length">
          <div v-for="p in providers" :key="p.id" class="provider-item">
            <div class="provider-info">
              <div class="provider-name">
                <span :class="['status-dot', p.api_key ? 'online' : 'offline']"></span>
                {{ p.name }}
              </div>
              <div class="provider-meta">
                <span class="tag tag-accent">{{ p.type }}</span>
                <span class="provider-model">{{ p.model }}</span>
              </div>
            </div>
            <div class="provider-actions">
              <button class="btn btn-sm btn-secondary" @click="testProvider(p)">测试</button>
              <button class="btn-icon" @click="openForm(p)" title="编辑">✏️</button>
              <button class="btn-icon" @click="deleteProvider(p.id)" title="删除">🗑️</button>
            </div>
          </div>
        </div>

        <div class="empty-state" v-else style="padding: 30px;">
          <div class="text">还没有配置模型，点击上方添加</div>
        </div>
      </div>

      <div class="card bindings-card">
        <h3 class="card-title">Agent 绑定</h3>
        <p class="card-desc">为不同的Agent分配不同的模型</p>

        <div class="binding-list">
          <div v-for="a in agentList" :key="a.key" class="binding-item">
            <div class="binding-label">{{ a.icon }} {{ a.label }}Agent</div>
            <select v-model="bindings[a.key]" @change="saveBindings">
              <option value="">未绑定</option>
              <option v-for="p in providers" :key="p.id" :value="p.id">{{ p.name }} ({{ p.model }})</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <div class="test-result card" v-if="testResult">
      <div :class="['test-status', testResult.success ? 'success' : 'error']">
        {{ testResult.success ? '✅ 连接成功' : '❌ 连接失败' }}
      </div>
      <div class="test-response">{{ testResult.success ? testResult.response : testResult.error }}</div>
      <button class="btn btn-sm btn-secondary" @click="testResult = null">关闭</button>
    </div>

    <div class="modal-overlay" v-if="showForm" @click.self="closeForm">
      <div class="modal card">
        <h2 class="modal-title">{{ editingProvider ? '编辑模型' : '添加模型' }}</h2>

        <div class="form-group">
          <label class="label">名称</label>
          <input v-model="form.name" placeholder="如：我的GPT-4o" />
        </div>

        <div class="form-group">
          <label class="label">类型</label>
          <select v-model="form.type">
            <option value="openai">OpenAI</option>
            <option value="anthropic">Anthropic</option>
            <option value="ollama">Ollama (本地)</option>
            <option value="custom">自定义 (OpenAI兼容)</option>
          </select>
        </div>

        <div class="form-group">
          <label class="label">API 地址</label>
          <input v-model="form.api_base" :placeholder="apiBasePlaceholder" />
        </div>

        <div class="form-group">
          <label class="label">API Key</label>
          <input v-model="form.api_key" type="password" :placeholder="editingProvider ? '留空则不修改' : '输入API Key'" />
        </div>

        <div class="form-group">
          <label class="label">模型名称</label>
          <input v-model="form.model" placeholder="如：gpt-4o, claude-3-sonnet, qwen2.5" />
        </div>

        <div class="form-row">
          <div class="form-group" style="flex:1">
            <label class="label">Temperature</label>
            <input v-model.number="form.params.temperature" type="number" min="0" max="2" step="0.1" />
          </div>
          <div class="form-group" style="flex:1">
            <label class="label">Max Tokens</label>
            <input v-model.number="form.params.max_tokens" type="number" min="100" max="128000" step="100" />
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn btn-secondary" @click="closeForm">取消</button>
          <button class="btn btn-secondary" @click="testForm" :disabled="testing">{{ testing ? '测试中...' : '测试连接' }}</button>
          <button class="btn btn-primary" @click="saveProvider" :disabled="!form.name || !form.model">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { llmApi } from '../api'

const providers = ref([])
const bindings = reactive({
  planner_provider_id: '',
  writer_provider_id: '',
  reviewer_provider_id: '',
  character_provider_id: '',
})
const showForm = ref(false)
const editingProvider = ref(null)
const testing = ref(false)
const testResult = ref(null)

const form = ref({
  name: '',
  type: 'openai',
  api_base: '',
  api_key: '',
  model: '',
  params: { temperature: 0.7, max_tokens: 4096 },
})

const agentList = [
  { key: 'planner_provider_id', label: '规划', icon: '🧠' },
  { key: 'writer_provider_id', label: '写作', icon: '✍️' },
  { key: 'reviewer_provider_id', label: '审查', icon: '🔍' },
  { key: 'character_provider_id', label: '角色', icon: '🎭' },
]

const apiBasePlaceholder = computed(() => {
  const map = {
    openai: 'https://api.openai.com/v1',
    anthropic: 'https://api.anthropic.com',
    ollama: 'http://localhost:11434',
    custom: 'https://your-api.com/v1',
  }
  return map[form.value.type] || ''
})

onMounted(async () => {
  await Promise.all([loadProviders(), loadBindings()])
})

async function loadProviders() {
  providers.value = await llmApi.getProviders()
}

async function loadBindings() {
  const b = await llmApi.getBindings()
  Object.keys(bindings).forEach(k => {
    bindings[k] = b[k] || ''
  })
}

function openForm(provider = null) {
  editingProvider.value = provider
  if (provider) {
    form.value = {
      name: provider.name,
      type: provider.type,
      api_base: provider.api_base,
      api_key: '',
      model: provider.model,
      params: { ...provider.params } || { temperature: 0.7, max_tokens: 4096 },
    }
  } else {
    form.value = {
      name: '',
      type: 'openai',
      api_base: '',
      api_key: '',
      model: '',
      params: { temperature: 0.7, max_tokens: 4096 },
    }
  }
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  editingProvider.value = null
}

async function saveProvider() {
  const data = { ...form.value }
  if (editingProvider.value) {
    if (!data.api_key) delete data.api_key
    await llmApi.updateProvider(editingProvider.value.id, data)
  } else {
    await llmApi.createProvider(data)
  }
  closeForm()
  await loadProviders()
}

async function deleteProvider(id) {
  if (!confirm('确定删除该模型配置？')) return
  await llmApi.deleteProvider(id)
  await loadProviders()
}

async function testProvider(provider) {
  testing.value = true
  testResult.value = null
  try {
    testResult.value = await llmApi.testConnection({ provider_id: provider.id })
  } catch (e) {
    testResult.value = { success: false, error: e.message }
  } finally {
    testing.value = false
  }
}

async function testForm() {
  testing.value = true
  testResult.value = null
  try {
    testResult.value = await llmApi.testConnection({
      type: form.value.type,
      api_base: form.value.api_base,
      api_key: form.value.api_key,
      model: form.value.model,
    })
  } catch (e) {
    testResult.value = { success: false, error: e.message }
  } finally {
    testing.value = false
  }
}

async function saveBindings() {
  const data = {}
  Object.keys(bindings).forEach(k => {
    if (bindings[k]) data[k] = bindings[k]
  })
  await llmApi.updateBindings(data)
}
</script>

<style scoped>
.llm-settings-page {
  padding: 32px;
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 28px;
}

.page-title {
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 700;
}

.settings-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.card-desc {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 16px;
}

.provider-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.provider-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
}

.provider-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.provider-name {
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-dot.online {
  background: var(--success);
}

.status-dot.offline {
  background: var(--text-muted);
}

.provider-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.provider-model {
  font-size: 12px;
  color: var(--text-muted);
}

.provider-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.binding-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.binding-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.binding-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.binding-item select {
  width: 100%;
}

.test-result {
  margin-top: 20px;
}

.test-status {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
}

.test-status.success {
  color: var(--success);
}

.test-status.error {
  color: var(--error);
}

.test-response {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 10px;
  padding: 8px 12px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-sm);
}

.form-row {
  display: flex;
  gap: 12px;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal {
  width: 480px;
  max-width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-title {
  font-family: var(--font-display);
  font-size: 18px;
  margin-bottom: 20px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

@media (max-width: 768px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }
}
</style>
