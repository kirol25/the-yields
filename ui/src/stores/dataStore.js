import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'
import { API_BASE } from '../config.js'
import { useAuthStore } from './authStore.js'
import { useToastStore } from './toastStore.js'

export const useDataStore = defineStore('data', () => {
  const storedYear = parseInt(localStorage.getItem('last_year'))
  const currentYear = ref(storedYear || new Date().getFullYear())
  const years = ref([])
  const yearData = ref({ dividends: {}, yields: {} })
  const allYearsData = ref({}) // { 2024: { dividends: {}, yields: {} }, ... }
  const loading = ref(false)
  const initializing = ref(true) // true until the first loadYear completes

  function userHeaders() {
    return useAuthStore().getAuthHeaders()
  }

  function toastError(message) {
    useToastStore().add(message, 'error')
  }

  async function fetchYears() {
    try {
      const { data } = await axios.get(`${API_BASE}/api/years`, { headers: userHeaders() })
      const base = data.length ? data : [currentYear.value]
      const withCurrent = base.includes(currentYear.value) ? base : [...base, currentYear.value]
      const sorted = withCurrent.slice().sort((a, b) => b - a)
      years.value = sorted
      // Validate stored year; fall back to most recent if it no longer exists
      if (!sorted.includes(currentYear.value)) {
        currentYear.value = sorted[0]
      }
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
      localStorage.setItem('last_year', year)
    } catch {
      toastError(`Failed to load data for ${year}.`)
    } finally {
      loading.value = false
      initializing.value = false
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
      await Promise.all(
        keys.map((key) =>
          axios.delete(`${API_BASE}/api/data/${currentYear.value}/${section}/${encodeURIComponent(key)}`, {
            headers: userHeaders(),
          }),
        ),
      )
      for (const key of keys) {
        delete yearData.value[section][key]
      }
      await loadAllYears()
    } catch {
      toastError('Failed to delete entries. Please try again.')
      await loadYear(currentYear.value)
    }
  }

  return { currentYear, years, yearData, allYearsData, loading, initializing, fetchYears, loadYear, loadAllYears, saveData, deleteEntries }
})
