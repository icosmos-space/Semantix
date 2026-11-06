<template>
  <div>
    <div class="toolbar">
      <h2>能力中心</h2>
      <el-button type="primary" @click="showCreate = true">注册能力</el-button>
    </div>
    <el-table :data="items" v-loading="loading">
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="kind" label="类型" width="140" />
      <el-table-column prop="operation" label="操作" width="100" />
      <el-table-column prop="status" label="状态" width="120" />
      <el-table-column prop="source" label="来源" width="120" />
      <el-table-column label="动作" width="160">
        <template #default="{ row }">
          <el-button
            v-if="row.status !== 'published'"
            link
            type="success"
            @click="publish(row.id)"
          >
            发布
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showCreate" title="注册 Capability" width="520px">
      <el-form label-position="top">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.kind" style="width: 100%">
            <el-option label="Semantic Data" value="semantic_data" />
            <el-option label="Functional" value="functional" />
            <el-option label="Knowledge" value="knowledge" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">取消</el-button>
        <el-button type="primary" @click="create">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '@/api/client'
import { useProjectStore } from '@/stores/project'

const projectStore = useProjectStore()
const projectId = computed(() => projectStore.currentProjectId)
const items = ref<any[]>([])
const loading = ref(false)
const showCreate = ref(false)
const form = reactive({
  name: 'semantic.query',
  kind: 'semantic_data',
  description: '自然语言语义查询',
})

async function load() {
  if (!projectId.value) return
  loading.value = true
  try {
    const { data } = await api.get(`/projects/${projectId.value}/capabilities`)
    items.value = data
  } finally {
    loading.value = false
  }
}

async function create() {
  if (!projectId.value) return
  await api.post(`/projects/${projectId.value}/capabilities`, {
    ...form,
    config: { use_demo_rows: true },
  })
  showCreate.value = false
  ElMessage.success('已注册（草稿）')
  await load()
}

async function publish(id: string) {
  if (!projectId.value) return
  await api.post(`/projects/${projectId.value}/capabilities/${id}/publish`)
  ElMessage.success('已发布')
  await load()
}

onMounted(load)
watch(projectId, load)
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
h2 {
  margin: 0;
}
</style>
