<template>
  <el-container class="shell">
    <el-aside width="220px" class="aside">
      <div class="brand">Semantix</div>
      <el-menu :default-active="active" router>
        <el-menu-item index="/dashboard">工作台</el-menu-item>
        <el-menu-item index="/datasources">数据源</el-menu-item>
        <el-menu-item index="/semantic">语义中心</el-menu-item>
        <el-menu-item index="/capabilities">能力中心</el-menu-item>
        <el-menu-item index="/integrations">系统集成</el-menu-item>
        <el-menu-item index="/chatbi">ChatBI</el-menu-item>
        <el-menu-item index="/coming-soon/settings">系统设置</el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-select
            v-if="projectStore.projects.length"
            :model-value="projectStore.currentProjectId ?? undefined"
            placeholder="选择项目"
            style="width: 220px"
            @change="onProjectChange"
          >
            <el-option
              v-for="p in projectStore.projects"
              :key="p.id"
              :label="p.name"
              :value="p.id"
            />
          </el-select>
          <el-button v-else type="primary" link @click="showCreate = true">创建            创建项目
          </el-button>
        </div>
        <div class="header-right">
          <span class="user">{{ auth.user?.display_name || auth.user?.email }}</span>
          <el-button link type="danger" @click="onLogout">退出</el-button>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>

  <el-dialog v-model="showCreate" title="新建项目" width="420px">
    <el-form label-position="top">
      <el-form-item label="名称">
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item label="Slug">
        <el-input v-model="form.slug" placeholder="demo-project" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showCreate = false">取消</el-button>
      <el-button type="primary" :loading="creating" @click="createProject">创建        创建
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { useProjectStore } from '@/stores/project'

const auth = useAuthStore()
const projectStore = useProjectStore()
const route = useRoute()
const router = useRouter()

const showCreate = ref(false)
const creating = ref(false)
const form = reactive({ name: '', slug: '' })
const active = computed(() => route.path)

onMounted(async () => {
  try {
    await projectStore.loadProjects()
    if (!projectStore.projects.length) {
      showCreate.value = true
    }
  } catch (e) {
    ElMessage.error('加载项目失败')
  }
})

function onProjectChange(id: string) {
  projectStore.setCurrentProject(id)
}

async function createProject() {
  creating.value = true
  try {
    await projectStore.createProject({ ...form })
    showCreate.value = false
    form.name = ''
    form.slug = ''
    ElMessage.success('项目已创建')
  } catch {
    ElMessage.error('创建项目失败')
  } finally {
    creating.value = false
  }
}

function onLogout() {
  auth.logout()
  router.push({ name: 'login' })
}
</script>

<style scoped>
.shell {
  min-height: 100vh;
}
.aside {
  background: #0f172a;
  color: #fff;
}
.brand {
  padding: 20px 16px;
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.04em;
}
.aside :deep(.el-menu) {
  border-right: none;
  background: transparent;
}
.aside :deep(.el-menu-item) {
  color: #cbd5e1;
}
.aside :deep(.el-menu-item.is-active),
.aside :deep(.el-menu-item:hover) {
  background: #1e293b;
  color: #fff;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.user {
  color: #64748b;
}
</style>
