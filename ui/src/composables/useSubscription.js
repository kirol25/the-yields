import { computed } from 'vue'

// TODO: wire to real billing state when payments are implemented
export function useSubscription() {
  const isPremium = computed(() => false)
  return { isPremium }
}
