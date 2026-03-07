<template>
  <div class="min-h-screen bg-gray-950 flex flex-col items-center justify-center px-4">
    <div class="w-full max-w-sm">

      <!-- Logo -->
      <div class="text-center mb-8">
        <span class="text-3xl font-bold text-emerald-400 tracking-tight">the-yields</span>
      </div>

      <!-- Card -->
      <div class="bg-gray-900 border border-gray-800 rounded-2xl p-8">
        <h1 class="text-lg font-semibold text-white mb-1">{{ t('resetPassword.title') }}</h1>
        <p class="text-sm text-gray-500 mb-6">{{ t('resetPassword.subtitle') }}</p>

        <form @submit.prevent="submit" class="space-y-4">
          <div>
            <label for="email" class="block text-xs font-medium text-gray-400 mb-1">{{ t('resetPassword.email') }}</label>
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

          <div>
            <label for="code" class="block text-xs font-medium text-gray-400 mb-1">{{ t('resetPassword.code') }}</label>
            <input
              id="code"
              v-model="code"
              type="text"
              inputmode="numeric"
              autocomplete="one-time-code"
              required
              placeholder="123456"
              class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-sm text-white placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
            />
          </div>

          <div>
            <label for="newPassword" class="block text-xs font-medium text-gray-400 mb-1">{{ t('resetPassword.newPassword') }}</label>
            <input
              id="newPassword"
              v-model="newPassword"
              type="password"
              autocomplete="new-password"
              required
              placeholder="••••••••"
              class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-sm text-white placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
            />
          </div>

          <div>
            <label for="confirmPassword" class="block text-xs font-medium text-gray-400 mb-1">{{ t('resetPassword.confirmPassword') }}</label>
            <input
              id="confirmPassword"
              v-model="confirmPassword"
              type="password"
              autocomplete="new-password"
              required
              placeholder="••••••••"
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
            {{ loading ? t('resetPassword.submitting') : t('resetPassword.submit') }}
          </button>
        </form>

        <p class="mt-5 text-center text-xs text-gray-500">
          <RouterLink to="/login" class="text-emerald-400 hover:text-emerald-300">{{ t('resetPassword.backToSignIn') }}</RouterLink>
        </p>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore.js'
import { useToastStore } from '../stores/toastStore.js'

const { t } = useI18n()
const auth = useAuthStore()
const toast = useToastStore()
const route = useRoute()
const router = useRouter()

const email = ref(route.query.email ?? '')
const code = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')

async function submit() {
  error.value = ''
  if (newPassword.value !== confirmPassword.value) {
    error.value = t('resetPassword.passwordMismatch')
    return
  }
  loading.value = true
  try {
    await auth.resetPassword(email.value, code.value, newPassword.value)
    toast.add(t('resetPassword.successToast'), 'success')
    router.push('/login')
  } catch (err) {
    error.value = err.message ?? 'Failed to reset password. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>
