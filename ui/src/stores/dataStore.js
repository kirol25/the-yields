import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import { API_BASE } from '../config.js'

export const useDataStore = defineStore('data', () => {
  const currentYear = ref(new Date().getFullYear())
  const years = ref([])
  const yearData = ref({ dividends: {}, yields: {} })
  const allYearsData = ref({}) // { 2024: { dividends: {}, yields: {} }, ... }
  const loading = ref(false)

  async function fetchYears() {
    const { data } = await axios.get(`${API_BASE}/api/years`)
    const base = data.length ? data : [currentYear.value]
    const withCurrent = base.includes(currentYear.value) ? base : [...base, currentYear.value]
    years.value = withCurrent.slice().sort((a, b) => b - a)
  }

  async function loadYear(year) {
    loading.value = true
    try {
      const { data } = await axios.get(`${API_BASE}/api/data/${year}`)
      yearData.value = data
      currentYear.value = year
      allYearsData.value[year] = data
    } finally {
      loading.value = false
    }
  }

  async function loadAllYears() {
    const results = await Promise.all(
      years.value.map((year) => axios.get(`${API_BASE}/api/data/${year}`).then((r) => [year, r.data])),
    )
    allYearsData.value = Object.fromEntries(results)
  }

  async function saveData() {
    await axios.put(`${API_BASE}/api/data/${currentYear.value}`, yearData.value)
    await fetchYears()
    await loadAllYears()
  }

  async function deleteEntries(section, keys) {
    for (const key of keys) {
      await axios.delete(`${API_BASE}/api/data/${currentYear.value}/${section}/${encodeURIComponent(key)}`)
      delete yearData.value[section][key]
    }
    await loadAllYears()
  }

  return { currentYear, years, yearData, allYearsData, loading, fetchYears, loadYear, loadAllYears, saveData, deleteEntries }
})
