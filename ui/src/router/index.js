import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/authStore.js'
import { useSettingsStore } from '../stores/settingsStore.js'
import { getLocaleFromPath, localizePath } from './locale.js'
import { REGISTRATION_ENABLED } from '../config.js'

function localizedAliases(paths) {
  const list = Array.isArray(paths) ? paths : [paths]
  return list.flatMap((path) => {
    if (path === '/') return ['/de', '/de/', '/en', '/en/']
    return [`/de${path}`, `/en${path}`]
  })
}

function withLocaleAliases(path, component, meta = {}, aliases = []) {
  return {
    path,
    alias: [...aliases, ...localizedAliases([path, ...aliases])],
    component,
    meta,
  }
}

const routes = [
  // Public landing page
  withLocaleAliases('/', () => import('../views/Landing.vue'), { public: true }),

  // Public-only routes (redirect to /dashboard if already authenticated)
  withLocaleAliases('/login', () => import('../views/Login.vue'), { guestOnly: true }),
  withLocaleAliases('/register', () => import('../views/Register.vue'), { guestOnly: true, registrationOnly: true }),
  withLocaleAliases('/confirm', () => import('../views/Confirm.vue'), { guestOnly: true, registrationOnly: true }),

  // Protected routes
  withLocaleAliases('/dashboard', () => import('../views/Dashboard.vue')),
  withLocaleAliases('/dividends', () => import('../views/Dividends.vue')),
  withLocaleAliases('/yields', () => import('../views/Yields.vue')),
  withLocaleAliases('/profile', () => import('../views/Profile.vue')),
  withLocaleAliases('/settings', () => import('../views/Settings.vue')),
  // Password reset (guest only)
  withLocaleAliases('/forgot-password', () => import('../views/ForgotPassword.vue'), { guestOnly: true }),
  withLocaleAliases('/reset-password', () => import('../views/ResetPassword.vue'), { guestOnly: true }),

  // Locale-prefixed 404
  { path: '/:locale(de|en)/:pathMatch(.*)*', component: () => import('../views/NotFound.vue'), meta: { public: true } },

  // 404 catch-all - must be last
  { path: '/:pathMatch(.*)*', component: () => import('../views/NotFound.vue'), meta: { public: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, _from, savedPosition) {
    if (savedPosition) return savedPosition
    if (to.hash) return { el: to.hash, behavior: 'smooth' }
    return { top: 0 }
  },
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  const settings = useSettingsStore()
  const pathLocale = getLocaleFromPath(to.path)
  const activeLocale = pathLocale ?? settings.locale

  if (!pathLocale) {
    return {
      path: localizePath(to.path, activeLocale),
      query: to.query,
      hash: to.hash,
      replace: true,
    }
  }

  if (settings.locale !== pathLocale) {
    settings.setLocale(pathLocale)
  }

  if (to.meta.registrationOnly && !REGISTRATION_ENABLED) return localizePath('/login', activeLocale)

  if (to.meta.guestOnly) {
    return auth.isAuthenticated ? localizePath('/dashboard', activeLocale) : true
  }

  if (to.meta.public) return true

  if (!auth.isAuthenticated) return { path: localizePath('/login', activeLocale), query: { redirect: to.fullPath } }
})

export default router
