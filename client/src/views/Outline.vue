<template>
  <div class="outline-page">
    <div class="page-header">
      <h2 class="page-title">📋 大纲编辑</h2>
      <div class="header-actions">
        <select v-model="outline.structure_type" @change="saveOutline" class="structure-select">
          <option value="three_act">三幕式</option>
          <option value="hero_journey">英雄之旅</option>
          <option value="custom">自定义</option>
        </select>
        <button class="btn btn-primary btn-sm" @click="addPlotPoint">+ 添加情节点</button>
      </div>
    </div>

    <div class="plot-points-list">
      <div v-for="(point, i) in outline.plot_points" :key="i" class="plot-point card">
        <div class="plot-point-header">
          <span class="plot-point-order">{{ i + 1 }}</span>
          <select v-model="point.type" @change="saveOutline" class="type-select">
            <option value="setup">铺陈</option>
            <option value="conflict">冲突</option>
            <option value="climax">高潮</option>
            <option value="resolution">结局</option>
          </select>
          <button class="btn-icon" @click="removePlotPoint(i)" title="删除">🗑️</button>
        </div>
        <div class="form-group">
          <label class="label">标题</label>
          <input v-model="point.title" @blur="saveOutline" placeholder="情节点标题" />
        </div>
        <div class="form-group">
          <label class="label">描述</label>
          <textarea v-model="point.description" @blur="saveOutline" placeholder="详细描述" rows="2"></textarea>
        </div>
        <div class="form-group">
          <label class="label">对应章节</label>
          <input v-model.number="point.chapter_index" @blur="saveOutline" type="number" min="0" placeholder="章节序号" />
        </div>
      </div>

      <div class="empty-state" v-if="!outline.plot_points.length" style="padding: 40px;">
        <div class="icon">📋</div>
        <div class="text">还没有情节点，点击上方添加</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRoute } from 'vue-router'
import { outlineApi } from '../../api'

const route = useRoute()
const projectId = route.params.id

const outline = reactive({
  structure_type: 'three_act',
  plot_points: [],
})

onMounted(async () => {
  try {
    const data = await outlineApi.get(projectId)
    outline.structure_type = data.structure_type || 'three_act'
    outline.plot_points = data.plot_points || []
  } catch {}
})

function addPlotPoint() {
  outline.plot_points.push({
    order: outline.plot_points.length,
    title: '',
    description: '',
    chapter_index: outline.plot_points.length,
    type: 'setup',
  })
  saveOutline()
}

function removePlotPoint(index) {
  outline.plot_points.splice(index, 1)
  outline.plot_points.forEach((p, i) => { p.order = i })
  saveOutline()
}

async function saveOutline() {
  try {
    await outlineApi.update(projectId, {
      structure_type: outline.structure_type,
      plot_points: outline.plot_points,
    })
  } catch {}
}
</script>

<style scoped>
.outline-page {
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

.header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.structure-select, .type-select {
  width: auto;
  min-width: 100px;
}

.plot-points-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.plot-point {
  transition: all var(--transition);
}

.plot-point:hover {
  border-color: var(--accent);
}

.plot-point-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.plot-point-order {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--accent-soft);
  color: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
}
</style>
