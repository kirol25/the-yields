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
        <h1 class="text-lg font-semibold text-white mb-2">{{ t('confirm.title') }}</h1>
        <p class="text-xs text-gray-500 mb-6">{{ t('confirm.subtitle') }}</p>

        <form @submit.prevent="submit" class="space-y-4">
          <div>
            <label for="email" class="block text-xs font-medium text-gray-400 mb-1">{{ t('confirm.email') }}</label>
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
            <label for="code" class="block text-xs font-medium text-gray-400 mb-1">{{ t('confirm.code') }}</label>
            <input
              id="code"
              v-model="code"
              type="text"
              inputmode="numeric"
              autocomplete="one-time-code"
              required
              maxlength="6"
              placeholder="123456"
              class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-sm text-white placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent tracking-widest"
            />
          </div>

          <p v-if="error" class="text-xs text-red-400">{{ error }}</p>
          <p v-if="resendMsg" class="text-xs text-emerald-400">{{ resendMsg }}</p>

          <button
            type="submit"
            :disabled="loading"
            class="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium text-sm transition-colors mt-2"
          >
            <Spinner v-if="loading" />
            {{ loading ? t('confirm.confirming') : t('confirm.submit') }}
          </button>
        </form>

        <p class="mt-5 text-center text-xs text-gray-500">
          {{ t('confirm.noCode') }}
          <button
            type="button"
            :disabled="resending"
            @click="resend"
            class="text-emerald-400 hover:text-emerald-300 disabled:opacity-50"
          >
            {{ t('confirm.resend') }}
          </button>
        </p>
      </div>

      <!-- Footer -->
      <p class="text-center text-xs text-gray-700 mt-6">
        © {{ new Date().getFullYear() }} Lorik Bajrami. {{ t('common.allRightsReserved') }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, defineComponent, h } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore.js'
import { useToastStore } from '../stores/toastStore.js'

const { t } = useI18n()
const auth = useAuthStore()
const toast = useToastStore()
const router = useRouter()

const email = ref(auth.pendingEmail)
const code = ref('')
const loading = ref(false)
const resending = ref(false)
const error = ref('')
const resendMsg = ref('')

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
  resendMsg.value = ''
  loading.value = true
  try {
    await auth.confirmSignUp(email.value, code.value)
    toast.add(t('confirm.confirmed'), 'success')
    router.push('/login')
  } catch (err) {
    error.value = err.message ?? 'Confirmation failed. Please try again.'
  } finally {
    loading.value = false
  }
}

async function resend() {
  error.value = ''
  resendMsg.value = ''
  resending.value = true
  try {
    await auth.resendCode(email.value)
    resendMsg.value = t('confirm.codeSent')
  } catch (err) {
    error.value = err.message ?? 'Could not resend code.'
  } finally {
    resending.value = false
  }
}
</script>
