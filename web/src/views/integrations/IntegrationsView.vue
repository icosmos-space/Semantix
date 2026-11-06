<template>
  <div>
    <div class="toolbar">
      <h2>系统集成</h2>
      <el-button type="primary" :disabled="!projectId" @click="showCreate = true">
        新建集成
      </el-button>
    </div>
    <el-alert
      v-if="!projectId"
      type="warning"
      title="请先选择或创建项目"
      :closable="false"
      style="margin-bottom: 16px"
    />

    <el-row :gutter="16">
      <el-col :span="8">
        <el-table
          :data="integrations"
          v-loading="loading"
          highlight-current-row
          @current-change="onSelectIntegration"
        >
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="base_url" label="Base URL" show-overflow-tooltip />
        </el-table>
      </el-col>
      <el-col :span="16">
        <template v-if="current">
          <div class="panel-toolbar">
            <h3>{{ current.name }}</h3>
            <div>
              <el-button @click="showImport = true">导入 OpenAPI</el-button>
              <el-button type="primary" :disabled="!selectedOverlay" @click="showPlayground = true">
                Playground
              </el-button>
            </div>
          </div>
          <el-table
            :data="overlays"
            v-loading="overlayLoading"
            highlight-current-row
            @current-change="onSelectOverlay"
          >
            <el-table-column prop="name" label="工具名" width="160" />
            <el-table-column prop="method" label="方法" width="80" />
            <el-table-column prop="path" label="路径" show-overflow-tooltip />
            <el-table-column label="只读确认" width="100">
              <template #default="{ row }">
                <el-tag :type="row.read_only_confirmed ? 'success' : 'info'" size="small">
                  {{ row.read_only_confirmed ? '是' : '否' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="动作" width="200">
              <template #default="{ row }">
                <el-button link type="primary" @click="openEditor(row)">编辑 Overlay</el-button>
                <el-button
                  link
                  type="success"
                  :disabled="!row.read_only_confirmed"
                  @click="publishOverlay(row.id)"
                >
                  发布
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </template>
        <el-empty v-else description="选择左侧集成查看工具" />
      </el-col>
    </el-row>

    <el-dialog v-model="showCreate" title="新建 HTTP 集成" width="520px">
      <el-form label-position="top">
        <el-form-item label="名称"><el-input v-model="createForm.name" /></el-form-item>
        <el-form-item label="Base URL">
          <el-input v-model="createForm.base_url" placeholder="http://127.0.0.1:18080" />
        </el-form-item>
        <el-form-item label="Auth">
          <el-select v-model="createForm.auth_type" style="width: 100%">
            <el-option label="none" value="none" />
            <el-option label="bearer" value="bearer" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="createForm.auth_type === 'bearer'" label="Token">
          <el-input v-model="createForm.auth_token" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="createIntegration">创建</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showImport" title="导入 OpenAPI JSON" width="640px">
      <el-input
        v-model="importText"
        type="textarea"
        :rows="14"
        placeholder='粘贴 OpenAPI JSON，例如含 GET /api/device/{device_id}/alarms'
      />
      <template #footer>
        <el-button @click="showImport = false">取消</el-button>
        <el-button type="primary" :loading="importing" @click="importOpenapi">导入</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showEditor" title="工具语义 Overlay" width="560px">
      <el-form v-if="editForm" label-position="top">
        <el-form-item label="名称"><el-input v-model="editForm.name" /></el-form-item>
        <el-form-item label="描述">
          <el-input v-model="editForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="意图（逗号分隔）">
          <el-input v-model="editForm.intentsText" />
        </el-form-item>
        <el-form-item label="确认只读">
          <el-switch v-model="editForm.read_only_confirmed" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditor = false">取消</el-button>
        <el-button type="primary" @click="saveOverlay">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showPlayground" title="Functional Playground" width="560px">
      <el-form label-position="top">
        <el-form-item label="Input JSON">
          <el-input v-model="playgroundInput" type="textarea" :rows="6" />
        </el-form-item>
        <el-form-item v-if="playgroundResult" label="结果">
          <pre class="result">{{ playgroundResult }}</pre>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPlayground = false">关闭</el-button>
        <el-button type="primary" :loading="invoking" @click="invokePlayground">执行</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '@/api/client'
import { useProjectStore } from '@/stores/project'

type Integration = { id: string; name: string; base_url: string; auth_type: string }
type Overlay = {
  id: string
  operation_id: string
  name: string
  description: string
  method: string
  path: string
  read_only_confirmed: boolean
  capability_id: string | null
  intents: string[]
}

const projectStore = useProjectStore()
const projectId = computed(() => projectStore.currentProjectId)

const integrations = ref<Integration[]>([])
const overlays = ref<Overlay[]>([])
const current = ref<Integration | null>(null)
const selectedOverlay = ref<Overlay | null>(null)
const loading = ref(false)
const overlayLoading = ref(false)
const saving = ref(false)
const importing = ref(false)
const invoking = ref(false)

const showCreate = ref(false)
const showImport = ref(false)
const showEditor = ref(false)
const showPlayground = ref(false)
const importText = ref('')
const playgroundInput = ref('{\n  "device_id": "tacey_002"\n}')
const playgroundResult = ref('')

const createForm = reactive({
  name: 'device-api',
  base_url: 'http://127.0.0.1:18080',
  auth_type: 'none',
  auth_token: '',
})

const editForm = ref<{
  id: string
  name: string
  description: string
  intentsText: string
  read_only_confirmed: boolean
} | null>(null)

async function loadIntegrations() {
  if (!projectId.value) {
    integrations.value = []
    current.value = null
    overlays.value = []
    return
  }
  loading.value = true
  try {
    const { data } = await api.get<Integration[]>(`/projects/${projectId.value}/integrations`)
    integrations.value = data
  } finally {
    loading.value = false
  }
}

async function loadOverlays() {
  if (!projectId.value || !current.value) {
    overlays.value = []
    return
  }
  overlayLoading.value = true
  try {
    const { data } = await api.get<Overlay[]>(
      `/projects/${projectId.value}/integrations/${current.value.id}/overlays`,
    )
    overlays.value = data
  } finally {
    overlayLoading.value = false
  }
}

function onSelectIntegration(row: Integration | null) {
  current.value = row
  selectedOverlay.value = null
  void loadOverlays()
}

function onSelectOverlay(row: Overlay | null) {
  selectedOverlay.value = row
}

async function createIntegration() {
  if (!projectId.value) return
  saving.value = true
  try {
    await api.post(`/projects/${projectId.value}/integrations`, {
      name: createForm.name,
      base_url: createForm.base_url,
      auth_type: createForm.auth_type,
      auth_token: createForm.auth_token || null,
    })
    showCreate.value = false
    ElMessage.success('集成已创建')
    await loadIntegrations()
  } catch {
    ElMessage.error('创建失败')
  } finally {
    saving.value = false
  }
}

async function importOpenapi() {
  if (!projectId.value || !current.value) return
  importing.value = true
  try {
    const openapi = JSON.parse(importText.value)
    const { data } = await api.post(
      `/projects/${projectId.value}/integrations/${current.value.id}/import`,
      { openapi },
    )
    showImport.value = false
    ElMessage.success(`导入完成：overlay ${data.overlays_created}，能力 ${data.capabilities_created}`)
    await loadOverlays()
  } catch {
    ElMessage.error('导入失败（检查 JSON）')
  } finally {
    importing.value = false
  }
}

function openEditor(row: Overlay) {
  editForm.value = {
    id: row.id,
    name: row.name,
    description: row.description,
    intentsText: (row.intents || []).join(', '),
    read_only_confirmed: row.read_only_confirmed,
  }
  showEditor.value = true
}

async function saveOverlay() {
  if (!projectId.value || !editForm.value) return
  const intents = editForm.value.intentsText
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean)
  await api.patch(`/projects/${projectId.value}/integrations/overlays/${editForm.value.id}`, {
    name: editForm.value.name,
    description: editForm.value.description,
    intents,
    read_only_confirmed: editForm.value.read_only_confirmed,
  })
  showEditor.value = false
  ElMessage.success('Overlay 已保存')
  await loadOverlays()
}

async function publishOverlay(id: string) {
  if (!projectId.value) return
  try {
    await api.post(`/projects/${projectId.value}/integrations/overlays/${id}/publish`)
    ElMessage.success('已发布为 Capability')
    await loadOverlays()
  } catch {
    ElMessage.error('发布失败（需先确认只读）')
  }
}

async function invokePlayground() {
  if (!projectId.value || !selectedOverlay.value?.capability_id) {
    ElMessage.warning('请先选择已关联 capability 的工具，并完成发布')
    return
  }
  invoking.value = true
  playgroundResult.value = ''
  try {
    const input = JSON.parse(playgroundInput.value)
    const { data } = await api.post(
      `/projects/${projectId.value}/capabilities/${selectedOverlay.value.capability_id}/execute`,
      { input },
    )
    playgroundResult.value = JSON.stringify(data, null, 2)
  } catch (e: any) {
    playgroundResult.value = JSON.stringify(e?.response?.data || { error: String(e) }, null, 2)
    ElMessage.error('执行失败')
  } finally {
    invoking.value = false
  }
}

onMounted(loadIntegrations)
watch(projectId, loadIntegrations)
</script>

<style scoped>
.toolbar,
.panel-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
h2,
h3 {
  margin: 0;
}
.result {
  margin: 0;
  max-height: 240px;
  overflow: auto;
  background: #0f172a;
  color: #e2e8f0;
  padding: 12px;
  border-radius: 8px;
  font-size: 12px;
}
</style>
