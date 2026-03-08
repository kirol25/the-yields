import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/authStore.js'
import { useSettingsStore } from '../stores/settingsStore.js'

const REGISTRATION_ENABLED = import.meta.env.VITE_REGISTRATION_ENABLED === 'true'

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
  withLocaleAliases('/subscriptions', () => import('../views/Subscriptions.vue'), { public: true }),
  withLocaleAliases('/subscription/success', () => import('../views/SubscriptionSuccess.vue'), { public: true }),
  withLocaleAliases('/impressum', () => import('../views/Impressum.vue'), { public: true }, ['/legal-notice']),
  withLocaleAliases('/datenschutz', () => import('../views/Datenschutz.vue'), { public: true }, ['/privacy-policy']),

  // Password reset (guest only)
  withLocaleAliases('/forgot-password', () => import('../views/ForgotPassword.vue'), { guestOnly: true }),
  withLocaleAliases('/reset-password', () => import('../views/ResetPassword.vue'), { guestOnly: true }),

  // Public pages
  withLocaleAliases('/terms', () => import('../views/Terms.vue'), { public: true }, ['/nutzungsbedingungen']),
  withLocaleAliases('/feedback', () => import('../views/Feedback.vue'), { public: true }),

  // Locale-prefixed 404
  { path: '/:locale(de|en)/:pathMatch(.*)*', component: () => import('../views/NotFound.vue'), meta: { public: true } },

  // 404 catch-all — must be last
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
  const localeMatch = to.path.match(/^\/(de|en)(?:\/|$)/)

  if (localeMatch && settings.locale !== localeMatch[1]) {
    settings.setLocale(localeMatch[1])
  }

  if (to.meta.registrationOnly && !REGISTRATION_ENABLED) return '/login'

  if (to.meta.guestOnly) {
    return auth.isAuthenticated ? '/dashboard' : true
  }

  if (to.meta.public) return true

  if (!auth.isAuthenticated) return '/login'
})

export default router
