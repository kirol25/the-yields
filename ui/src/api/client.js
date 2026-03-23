import axios from 'axios'
import { useAuthStore } from '../stores/authStore.js'
import { useSettingsStore } from '../stores/settingsStore.js'
import { useToastStore } from '../stores/toastStore.js'
import { API_BASE } from '../config.js'
import router from '../router/index.js'
import { localizePath } from '../router/locale.js'

const client = axios.create({ baseURL: API_BASE, timeout: 15_000 })

// ── Request interceptor - inject auth headers on every call ──────────────────

client.interceptors.request.use((config) => {
  // useAuthStore() is called here (inside the interceptor), not at module load
  // time, so Pinia is guaranteed to be initialised before this runs.
  const headers = useAuthStore().getAuthHeaders()
  Object.assign(config.headers, headers)
  return config
})

// ── Response interceptor - centralised error handling ────────────────────────

client.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status

    if (status === 401) {
      error._handled = true
      useAuthStore().logout()
      router.push(localizePath('/login', useSettingsStore().locale))
    } else if (status === 429) {
      error._handled = true
      useToastStore().add('Too many requests - please slow down.', 'error')
    } else if (status >= 500) {
      error._handled = true
      useToastStore().add('Server error - please try again later.', 'error')
    }

    return Promise.reject(error)
  },
)

export default client
