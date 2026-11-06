import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/api/client'

export type Project = {
  id: string
  name: string
  slug: string
}

export const useProjectStore = defineStore('project', () => {
  const projects = ref<Project[]>([])
  const currentProjectId = ref<string | null>(localStorage.getItem('current_project_id'))

  async function loadProjects() {
    const { data } = await api.get<Project[]>('/projects')
    projects.value = data
    if (!currentProjectId.value && data.length > 0) {
      setCurrentProject(data[0].id)
    }
  }

  async function createProject(payload: { name: string; slug: string }) {
    const { data } = await api.post<Project>('/projects', payload)
    projects.value = [data, ...projects.value]
    setCurrentProject(data.id)
    return data
  }

  function setCurrentProject(id: string) {
    currentProjectId.value = id
    localStorage.setItem('current_project_id', id)
  }

  return { projects, currentProjectId, loadProjects, createProject, setCurrentProject }
})
