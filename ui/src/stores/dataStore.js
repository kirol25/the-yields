import { defineStore } from 'pinia'
import { ref } from 'vue'
import client from '../api/client.js'
import { useToastStore } from './toastStore.js'

export const useDataStore = defineStore('data', () => {
  const storedYear = parseInt(localStorage.getItem('last_year'))
  const currentYear = ref(storedYear || new Date().getFullYear())
  const years = ref([])
  const yearData = ref({ dividends: {}, yields: {} })
  const allYearsData = ref({})
  const loading = ref(false)
  const initializing = ref(true)

  function toastError(message, error) {
    if (error?._handled) return
    useToastStore().add(message, 'error')
  }

  async function fetchYears() {
    try {
      const { data } = await client.get('/api/years')
      const base = data.length ? data : [currentYear.value]
      const withCurrent = base.includes(currentYear.value) ? base : [...base, currentYear.value]
      const sorted = withCurrent.slice().sort((a, b) => b - a)
      years.value = sorted
      if (!sorted.includes(currentYear.value)) currentYear.value = sorted[0]
    } catch (e) {
      toastError('Failed to load years. Please refresh.', e)
    }
  }

  async function loadYear(year) {
    loading.value = true
    try {
      const { data } = await client.get(`/api/data/${year}`)
      yearData.value = data
      currentYear.value = year
      allYearsData.value[year] = data
      localStorage.setItem('last_year', year)
    } catch (e) {
      toastError(`Failed to load data for ${year}.`, e)
    } finally {
      loading.value = false
      initializing.value = false
    }
  }

  async function loadAllYears() {
    try {
      const results = await Promise.all(
        years.value.map((year) =>
          client.get(`/api/data/${year}`).then((r) => [year, r.data]),
        ),
      )
      allYearsData.value = Object.fromEntries(results)
    } catch (e) {
      toastError('Failed to load historical data.', e)
    }
  }

  async function saveData() {
    try {
      await client.put(`/api/data/${currentYear.value}`, yearData.value)
      allYearsData.value[currentYear.value] = yearData.value
      await fetchYears()
    } catch (e) {
      toastError('Failed to save. Please try again.', e)
    }
  }

  async function deleteEntries(section, keys) {
    try {
      await Promise.all(
        keys.map((key) =>
          client.delete(`/api/data/${currentYear.value}/${section}/${encodeURIComponent(key)}`),
        ),
      )
      for (const key of keys) delete yearData.value[section][key]
      await loadAllYears()
    } catch (e) {
      toastError('Failed to delete entries. Please try again.', e)
      await loadYear(currentYear.value)
    }
  }

  return { currentYear, years, yearData, allYearsData, loading, initializing, fetchYears, loadYear, loadAllYears, saveData, deleteEntries }
})
