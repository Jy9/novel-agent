<template>
  <div class="chapters-page">
    <div class="page-header">
      <h2 class="page-title">📑 章节管理</h2>
      <button class="btn btn-primary btn-sm" @click="addChapter">+ 新建章节</button>
    </div>

    <div class="chapter-list" v-if="chapters.length">
      <div v-for="ch in chapters" :key="ch.id" class="chapter-item card" @click="selectChapter(ch)">
        <div class="chapter-item-left">
          <span class="chapter-order">{{ ch.order + 1 }}</span>
          <div class="chapter-info">
            <span class="chapter-title">{{ ch.title || '未命名章节' }}</span>
            <span :class="['tag', statusTag(ch.status)]">{{ statusLabel(ch.status) }}</span>
          </div>
        </div>
        <div class="chapter-item-right">
          <span class="chapter-words" v-if="ch.content">{{ ch.content.length }} 字</span>
          <button class="btn-icon" @click.stop="deleteChapter(ch.id)" title="删除">🗑️</button>
        </div>
      </div>
    </div>

    <div class="empty-state" v-else>
      <div class="icon">📑</div>
      <div class="text">还没有章节，点击上方创建</div>
    </div>

    <div class="chapter-editor card" v-if="currentChapter">
      <div class="editor-header">
        <input v-model="currentChapter.title" class="editor-title" @blur="saveCurrentChapter" placeholder="章节标题" />
        <div class="editor-actions">
          <select v-model="currentChapter.status" @change="saveCurrentChapter">
            <option value="draft">草稿</option>
            <option value="reviewed">已审查</option>
            <option value="final">定稿</option>
          </select>
          <button class="btn btn-sm btn-secondary" @click="saveCurrentChapter">保存</button>
        </div>
      </div>
      <textarea
        v-model="currentChapter.content"
        class="editor-content"
        @blur="saveCurrentChapter"
        placeholder="在这里编写章节内容..."
      ></textarea>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { chapterApi } from '../../api'

const route = useRoute()
const projectId = route.params.id

const chapters = ref([])
const currentChapter = ref(null)

onMounted(loadChapters)

async function loadChapters() {
  chapters.value = await chapterApi.list(projectId)
}

async function addChapter() {
  const order = chapters.value.length
  await chapterApi.create(projectId, { title: `第${order + 1}章`, order })
  await loadChapters()
}

function selectChapter(ch) {
  currentChapter.value = { ...ch }
}

async function saveCurrentChapter() {
  if (!currentChapter.value) return
  try {
    await chapterApi.update(projectId, currentChapter.value.id, {
      title: currentChapter.value.title,
      content: currentChapter.value.content,
      status: currentChapter.value.status,
    })
    await loadChapters()
  } catch {}
}

async function deleteChapter(id) {
  if (!confirm('确定删除该章节？')) return
  if (currentChapter.value?.id === id) currentChapter.value = null
  await chapterApi.delete(projectId, id)
  await loadChapters()
}

function statusTag(s) {
  return { draft: 'tag-warning', reviewed: 'tag-accent', final: 'tag-success' }[s] || 'tag-warning'
}

function statusLabel(s) {
  return { draft: '草稿', reviewed: '已审查', final: '定稿' }[s] || '草稿'
}
</script>

<style scoped>
.chapters-page {
  padding: 24px;
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 20px;
  height: 100%;
}

.page-header {
  grid-column: 1 / -1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 600;
}

.chapter-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  overflow-y: auto;
  max-height: calc(100vh - 140px);
}

.chapter-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  cursor: pointer;
  transition: all var(--transition);
}

.chapter-item:hover {
  border-color: var(--accent);
}

.chapter-item-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.chapter-order {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: var(--text-secondary);
}

.chapter-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.chapter-title {
  font-size: 13px;
  font-weight: 500;
}

.chapter-item-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.chapter-words {
  font-size: 11px;
  color: var(--text-muted);
}

.chapter-editor {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 140px);
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
}

.editor-title {
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 600;
  background: transparent;
  border: none;
  flex: 1;
}

.editor-title:focus {
  outline: none;
}

.editor-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.editor-actions select {
  width: auto;
  min-width: 80px;
}

.editor-content {
  flex: 1;
  resize: none;
  min-height: 300px;
  font-size: 14px;
  line-height: 2;
  font-family: var(--font-body);
  background: transparent;
  border: none;
  padding: 0;
}

.editor-content:focus {
  outline: none;
  border: none;
}
</style>
