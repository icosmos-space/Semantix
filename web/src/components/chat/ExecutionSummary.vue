<template>
  <el-card shadow="never" class="summary">
    <template #header>执行摘要</template>
    <el-descriptions :column="1" size="small" border>
      <el-descriptions-item label="引擎">{{ summary.engine || '—' }}</el-descriptions-item>
      <el-descriptions-item label="状态">{{ summary.status || '—' }}</el-descriptions-item>
      <el-descriptions-item label="行数">{{ summary.row_count ?? rows.length }}</el-descriptions-item>
      <el-descriptions-item label="耗时(ms)">{{ summary.duration_ms ?? '—' }}</el-descriptions-item>
    </el-descriptions>
    <div v-if="sql" class="sql">
      <div class="label">SQL</div>
      <pre>{{ sql }}</pre>
    </div>
  </el-card>
</template>

<script setup lang="ts">
defineProps<{
  summary: Record<string, unknown>
  sql?: string | null
  rows?: unknown[]
}>()
</script>

<style scoped>
.summary {
  position: sticky;
  top: 12px;
}
.sql {
  margin-top: 12px;
}
.label {
  color: #64748b;
  margin-bottom: 6px;
}
pre {
  background: #0f172a;
  color: #e2e8f0;
  padding: 10px;
  border-radius: 8px;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 12px;
}
</style>
