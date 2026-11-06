import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { api } from '@/api/client'

export type User = {
  id: string
  email: string
  display_name: string
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const user = ref<User | null>(null)

  const isAuthenticated = computed(() => Boolean(token.value))

  async function register(payload: {
    email: string
    password: string
    display_name: string
  }) {
    await api.post('/auth/register', payload)
    return login({ email: payload.email, password: payload.password })
  }

  async function login(payload: { email: string; password: string }) {
    const { data } = await api.post<{ access_token: string }>('/auth/login', payload)
    token.value = data.access_token
    localStorage.setItem('access_token', data.access_token)
    await fetchMe()
  }

  async function fetchMe() {
    if (!token.value) {
      user.value = null
      return
    }
    const { data } = await api.get<User>('/auth/me')
    user.value = data
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('access_token')
  }

  return { token, user, isAuthenticated, register, login, fetchMe, logout }
})
