<template>
  <div>
    <h2>工作台</h2>
    <p class="hint">Phase 0 占位：后续将展示数据源健康、指标与查询统计。</p>
    <el-row :gutter="16">
      <el-col :span="6" v-for="card in cards" :key="card.title">
        <el-card shadow="never">
          <div class="label">{{ card.title }}</div>
          <div class="value">{{ card.value }}</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
const cards = [
  { title: '数据源', value: '—' },
  { title: '语义模型', value: '—' },
  { title: '已发布指标', value: '—' },
  { title: 'Capabilities', value: '—' },
]
</script>

<style scoped>
h2 {
  margin: 0 0 8px;
}
.hint {
  color: #64748b;
  margin-bottom: 20px;
}
.label {
  color: #64748b;
  font-size: 13px;
}
.value {
  margin-top: 8px;
  font-size: 28px;
  font-weight: 600;
}
</style>
