import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import client from '../api/client.js'
import { useToastStore } from './toastStore.js'

export const useDepotStore = defineStore('depot', () => {
  const depots = ref([])
  const currentDepotId = ref(localStorage.getItem('last_depot_id') || null)

  function toastError(message, error) {
    if (error?._handled) return
    useToastStore().add(message, 'error')
  }

  async function fetchDepots() {
    try {
      const { data } = await client.get('/api/depots')
      depots.value = data
      // Auto-select the first depot if stored id is no longer valid
      if (depots.value.length > 0) {
        const ids = depots.value.map((d) => d.id)
        if (!currentDepotId.value || !ids.includes(currentDepotId.value)) {
          currentDepotId.value = depots.value[0].id
          localStorage.setItem('last_depot_id', currentDepotId.value)
        }
      } else {
        // No depots yet — clear any stale id so apiPrefix falls back to /api
        currentDepotId.value = null
        localStorage.removeItem('last_depot_id')
      }
    } catch (e) {
      toastError('Failed to load depots.', e)
    }
  }

  async function createDepot(name) {
    const { data } = await client.post('/api/depots', { name })
    depots.value.push(data)
    return data
  }

  async function renameDepot(id, name) {
    const { data } = await client.patch(`/api/depots/${id}`, { name })
    const idx = depots.value.findIndex((d) => d.id === id)
    if (idx !== -1) depots.value[idx] = data
    return data
  }

  async function deleteDepot(id) {
    await client.delete(`/api/depots/${id}`)
    depots.value = depots.value.filter((d) => d.id !== id)
    if (currentDepotId.value === id) {
      currentDepotId.value = depots.value[0]?.id || null
      if (currentDepotId.value) localStorage.setItem('last_depot_id', currentDepotId.value)
    }
  }

  function selectDepot(id) {
    currentDepotId.value = id
    localStorage.setItem('last_depot_id', id)
  }

  const currentDepot = computed(
    () => depots.value.find((d) => d.id === currentDepotId.value) || null,
  )

  // API prefix to use for finance routes when a depot is selected
  const apiPrefix = computed(() =>
    currentDepotId.value ? `/api/depots/${currentDepotId.value}` : '/api',
  )

  return {
    depots,
    currentDepotId,
    currentDepot,
    apiPrefix,
    fetchDepots,
    createDepot,
    renameDepot,
    deleteDepot,
    selectDepot,
  }
})
