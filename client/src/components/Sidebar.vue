<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="logo">
        <span class="logo-icon">📖</span>
        <span class="logo-text">小说Agent</span>
      </div>
    </div>

    <nav class="sidebar-nav" v-if="currentProject">
      <div class="nav-section">
        <div class="nav-section-title">创作</div>
        <router-link :to="`/project/${currentProject.id}`" class="nav-item" active-class="active">
          <span class="nav-icon">🖊️</span> 创作工作台
        </router-link>
        <router-link :to="`/project/${currentProject.id}/outline`" class="nav-item" active-class="active">
          <span class="nav-icon">📋</span> 大纲
        </router-link>
        <router-link :to="`/project/${currentProject.id}/characters`" class="nav-item" active-class="active">
          <span class="nav-icon">👥</span> 角色
        </router-link>
        <router-link :to="`/project/${currentProject.id}/worldview`" class="nav-item" active-class="active">
          <span class="nav-icon">🌍</span> 世界观
        </router-link>
        <router-link :to="`/project/${currentProject.id}/chapters`" class="nav-item" active-class="active">
          <span class="nav-icon">📑</span> 章节
        </router-link>
      </div>
    </nav>

    <div class="sidebar-divider"></div>

    <nav class="sidebar-nav">
      <div class="nav-section">
        <div class="nav-section-title">系统</div>
        <router-link to="/settings/llm" class="nav-item" active-class="active">
          <span class="nav-icon">🤖</span> LLM配置
        </router-link>
        <router-link to="/" class="nav-item" active-class="active">
          <span class="nav-icon">📚</span> 我的项目
        </router-link>
      </div>
    </nav>

    <div class="sidebar-footer" v-if="currentProject">
      <div class="project-badge">
        <span class="project-name">{{ currentProject.name }}</span>
        <span class="project-genre" v-if="currentProject.genre">{{ currentProject.genre }}</span>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { projectApi } from '../api'

const route = useRoute()
const currentProject = ref(null)

watch(
  () => route.params.id,
  async (id) => {
    if (id) {
      try {
        currentProject.value = await projectApi.get(id)
      } catch {
        currentProject.value = null
      }
    } else {
      currentProject.value = null
    }
  },
  { immediate: true }
)
</script>

<style scoped>
.sidebar {
  width: var(--sidebar-width);
  min-width: var(--sidebar-width);
  height: 100%;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.sidebar-header {
  padding: 20px 20px 16px;
  border-bottom: 1px solid var(--border);
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 700;
  color: var(--accent);
  letter-spacing: 2px;
}

.sidebar-nav {
  padding: 12px 12px 0;
}

.nav-section {
  margin-bottom: 8px;
}

.nav-section-title {
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 1px;
  padding: 8px 12px 6px;
  font-weight: 600;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: 13px;
  transition: all var(--transition);
  cursor: pointer;
  text-decoration: none;
}

.nav-item:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.nav-item.active {
  background: var(--accent-soft);
  color: var(--accent);
}

.nav-icon {
  font-size: 15px;
  width: 20px;
  text-align: center;
}

.sidebar-divider {
  height: 1px;
  background: var(--border);
  margin: 8px 20px;
}

.sidebar-footer {
  margin-top: auto;
  padding: 16px 20px;
  border-top: 1px solid var(--border);
}

.project-badge {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.project-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.project-genre {
  font-size: 11px;
  color: var(--text-muted);
}
</style>
