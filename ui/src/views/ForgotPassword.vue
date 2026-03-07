<template>
  <div class="min-h-screen bg-gray-950 flex flex-col items-center justify-center px-4">
    <div class="w-full max-w-sm">

      <!-- Logo -->
      <div class="text-center mb-8">
        <span class="text-3xl font-bold text-emerald-400 tracking-tight">the-yields</span>
      </div>

      <!-- Card -->
      <div class="bg-gray-900 border border-gray-800 rounded-2xl p-8">

        <!-- Success state -->
        <template v-if="sent">
          <div class="text-center space-y-3">
            <div class="w-12 h-12 rounded-full bg-emerald-600/20 border border-emerald-500/50 flex items-center justify-center mx-auto">
              <svg class="w-6 h-6 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
              </svg>
            </div>
            <h1 class="text-lg font-semibold text-white">{{ t('forgotPassword.successTitle') }}</h1>
            <p class="text-sm text-gray-400">{{ t('forgotPassword.successSub') }}</p>
          </div>
        </template>

        <!-- Form state -->
        <template v-else>
          <h1 class="text-lg font-semibold text-white mb-1">{{ t('forgotPassword.title') }}</h1>
          <p class="text-sm text-gray-500 mb-6">{{ t('forgotPassword.subtitle') }}</p>

          <form @submit.prevent="submit" class="space-y-4">
            <div>
              <label for="email" class="block text-xs font-medium text-gray-400 mb-1">{{ t('forgotPassword.email') }}</label>
              <input
                id="email"
                v-model="email"
                type="email"
                autocomplete="email"
                required
                placeholder="you@example.com"
                class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-sm text-white placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
              />
            </div>

            <p v-if="error" class="text-xs text-red-400">{{ error }}</p>

            <button
              type="submit"
              :disabled="loading"
              class="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium text-sm transition-colors mt-2"
            >
              <svg v-if="loading" class="w-4 h-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
              </svg>
              {{ loading ? t('forgotPassword.submitting') : t('forgotPassword.submit') }}
            </button>
          </form>
        </template>

        <p class="mt-5 text-center text-xs text-gray-500">
          <RouterLink to="/login" class="text-emerald-400 hover:text-emerald-300">{{ t('forgotPassword.backToSignIn') }}</RouterLink>
        </p>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore.js'

const { t } = useI18n()
const auth = useAuthStore()
const router = useRouter()

const email = ref('')
const loading = ref(false)
const error = ref('')
const sent = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await auth.forgotPassword(email.value)
    sent.value = true
    router.push('/reset-password?email=' + encodeURIComponent(email.value))
  } catch (err) {
    error.value = err.message ?? 'Failed to send reset code. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>
