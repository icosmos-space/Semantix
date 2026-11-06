<template>
  <div>
    <h2>语义中心</h2>
    <el-tabs v-model="tab">
      <el-tab-pane label="模型" name="models">
        <div class="toolbar">
          <el-button type="primary" @click="showModel = true">新建模型</el-button>
        </div>
        <el-table :data="models">
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="table_name" label="表" />
          <el-table-column prop="description" label="说明" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="指标" name="metrics">
        <div class="toolbar">
          <el-button type="primary" @click="showMetric = true">新建指标</el-button>
        </div>
        <el-table :data="metrics">
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="model_name" label="模型" />
          <el-table-column prop="expression" label="表达式" />
          <el-table-column prop="status" label="状态" width="100" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="MDL" name="mdl">
        <el-input v-model="yamlText" type="textarea" :rows="16" />
        <div class="toolbar" style="margin-top: 12px">
          <el-button type="primary" :loading="savingMdl" @click="saveMdl">保存草稿</el-button>
          <el-button
            type="success"
            :disabled="!latestDraftId"
            :loading="publishing"
            @click="publishMdl"
          >
            发布最新草稿
          </el-button>
        </div>
        <el-table :data="revisions" style="margin-top: 12px">
          <el-table-column prop="id" label="Revision" width="320" />
          <el-table-column prop="status" label="状态" width="120" />
          <el-table-column prop="note" label="备注" />
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="showModel" title="新建语义模型" width="480px">
      <el-form label-position="top">
        <el-form-item label="名称"><el-input v-model="modelForm.name" /></el-form-item>
        <el-form-item label="表名"><el-input v-model="modelForm.table_name" /></el-form-item>
        <el-form-item label="说明"><el-input v-model="modelForm.description" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showModel = false">取消</el-button>
        <el-button type="primary" @click="createModel">创建</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showMetric" title="新建指标" width="520px">
      <el-form label-position="top">
        <el-form-item label="名称"><el-input v-model="metricForm.name" /></el-form-item>
        <el-form-item label="模型"><el-input v-model="metricForm.model_name" /></el-form-item>
        <el-form-item label="表达式"><el-input v-model="metricForm.expression" type="textarea" /></el-form-item>
        <el-form-item label="维度（逗号分隔）">
          <el-input v-model="metricForm.dimensionsText" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showMetric = false">取消</el-button>
        <el-button type="primary" @click="createMetric">创建</el-button>
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
const tab = ref('models')
const models = ref<any[]>([])
const metrics = ref<any[]>([])
const revisions = ref<any[]>([])
const yamlText = ref(`models:
  - name: devices
    table: devices
    columns:
      - name: device_id
        type: string
metrics:
  - name: device_online_rate
    model: devices
    expression: "1.0"
    dimensions: [project_id]
`)
const showModel = ref(false)
const showMetric = ref(false)
const savingMdl = ref(false)
const publishing = ref(false)
const modelForm = reactive({ name: '', table_name: '', description: '' })
const metricForm = reactive({
  name: '',
  model_name: '',
  expression: '',
  dimensionsText: 'project_id',
})
const latestDraftId = computed(
  () => revisions.value.find((r) => r.status === 'draft')?.id as string | undefined,
)

async function load() {
  if (!projectId.value) return
  const [m, met, rev] = await Promise.all([
    api.get(`/projects/${projectId.value}/semantic/models`),
    api.get(`/projects/${projectId.value}/semantic/metrics`),
    api.get(`/projects/${projectId.value}/semantic/mdl/revisions`),
  ])
  models.value = m.data
  metrics.value = met.data
  revisions.value = rev.data
  if (rev.data[0]?.yaml_text) yamlText.value = rev.data[0].yaml_text
}

async function createModel() {
  if (!projectId.value) return
  await api.post(`/projects/${projectId.value}/semantic/models`, {
    ...modelForm,
    columns: [],
  })
  showModel.value = false
  ElMessage.success('模型已创建')
  await load()
}

async function createMetric() {
  if (!projectId.value) return
  await api.post(`/projects/${projectId.value}/semantic/metrics`, {
    name: metricForm.name,
    model_name: metricForm.model_name,
    expression: metricForm.expression,
    dimensions: metricForm.dimensionsText
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean),
  })
  showMetric.value = false
  ElMessage.success('指标已创建')
  await load()
}

async function saveMdl() {
  if (!projectId.value) return
  savingMdl.value = true
  try {
    await api.post(`/projects/${projectId.value}/semantic/mdl/revisions`, {
      yaml_text: yamlText.value,
      note: 'studio draft',
    })
    ElMessage.success('MDL 草稿已保存')
    await load()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '保存失败')
  } finally {
    savingMdl.value = false
  }
}

async function publishMdl() {
  if (!projectId.value || !latestDraftId.value) return
  publishing.value = true
  try {
    await api.post(
      `/projects/${projectId.value}/semantic/mdl/revisions/${latestDraftId.value}/publish`,
    )
    ElMessage.success('已发布')
    await load()
  } catch {
    ElMessage.error('发布失败')
  } finally {
    publishing.value = false
  }
}

onMounted(load)
watch(projectId, load)
</script>

<style scoped>
.toolbar {
  margin-bottom: 12px;
}
h2 {
  margin-top: 0;
}
</style>
