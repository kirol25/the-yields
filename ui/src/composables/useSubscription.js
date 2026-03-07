import { computed } from 'vue'
import { useAuthStore } from '../stores/authStore.js'

export function useSubscription() {
  const auth = useAuthStore()
  const isPremium = computed(() => auth.user?.isPremium === true)
  return { isPremium }
}
