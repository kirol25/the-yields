import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/authStore.js'
import Dashboard from '../views/Dashboard.vue'
import Dividends from '../views/Dividends.vue'
import Yields from '../views/Yields.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Confirm from '../views/Confirm.vue'
import Profile from '../views/Profile.vue'
import Settings from '../views/Settings.vue'
import Impressum from '../views/Impressum.vue'
import Datenschutz from '../views/Datenschutz.vue'

const routes = [
  { path: '/login', component: Login, meta: { public: true } },
  { path: '/register', component: Register, meta: { public: true } },
  { path: '/confirm', component: Confirm, meta: { public: true } },
  { path: '/', component: Dashboard },
  { path: '/impressum', component: Impressum, meta: { public: true } },
  { path: '/datenschutz', component: Datenschutz, meta: { public: true } },
  { path: '/dividends', component: Dividends },
  { path: '/yields', component: Yields },
  { path: '/profile', component: Profile },
  { path: '/settings', component: Settings },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  if (to.meta.public) return true
  const auth = useAuthStore()
  if (!auth.isAuthenticated) return '/login'
})

export default router
