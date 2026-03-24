import { ref } from 'vue'
import client from '../api/client.js'

// Module-level — shared across all component instances
const subStatus = ref({
  active: false,
  cancel_at_period_end: false,
  ends_at: null,
  started_at: null,
  current_period_start: null,
  current_period_end: null,
  interval: null,
})
let _fetched = false

export function useSubscriptionStatus() {
  async function fetchStatus(force = false) {
    if (_fetched && !force) return
    try {
      const { data } = await client.get('/api/subscription/status')
      subStatus.value = data
      _fetched = true
    } catch { /* non-critical */ }
  }

  function markCancelled(endsAt) {
    subStatus.value = { ...subStatus.value, cancel_at_period_end: true, ends_at: endsAt }
  }

  function markReactivated() {
    subStatus.value = { ...subStatus.value, cancel_at_period_end: false, ends_at: null }
  }

  return { subStatus, fetchStatus, markCancelled, markReactivated }
}
