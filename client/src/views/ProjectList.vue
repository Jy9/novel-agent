<template>
  <div class="project-list-page">
    <div class="page-header">
      <h1 class="page-title">我的项目</h1>
      <button class="btn btn-primary" @click="showCreate = true">+ 新建小说</button>
    </div>

    <div class="project-grid" v-if="projects.length">
      <div
        v-for="p in projects"
        :key="p.id"
        class="project-card card"
        @click="$router.push(`/project/${p.id}`)"
      >
        <div class="project-card-header">
          <span class="project-card-icon">📖</span>
          <span class="tag tag-accent" v-if="p.genre">{{ p.genre }}</span>
        </div>
        <h3 class="project-card-name">{{ p.name }}</h3>
        <p class="project-card-desc" v-if="p.description">{{ p.description }}</p>
        <div class="project-card-footer">
          <span class="project-card-time">{{ formatDate(p.updated_at) }}</span>
          <button class="btn-icon" @click.stop="deleteProject(p.id)" title="删除">🗑️</button>
        </div>
      </div>
    </div>

    <div class="empty-state" v-else>
      <div class="icon">📖</div>
      <div class="text">还没有小说项目，点击上方按钮创建</div>
    </div>

    <div class="modal-overlay" v-if="showCreate" @click.self="showCreate = false">
      <div class="modal card">
        <h2 class="modal-title">新建小说项目</h2>
        <div class="form-group">
          <label class="label">项目名称</label>
          <input v-model="form.name" placeholder="输入小说名称" />
        </div>
        <div class="form-group">
          <label class="label">类型</label>
          <select v-model="form.genre">
            <option value="">选择类型</option>
            <option value="玄幻">玄幻</option>
            <option value="科幻">科幻</option>
            <option value="悬疑">悬疑</option>
            <option value="言情">言情</option>
            <option value="武侠">武侠</option>
            <option value="都市">都市</option>
            <option value="历史">历史</option>
            <option value="恐怖">恐怖</option>
            <option value="其他">其他</option>
          </select>
        </div>
        <div class="form-group">
          <label class="label">简介</label>
          <textarea v-model="form.description" placeholder="简述小说的核心设定或故事梗概" rows="3"></textarea>
        </div>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="showCreate = false">取消</button>
          <button class="btn btn-primary" @click="createProject" :disabled="!form.name">创建</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { projectApi } from '../api'

const projects = ref([])
const showCreate = ref(false)
const form = ref({ name: '', genre: '', description: '' })

onMounted(loadProjects)

async function loadProjects() {
  projects.value = await projectApi.list()
}

async function createProject() {
  if (!form.value.name) return
  await projectApi.create(form.value)
  form.value = { name: '', genre: '', description: '' }
  showCreate.value = false
  await loadProjects()
}

async function deleteProject(id) {
  if (!confirm('确定删除该项目？所有数据将丢失。')) return
  await projectApi.delete(id)
  await loadProjects()
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`
}
</script>

<style scoped>
.project-list-page {
  padding: 32px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
}

.page-title {
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.project-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.project-card {
  cursor: pointer;
  transition: all var(--transition);
}

.project-card:hover {
  border-color: var(--accent);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.project-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.project-card-icon {
  font-size: 28px;
}

.project-card-name {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 6px;
  color: var(--text-primary);
}

.project-card-desc {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 12px;
}

.project-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.project-card-time {
  font-size: 11px;
  color: var(--text-muted);
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
  width: 440px;
  max-width: 90vw;
}

.modal-title {
  font-family: var(--font-display);
  font-size: 18px;
  margin-bottom: 20px;
  color: var(--text-primary);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}
</style>
