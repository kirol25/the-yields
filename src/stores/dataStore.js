import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useDataStore = defineStore('data', () => {
  const currentYear = ref(new Date().getFullYear())
  const years = ref([])
  const yearData = ref({ dividends: {}, yields: {} })
  const loading = ref(false)

  async function fetchYears() {
    const { data } = await axios.get('/api/years')
    years.value = data.length ? data : [currentYear.value]
    if (!years.value.includes(currentYear.value)) {
      years.value = [...years.value, currentYear.value].sort((a, b) => a - b)
    }
  }

  async function loadYear(year) {
    loading.value = true
    try {
      const { data } = await axios.get(`/api/data/${year}`)
      yearData.value = data
      currentYear.value = year
    } finally {
      loading.value = false
    }
  }

  async function saveData() {
    await axios.put(`/api/data/${currentYear.value}`, yearData.value)
    await fetchYears()
  }

  return { currentYear, years, yearData, loading, fetchYears, loadYear, saveData }
})
