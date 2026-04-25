import { defineStore } from 'pinia'
import { ref } from 'vue'
import client from '../api/client.js'
import { useToastStore } from './toastStore.js'
import { useDepotStore } from './depotStore.js'

export const useDataStore = defineStore('data', () => {
  const storedYear = parseInt(localStorage.getItem('last_year'))
  const currentYear = ref(storedYear || new Date().getFullYear())
  const years = ref([])
  const yearData = ref({ dividends: {}, yields: {} })
  const allYearsData = ref({})
  const loading = ref(false)
  const initializing = ref(true)
  let _meFetched = false

  function toastError(message, error) {
    if (error?._handled) return
    useToastStore().add(message, 'error')
  }

  function _apiPrefix() {
    return useDepotStore().apiPrefix
  }

  async function fetchMe() {
    if (_meFetched) return
    try {
      const { data } = await client.get('/api/me')
      _meFetched = true
    } catch (e) {
      toastError('Failed to load user context.', e)
    }
  }

  async function fetchYears() {
    try {
      const THIS_YEAR = new Date().getFullYear()
      const { data } = await client.get(`${_apiPrefix()}/years`)
      const yearSet = new Set([...data, THIS_YEAR, currentYear.value])
      const sorted = [...yearSet].sort((a, b) => b - a)
      years.value = sorted
      if (!sorted.includes(currentYear.value)) currentYear.value = sorted[0]
    } catch (e) {
      toastError('Failed to load years. Please refresh.', e)
    }
  }

  async function loadYear(year) {
    loading.value = true
    try {
      const { data } = await client.get(`${_apiPrefix()}/data/${year}`)
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

  function clearYearCache() {
    allYearsData.value = {}
    yearData.value = { dividends: {}, yields: {} }
  }

  async function loadAllYears() {
    const missing = years.value.filter((year) => !(year in allYearsData.value))
    if (!missing.length) return
    try {
      const results = await Promise.all(
        missing.map((year) => client.get(`${_apiPrefix()}/data/${year}`).then((r) => [year, r.data])),
      )
      allYearsData.value = { ...allYearsData.value, ...Object.fromEntries(results) }
    } catch (e) {
      toastError('Failed to load historical data.', e)
    }
  }

  async function saveData() {
    try {
      await client.put(`${_apiPrefix()}/data/${currentYear.value}`, yearData.value)
      allYearsData.value[currentYear.value] = yearData.value
      await fetchYears()
    } catch (e) {
      toastError('Failed to save. Please try again.', e)
    }
  }

  async function saveEntryToYear(year, section, key, monthStr, value, name) {
    loading.value = true
    try {
      // Use cached data if available, otherwise fetch from the server
      const base = allYearsData.value[year]
        ?? (await client.get(`${_apiPrefix()}/data/${year}`).then((r) => r.data))

      const existingEntry = base[section]?.[key]
      const merged = {
        ...base,
        [section]: {
          ...base[section],
          [key]: {
            ...(existingEntry ?? (name ? { name, months: {} } : { months: {} })),
            months: { ...(existingEntry?.months ?? {}), [monthStr]: value },
          },
        },
      }

      await client.put(`${_apiPrefix()}/data/${year}`, merged)
      allYearsData.value[year] = merged
      if (year === currentYear.value) yearData.value = merged
      await fetchYears()
    } catch (e) {
      toastError('Failed to save. Please try again.', e)
    } finally {
      loading.value = false
    }
  }

  async function deleteEntries(section, keys) {
    try {
      await Promise.all(
        keys.map((key) =>
          client.delete(
            `${_apiPrefix()}/data/${currentYear.value}/${section}/${encodeURIComponent(key)}`,
          ),
        ),
      )
      for (const key of keys) delete yearData.value[section][key]
      await loadAllYears()
    } catch (e) {
      toastError('Failed to delete entries. Please try again.', e)
      await loadYear(currentYear.value)
    }
  }

  function initFromData({ me, years: initYears, year_data, current_year, depot_id }) {
    if (me) {
      _meFetched = true
    }
    const THIS_YEAR = new Date().getFullYear()
    const base = initYears?.length ? initYears : [THIS_YEAR]
    // Always include THIS_YEAR so users can navigate to the current year even
    // if they have no data for it yet, and include current_year (stored year).
    const yearSet = new Set([...base, THIS_YEAR, current_year])
    years.value = [...yearSet].sort((a, b) => b - a)
    currentYear.value = current_year
    yearData.value = year_data ?? { dividends: {}, yields: {} }
    allYearsData.value[current_year] = yearData.value
    if (current_year) localStorage.setItem('last_year', current_year)
    loading.value = false
    initializing.value = false
  }

  return { currentYear, years, yearData, allYearsData, loading, initializing, fetchMe, fetchYears, loadYear, loadAllYears, clearYearCache, saveData, saveEntryToYear, deleteEntries, initFromData }
})
