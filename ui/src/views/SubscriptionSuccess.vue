<template>
  <div class="min-h-[60vh] flex items-center justify-center px-6">
    <div class="text-center max-w-sm">
      <div class="w-16 h-16 rounded-full bg-emerald-500/10 flex items-center justify-center mx-auto mb-6">
        <svg class="w-8 h-8 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"/>
        </svg>
      </div>
      <h1 class="text-2xl font-bold text-gray-100 mb-2">{{ t('subscriptions.successTitle') }}</h1>
      <p class="text-sm text-gray-400 mb-8">{{ t('subscriptions.successSub') }}</p>
      <RouterLink
        to="/dashboard"
        class="inline-block px-6 py-2.5 rounded-lg text-sm font-medium bg-emerald-600 hover:bg-emerald-500 text-white transition-colors"
      >
        {{ t('subscriptions.successCta') }}
      </RouterLink>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../stores/authStore.js'

const { t } = useI18n()
const auth = useAuthStore()

// Refresh the Cognito token so custom:is_premium is reflected immediately
onMounted(async () => {
  try {
    await auth.refreshSession()
  } catch {
    // Best-effort - user can reload later if needed
  }
})
</script>
