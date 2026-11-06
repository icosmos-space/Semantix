import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/login/LoginView.vue'),
      meta: { public: true },
    },
    {
      path: '/',
      component: () => import('@/layouts/MainLayout.vue'),
      children: [
        { path: '', redirect: '/dashboard' },
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('@/views/dashboard/DashboardView.vue'),
        },
        {
          path: 'datasources',
          name: 'datasources',
          component: () => import('@/views/datasources/DataSourceListView.vue'),
        },
        {
          path: 'datasources/:id/schema',
          name: 'datasource-schema',
          component: () => import('@/views/datasources/SchemaExplorerView.vue'),
        },
        {
          path: 'semantic',
          name: 'semantic',
          component: () => import('@/views/semantic/SemanticStudioView.vue'),
        },
        {
          path: 'coming-soon/:module',
          name: 'coming-soon',
          component: () => import('@/views/ComingSoonView.vue'),
        },


      ],
    },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.name === 'login' && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }
  if (auth.isAuthenticated && !auth.user) {
    try {
      await auth.fetchMe()
    } catch {
      auth.logout()
      return { name: 'login' }
    }
  }
  return true
})

export default router
