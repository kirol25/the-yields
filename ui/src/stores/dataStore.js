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
  const freeTierLimit = ref(5) // fallback until /api/me is fetched
  const isPremium = ref(false)  // source of truth — read from DB via /api/me
  const subscriptionPlan = ref(null) // 'monthly' | 'yearly' | null
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
      freeTierLimit.value = data.free_tier_limit
      isPremium.value = data.is_premium
      subscriptionPlan.value = data.subscription_plan ?? null
      _meFetched = true
    } catch (e) {
      toastError('Failed to load user context.', e)
    }
  }

  async function fetchYears() {
    try {
      const { data } = await client.get(`${_apiPrefix()}/years`)
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
      freeTierLimit.value = me.free_tier_limit
      isPremium.value = me.is_premium
      subscriptionPlan.value = me.subscription_plan ?? null
      _meFetched = true
    }
    const base = initYears?.length ? initYears : [currentYear.value]
    const withCurrent = base.includes(current_year) ? base : [...base, current_year]
    years.value = withCurrent.slice().sort((a, b) => b - a)
    currentYear.value = current_year
    yearData.value = year_data ?? { dividends: {}, yields: {} }
    allYearsData.value[current_year] = yearData.value
    if (current_year) localStorage.setItem('last_year', current_year)
    loading.value = false
    initializing.value = false
  }

  return { currentYear, years, yearData, allYearsData, loading, initializing, freeTierLimit, isPremium, subscriptionPlan, fetchMe, fetchYears, loadYear, loadAllYears, clearYearCache, saveData, deleteEntries, initFromData }
})
