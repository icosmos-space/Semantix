<template>
  <div>
    <div class="toolbar">
      <h2>数据源</h2>
      <el-button type="primary" :disabled="!projectId" @click="showCreate = true">
        新建数据源
      </el-button>
    </div>
    <el-alert
      v-if="!projectId"
      type="warning"
      title="请先选择或创建项目"
      :closable="false"
      style="margin-bottom: 16px"
    />
    <el-table :data="items" v-loading="loading">
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="type" label="类型" width="120" />
      <el-table-column label="连接" min-width="220">
        <template #default="{ row }">
          {{ row.host }}:{{ row.port }}/{{ row.database }}
        </template>
      </el-table-column>
      <el-table-column prop="read_only" label="只读" width="90">
        <template #default="{ row }">
          <el-tag :type="row.read_only ? 'success' : 'danger'" size="small">
            {{ row.read_only ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220">
        <template #default="{ row }">
          <el-button link type="primary" @click="test(row.id)">测试连接</el-button>
          <el-button link type="primary" @click="goSchema(row.id)">Schema</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showCreate" title="新建 PostgreSQL 数据源" width="520px">
      <el-form label-position="top">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="Host"><el-input v-model="form.host" /></el-form-item>
        <el-form-item label="Port"><el-input-number v-model="form.port" :min="1" /></el-form-item>
        <el-form-item label="Database"><el-input v-model="form.database" /></el-form-item>
        <el-form-item label="Username"><el-input v-model="form.username" /></el-form-item>
        <el-form-item label="Password">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="create">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '@/api/client'
import { useProjectStore } from '@/stores/project'

type DS = {
  id: string
  name: string
  type: string
  host: string
  port: number
  database: string
  read_only: boolean
}

const projectStore = useProjectStore()
const router = useRouter()
const projectId = computed(() => projectStore.currentProjectId)
const items = ref<DS[]>([])
const loading = ref(false)
const showCreate = ref(false)
const saving = ref(false)
const form = reactive({
  name: '',
  type: 'postgres',
  host: 'localhost',
  port: 5432,
  database: '',
  username: '',
  password: '',
  read_only: true,
})

async function load() {
  if (!projectId.value) {
    items.value = []
    return
  }
  loading.value = true
  try {
    const { data } = await api.get<DS[]>(`/projects/${projectId.value}/datasources`)
    items.value = data
  } finally {
    loading.value = false
  }
}

async function create() {
  if (!projectId.value) return
  saving.value = true
  try {
    await api.post(`/projects/${projectId.value}/datasources`, { ...form })
    showCreate.value = false
    ElMessage.success('已创建（请使用只读数据库账号）')
    await load()
  } catch {
    ElMessage.error('创建失败')
  } finally {
    saving.value = false
  }
}

async function test(id: string) {
  if (!projectId.value) return
  try {
    await api.post(`/projects/${projectId.value}/datasources/${id}/test`)
    ElMessage.success('连接成功')
  } catch {
    ElMessage.error('连接失败')
  }
}

function goSchema(id: string) {
  router.push(`/datasources/${id}/schema`)
}

onMounted(load)
watch(projectId, load)
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
