<template>
  <div class="chatbi">
    <aside class="history">
      <div class="toolbar">
        <strong>会话</strong>
        <el-button size="small" type="primary" @click="newSession">新建</el-button>
      </div>
      <el-menu :default-active="sessionId || undefined" @select="selectSession">
        <el-menu-item v-for="s in sessions" :key="s.id" :index="s.id">
          {{ s.title }}
        </el-menu-item>
      </el-menu>
    </aside>

    <section class="conversation">
      <div class="messages" ref="scroller">
        <div v-for="m in messages" :key="m.id" class="msg" :class="m.role">
          <div class="role">{{ m.role === 'user' ? '你' : 'Semantix' }}</div>
          <MarkdownMessage :content="m.content_markdown" />
        </div>
      </div>
      <div class="composer">
        <el-input
          v-model="question"
          type="textarea"
          :rows="3"
          placeholder="例如：查询各项目最近 7 天的设备在线率。"
          @keydown.ctrl.enter="send"
        />
        <el-button type="primary" :loading="sending" :disabled="!sessionId" @click="send">
          发送
        </el-button>
      </div>
    </section>

    <aside class="side">
      <ExecutionSummary
        :summary="latestSummary"
        :sql="latestSql"
        :rows="latestRows"
      />
    </aside>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '@/api/client'
import { useProjectStore } from '@/stores/project'
import MarkdownMessage from '@/components/chat/MarkdownMessage.vue'
import ExecutionSummary from '@/components/chat/ExecutionSummary.vue'

type Session = { id: string; title: string }
type Message = {
  id: string
  role: string
  content_markdown: string
  sql?: string | null
  columns?: string[]
  rows?: Record<string, unknown>[]
  execution_summary?: Record<string, unknown>
}

const projectStore = useProjectStore()
const sessions = ref<Session[]>([])
const sessionId = ref<string | null>(null)
const messages = ref<Message[]>([])
const question = ref('查询各项目最近 7 天的设备在线率。')
const sending = ref(false)
const scroller = ref<HTMLElement | null>(null)

const latestAssistant = computed(() => [...messages.value].reverse().find((m) => m.role === 'assistant'))
const latestSummary = computed(() => latestAssistant.value?.execution_summary || {})
const latestSql = computed(() => latestAssistant.value?.sql || null)
const latestRows = computed(() => latestAssistant.value?.rows || [])

async function loadSessions() {
  const projectId = projectStore.currentProjectId
  if (!projectId) return
  const { data } = await api.get<Session[]>(`/projects/${projectId}/chatbi/sessions`)
  sessions.value = data
  if (!sessionId.value && data[0]) {
    sessionId.value = data[0].id
  }
}

async function loadMessages() {
  const projectId = projectStore.currentProjectId
  if (!projectId || !sessionId.value) {
    messages.value = []
    return
  }
  const { data } = await api.get<Message[]>(
    `/projects/${projectId}/chatbi/sessions/${sessionId.value}/messages`,
  )
  messages.value = data
  await nextTick()
  if (scroller.value) scroller.value.scrollTop = scroller.value.scrollHeight
}

async function newSession() {
  const projectId = projectStore.currentProjectId
  if (!projectId) {
    ElMessage.warning('请先选择项目')
    return
  }
  const { data } = await api.post<Session>(`/projects/${projectId}/chatbi/sessions`, {
    title: `会话 ${new Date().toLocaleTimeString()}`,
  })
  sessions.value = [data, ...sessions.value]
  sessionId.value = data.id
  messages.value = []
}

function selectSession(id: string) {
  sessionId.value = id
}

async function send() {
  const projectId = projectStore.currentProjectId
  if (!projectId || !sessionId.value || !question.value.trim()) return
  sending.value = true
  try {
    const { data } = await api.post<Message>(
      `/projects/${projectId}/chatbi/sessions/${sessionId.value}/messages`,
      {
        content: question.value.trim(),
        use_demo_rows: true,
      },
    )
    messages.value.push(
      {
        id: `u-${Date.now()}`,
        role: 'user',
        content_markdown: question.value.trim(),
      },
      data,
    )
    question.value = ''
    await nextTick()
    if (scroller.value) scroller.value.scrollTop = scroller.value.scrollHeight
  } catch {
    ElMessage.error('发送失败')
  } finally {
    sending.value = false
  }
}

onMounted(async () => {
  await loadSessions()
  if (!sessions.value.length) await newSession()
  await loadMessages()
})

watch(
  () => projectStore.currentProjectId,
  async () => {
    sessionId.value = null
    await loadSessions()
    if (!sessions.value.length) await newSession()
    await loadMessages()
  },
)

watch(sessionId, loadMessages)
</script>

<style scoped>
.chatbi {
  display: grid;
  grid-template-columns: 220px 1fr 300px;
  gap: 12px;
  min-height: calc(100vh - 140px);
}
.history,
.side {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 8px;
}
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.conversation {
  display: flex;
  flex-direction: column;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  min-height: 0;
}
.messages {
  flex: 1;
  overflow: auto;
  padding: 16px;
}
.msg {
  margin-bottom: 16px;
}
.msg .role {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 4px;
}
.composer {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
  padding: 12px;
  border-top: 1px solid #e5e7eb;
}
@media (max-width: 1100px) {
  .chatbi {
    grid-template-columns: 1fr;
  }
}
</style>
