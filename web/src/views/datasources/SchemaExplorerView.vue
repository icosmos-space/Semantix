<template>
  <div>
    <div class="toolbar">
      <h2>Schema Explorer</h2>
      <el-button type="primary" :loading="syncing" @click="sync">刷新元数据</el-button>
    </div>
    <el-tree v-loading="loading" :data="tree" default-expand-all />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '@/api/client'
import { useProjectStore } from '@/stores/project'

type SchemaPayload = {
  database: string
  tables: Array<{
    schema: string
    name: string
    columns: Array<{ name: string; type: string; nullable: boolean }>
  }>
}

const route = useRoute()
const projectStore = useProjectStore()
const loading = ref(false)
const syncing = ref(false)
const schema = ref<SchemaPayload | null>(null)
const datasourceId = computed(() => String(route.params.id))

const tree = computed(() => {
  if (!schema.value) return []
  const bySchema = new Map<string, any>()
  for (const t of schema.value.tables) {
    if (!bySchema.has(t.schema)) {
      bySchema.set(t.schema, { label: t.schema, children: [] })
    }
    bySchema.get(t.schema).children.push({
      label: t.name,
      children: t.columns.map((c) => ({
        label: `${c.name}: ${c.type}${c.nullable ? '' : ' NOT NULL'}`,
      })),
    })
  }
  return [{ label: schema.value.database, children: [...bySchema.values()] }]
})

async function load() {
  const projectId = projectStore.currentProjectId
  if (!projectId) return
  loading.value = true
  try {
    const { data } = await api.get<SchemaPayload>(
      `/projects/${projectId}/datasources/${datasourceId.value}/schema`,
    )
    schema.value = data
  } catch {
    ElMessage.error('加载 Schema 失败')
  } finally {
    loading.value = false
  }
}

async function sync() {
  const projectId = projectStore.currentProjectId
  if (!projectId) return
  syncing.value = true
  try {
    const { data } = await api.post<SchemaPayload>(
      `/projects/${projectId}/datasources/${datasourceId.value}/schema/sync`,
    )
    schema.value = data
    ElMessage.success('已刷新')
  } catch {
    ElMessage.error('刷新失败')
  } finally {
    syncing.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
h2 {
  margin: 0;
}
</style>
