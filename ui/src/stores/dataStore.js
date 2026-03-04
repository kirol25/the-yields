import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'
import { API_BASE } from '../config.js'
import { useAuthStore } from './authStore.js'
import { useToastStore } from './toastStore.js'

export const useDataStore = defineStore('data', () => {
  const currentYear = ref(new Date().getFullYear())
  const years = ref([])
  const yearData = ref({ dividends: {}, yields: {} })
  const allYearsData = ref({}) // { 2024: { dividends: {}, yields: {} }, ... }
  const loading = ref(false)

  function userHeaders() {
    const auth = useAuthStore()
    return { 'X-User-Email': auth.user?.email ?? '' }
  }

  function toastError(message) {
    useToastStore().add(message, 'error')
  }

  async function fetchYears() {
    try {
      const { data } = await axios.get(`${API_BASE}/api/years`, { headers: userHeaders() })
      const base = data.length ? data : [currentYear.value]
      const withCurrent = base.includes(currentYear.value) ? base : [...base, currentYear.value]
      years.value = withCurrent.slice().sort((a, b) => b - a)
    } catch {
      toastError('Failed to load years. Please refresh.')
    }
  }

  async function loadYear(year) {
    loading.value = true
    try {
      const { data } = await axios.get(`${API_BASE}/api/data/${year}`, { headers: userHeaders() })
      yearData.value = data
      currentYear.value = year
      allYearsData.value[year] = data
    } catch {
      toastError(`Failed to load data for ${year}.`)
    } finally {
      loading.value = false
    }
  }

  async function loadAllYears() {
    try {
      const results = await Promise.all(
        years.value.map((year) =>
          axios.get(`${API_BASE}/api/data/${year}`, { headers: userHeaders() }).then((r) => [year, r.data]),
        ),
      )
      allYearsData.value = Object.fromEntries(results)
    } catch {
      toastError('Failed to load historical data.')
    }
  }

  async function saveData() {
    try {
      await axios.put(`${API_BASE}/api/data/${currentYear.value}`, yearData.value, { headers: userHeaders() })
      await fetchYears()
      await loadAllYears()
    } catch {
      toastError('Failed to save. Please try again.')
    }
  }

  async function deleteEntries(section, keys) {
    try {
      for (const key of keys) {
        await axios.delete(`${API_BASE}/api/data/${currentYear.value}/${section}/${encodeURIComponent(key)}`, {
          headers: userHeaders(),
        })
        delete yearData.value[section][key]
      }
      await loadAllYears()
    } catch {
      toastError('Failed to delete entries. Please try again.')
    }
  }

  return { currentYear, years, yearData, allYearsData, loading, fetchYears, loadYear, loadAllYears, saveData, deleteEntries }
})
