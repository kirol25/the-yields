import axios from 'axios'
import { useAuthStore } from '../stores/authStore.js'
import { useToastStore } from '../stores/toastStore.js'
import { API_BASE } from '../config.js'
import router from '../router/index.js'

const client = axios.create({ baseURL: API_BASE })

// ── Request interceptor — inject auth headers on every call ──────────────────

client.interceptors.request.use((config) => {
  // useAuthStore() is called here (inside the interceptor), not at module load
  // time, so Pinia is guaranteed to be initialised before this runs.
  const headers = useAuthStore().getAuthHeaders()
  Object.assign(config.headers, headers)
  return config
})

// ── Response interceptor — centralised error handling ────────────────────────

client.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status

    if (status === 401) {
      useAuthStore().logout()
      router.push('/login')
    } else if (status === 429) {
      useToastStore().add('Too many requests — please slow down.', 'error')
    } else if (status >= 500) {
      useToastStore().add('Server error — please try again later.', 'error')
    }

    return Promise.reject(error)
  },
)

export default client
