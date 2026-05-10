<template>
  <div class="worldview-page">
    <div class="page-header">
      <h2 class="page-title">🌍 世界观设定</h2>
      <button class="btn btn-primary btn-sm" @click="saveWorldview">保存</button>
    </div>

    <div class="worldview-form card">
      <div class="form-group">
        <label class="label">地理环境</label>
        <textarea v-model="worldview.geography" placeholder="描述故事发生的地理环境、重要地点" rows="3"></textarea>
      </div>
      <div class="form-group">
        <label class="label">历史背景</label>
        <textarea v-model="worldview.history" placeholder="重要的历史事件、时代背景" rows="3"></textarea>
      </div>
      <div class="form-group">
        <label class="label">魔法/超自然体系</label>
        <textarea v-model="worldview.magic_system" placeholder="如果有魔法或超自然力量，描述其规则和限制" rows="3"></textarea>
      </div>
      <div class="form-group">
        <label class="label">科技水平</label>
        <input v-model="worldview.tech_level" placeholder="如：中世纪、蒸汽朋克、赛博朋克、星际文明" />
      </div>
      <div class="form-group">
        <label class="label">社会结构</label>
        <textarea v-model="worldview.social_structure" placeholder="政治体制、阶级结构、重要组织" rows="3"></textarea>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { worldviewApi } from '../../api'

const route = useRoute()
const projectId = route.params.id

const worldview = reactive({
  geography: '',
  history: '',
  magic_system: '',
  tech_level: '',
  social_structure: '',
  custom_fields: {},
})

onMounted(async () => {
  try {
    const data = await worldviewApi.get(projectId)
    Object.keys(worldview).forEach(k => {
      if (data[k] !== undefined) worldview[k] = data[k]
    })
  } catch {}
})

async function saveWorldview() {
  try {
    await worldviewApi.update(projectId, { ...worldview })
    alert('保存成功')
  } catch (e) {
    alert('保存失败: ' + e.message)
  }
}
</script>

<style scoped>
.worldview-page {
  padding: 24px;
  max-width: 800px;
  margin: 0 auto;
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

.worldview-form {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
</style>
