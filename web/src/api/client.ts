import axios from 'axios'

export const api = axios.create({
  baseURL: '/api/v1',
})

api.interceptors.request.use((cfg) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    cfg.headers.Authorization = `Bearer ${token}`
  }
  return cfg
})
