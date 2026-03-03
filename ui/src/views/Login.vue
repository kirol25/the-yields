<template>
  <div class="min-h-screen bg-gray-950 flex flex-col items-center justify-center px-4">
    <div class="w-full max-w-sm">

      <!-- Logo -->
      <div class="text-center mb-8">
        <span class="text-3xl font-bold text-emerald-400 tracking-tight">the-yield</span>
        <p class="mt-2 text-sm text-gray-500">{{ t('login.tagline') }}</p>
      </div>

      <!-- Card -->
      <div class="bg-gray-900 border border-gray-800 rounded-2xl p-8">
        <h1 class="text-lg font-semibold text-white mb-6">{{ t('login.title') }}</h1>

        <form @submit.prevent="submit" class="space-y-4">
          <div>
            <label for="email" class="block text-xs font-medium text-gray-400 mb-1">{{ t('login.email') }}</label>
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
            <label for="password" class="block text-xs font-medium text-gray-400 mb-1">{{ t('login.password') }}</label>
            <input
              id="password"
              v-model="password"
              type="password"
              autocomplete="current-password"
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
            <Spinner v-if="loading" />
            {{ loading ? t('login.signingIn') : t('login.submit') }}
          </button>
        </form>

        <p v-if="registrationEnabled" class="mt-5 text-center text-xs text-gray-500">
          {{ t('login.noAccount') }}
          <RouterLink to="/register" class="text-emerald-400 hover:text-emerald-300">{{ t('login.createOne') }}</RouterLink>
        </p>
      </div>

      <!-- Footer -->
      <p class="text-center text-xs text-gray-700 mt-6">
        © {{ new Date().getFullYear() }} [Project Maintainer]. {{ t('common.allRightsReserved') }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, defineComponent, h } from 'vue'

const registrationEnabled = import.meta.env.VITE_REGISTRATION_ENABLED === 'true'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore.js'

const { t } = useI18n()
const auth = useAuthStore()
const router = useRouter()

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const Spinner = defineComponent({
  render: () => h('svg', {
    class: 'w-4 h-4 animate-spin',
    xmlns: 'http://www.w3.org/2000/svg',
    fill: 'none',
    viewBox: '0 0 24 24',
  }, [
    h('circle', { class: 'opacity-25', cx: '12', cy: '12', r: '10', stroke: 'currentColor', 'stroke-width': '4' }),
    h('path', { class: 'opacity-75', fill: 'currentColor', d: 'M4 12a8 8 0 018-8v8z' }),
  ]),
})

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await auth.signIn(email.value, password.value)
    router.push('/dashboard')
  } catch (err) {
    if (err.type === 'UserNotConfirmedException') {
      router.push('/confirm')
    } else {
      error.value = err.message ?? 'Sign in failed. Please try again.'
    }
  } finally {
    loading.value = false
  }
}
</script>
