<template>
  <div class="login-page">
    <el-card class="card">
      <h1>Semantix Studio</h1>
      <p class="sub">登录以管理语义、数据源与 ChatBI</p>
      <el-tabs v-model="mode">
        <el-tab-pane label="登录" name="login" />
        <el-tab-pane label="注册" name="register" />
      </el-tabs>
      <el-form label-position="top" @submit.prevent="onSubmit">
        <el-form-item v-if="mode === 'register'" label="显示名称">
          <el-input v-model="form.display_name" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" type="email" autocomplete="username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input
            v-model="form.password"
            type="password"
            show-password
            autocomplete="current-password"
          />
        </el-form-item>
        <el-button type="primary" native-type="submit" :loading="loading" style="width: 100%">
          {{ mode === 'login' ? '登录' : '注册并登录' }}
        </el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const mode = ref<'login' | 'register'>('login')
const loading = ref(false)
const form = reactive({
  email: '',
  password: '',
  display_name: '',
})

async function onSubmit() {
  loading.value = true
  try {
    if (mode.value === 'register') {
      await auth.register({ ...form })
    } else {
      await auth.login({ email: form.email, password: form.password })
    }
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/dashboard'
    await router.replace(redirect)
  } catch {
    ElMessage.error(mode.value === 'login' ? '登录失败' : '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background:
    radial-gradient(circle at top left, #dbeafe, transparent 40%),
    linear-gradient(160deg, #f8fafc, #e2e8f0);
}
.card {
  width: min(420px, 92vw);
  padding: 8px 8px 16px;
}
h1 {
  margin: 0;
  font-size: 28px;
}
.sub {
  margin: 8px 0 0;
  color: #64748b;
}
</style>
