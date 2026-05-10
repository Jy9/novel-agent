<template>
  <div class="characters-page">
    <div class="page-header">
      <h2 class="page-title">👥 角色管理</h2>
      <button class="btn btn-primary btn-sm" @click="openForm()">+ 新建角色</button>
    </div>

    <div class="character-grid" v-if="characters.length">
      <div v-for="c in characters" :key="c.id" class="character-card card">
        <div class="character-avatar">{{ c.name[0] }}</div>
        <h3 class="character-name">{{ c.name }}</h3>
        <p class="character-personality" v-if="c.personality">{{ c.personality }}</p>
        <div class="character-details" v-if="c.background">
          <span class="detail-label">背景:</span> {{ c.background }}
        </div>
        <div class="character-details" v-if="c.speaking_style">
          <span class="detail-label">说话风格:</span> {{ c.speaking_style }}
        </div>
        <div class="character-actions">
          <button class="btn btn-sm btn-secondary" @click="openForm(c)">编辑</button>
          <button class="btn btn-sm btn-danger" @click="deleteCharacter(c.id)">删除</button>
        </div>
      </div>
    </div>

    <div class="empty-state" v-else>
      <div class="icon">👥</div>
      <div class="text">还没有角色，点击上方创建</div>
    </div>

    <div class="modal-overlay" v-if="showForm" @click.self="closeForm">
      <div class="modal card">
        <h2 class="modal-title">{{ editing ? '编辑角色' : '新建角色' }}</h2>
        <div class="form-group">
          <label class="label">姓名</label>
          <input v-model="form.name" placeholder="角色姓名" />
        </div>
        <div class="form-group">
          <label class="label">性格</label>
          <textarea v-model="form.personality" placeholder="描述角色的性格特点" rows="2"></textarea>
        </div>
        <div class="form-group">
          <label class="label">背景故事</label>
          <textarea v-model="form.background" placeholder="角色的背景故事" rows="2"></textarea>
        </div>
        <div class="form-group">
          <label class="label">外貌</label>
          <input v-model="form.appearance" placeholder="描述角色的外貌" />
        </div>
        <div class="form-group">
          <label class="label">说话风格</label>
          <input v-model="form.speaking_style" placeholder="如：冷静理性、热情活泼" />
        </div>
        <div class="form-group">
          <label class="label">角色弧线</label>
          <textarea v-model="form.arc_description" placeholder="角色在故事中的成长变化" rows="2"></textarea>
        </div>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="closeForm">取消</button>
          <button class="btn btn-primary" @click="saveCharacter" :disabled="!form.name">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { characterApi } from '../../api'

const route = useRoute()
const projectId = route.params.id

const characters = ref([])
const showForm = ref(false)
const editing = ref(null)
const form = ref({
  name: '', personality: '', background: '',
  appearance: '', speaking_style: '', arc_description: '',
})

onMounted(loadCharacters)

async function loadCharacters() {
  characters.value = await characterApi.list(projectId)
}

function openForm(c = null) {
  editing.value = c
  if (c) {
    form.value = { ...c }
  } else {
    form.value = {
      name: '', personality: '', background: '',
      appearance: '', speaking_style: '', arc_description: '',
    }
  }
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  editing.value = null
}

async function saveCharacter() {
  if (!form.value.name) return
  if (editing.value) {
    await characterApi.update(projectId, editing.value.id, form.value)
  } else {
    await characterApi.create(projectId, form.value)
  }
  closeForm()
  await loadCharacters()
}

async function deleteCharacter(id) {
  if (!confirm('确定删除该角色？')) return
  await characterApi.delete(projectId, id)
  await loadCharacters()
}
</script>

<style scoped>
.characters-page {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 600;
}

.character-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}

.character-card {
  text-align: center;
  transition: all var(--transition);
}

.character-card:hover {
  border-color: var(--accent);
}

.character-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--accent-soft);
  color: var(--accent);
  font-size: 22px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  font-family: var(--font-display);
}

.character-name {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 6px;
}

.character-personality {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.character-details {
  font-size: 12px;
  color: var(--text-muted);
  text-align: left;
  margin-bottom: 4px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.detail-label {
  color: var(--text-secondary);
}

.character-actions {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 12px;
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
</style>
