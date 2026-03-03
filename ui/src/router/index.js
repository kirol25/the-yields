import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/authStore.js'

const REGISTRATION_ENABLED = "false"

const routes = [
  // Public-only routes (redirect to dashboard if already authenticated)
  { path: '/login',    component: () => import('../views/Login.vue'),    meta: { guestOnly: true } },
  { path: '/register', component: () => import('../views/Register.vue'), meta: { guestOnly: true, registrationOnly: true } },
  { path: '/confirm',  component: () => import('../views/Confirm.vue'),  meta: { guestOnly: true, registrationOnly: true } },

  // Protected routes
  { path: '/',           component: () => import('../views/Dashboard.vue') },
  { path: '/dividends',  component: () => import('../views/Dividends.vue') },
  { path: '/yields',     component: () => import('../views/Yields.vue') },
  { path: '/profile',    component: () => import('../views/Profile.vue') },
  { path: '/settings',   component: () => import('../views/Settings.vue') },
  { path: '/impressum',  component: () => import('../views/Impressum.vue') },
  { path: '/datenschutz', component: () => import('../views/Datenschutz.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.meta.registrationOnly && !REGISTRATION_ENABLED) return '/login'

  if (to.meta.guestOnly) {
    return auth.isAuthenticated ? '/' : true
  }

  if (!auth.isAuthenticated) return '/login'
})

export default router
