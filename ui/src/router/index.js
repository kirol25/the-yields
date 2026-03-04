import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/authStore.js'

const REGISTRATION_ENABLED = import.meta.env.VITE_REGISTRATION_ENABLED === 'true'

const routes = [
  // Public landing page
  { path: '/', component: () => import('../views/Landing.vue'), meta: { public: true } },

  // Public-only routes (redirect to /dashboard if already authenticated)
  { path: '/login',    component: () => import('../views/Login.vue'),    meta: { guestOnly: true } },
  { path: '/register', component: () => import('../views/Register.vue'), meta: { guestOnly: true, registrationOnly: true } },
  { path: '/confirm',  component: () => import('../views/Confirm.vue'),  meta: { guestOnly: true, registrationOnly: true } },

  // Protected routes
  { path: '/dashboard',  component: () => import('../views/Dashboard.vue') },
  { path: '/dividends',  component: () => import('../views/Dividends.vue') },
  { path: '/yields',     component: () => import('../views/Yields.vue') },
  { path: '/profile',    component: () => import('../views/Profile.vue') },
  { path: '/settings',   component: () => import('../views/Settings.vue') },
  { path: '/subscriptions', component: () => import('../views/Subscriptions.vue'), meta: { public: true } },
  { path: '/impressum',  component: () => import('../views/Impressum.vue'), meta: { public: true } },
  { path: '/datenschutz', component: () => import('../views/Datenschutz.vue'), meta: { public: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.meta.registrationOnly && !REGISTRATION_ENABLED) return '/login'

  if (to.meta.guestOnly) {
    return auth.isAuthenticated ? '/dashboard' : true
  }

  if (to.meta.public) return true

  if (!auth.isAuthenticated) return '/login'
})

export default router
