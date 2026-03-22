import { computed } from 'vue'
import { useDataStore } from '../stores/dataStore.js'

export function useSubscription() {
  const store = useDataStore()
  const isPremium = computed(() => store.isPremium)
  const subscriptionPlan = computed(() => store.subscriptionPlan)
  return { isPremium, subscriptionPlan }
}
