<template>
  <div class="max-w-5xl mx-auto px-6 py-16">
    <div class="text-center mb-12">
      <span class="inline-block px-3 py-1 text-xs font-semibold uppercase tracking-wider text-emerald-400 bg-emerald-400/10 rounded-full mb-4">
        {{ t('subscriptions.badge') }}
      </span>
      <h1 class="text-3xl font-bold text-gray-100">{{ t('subscriptions.title') }}</h1>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- Free -->
      <div class="bg-gray-900 border border-gray-800 rounded-xl p-6 flex flex-col transition-all duration-300 hover:border-gray-600 hover:shadow-[0_0_24px_rgba(156,163,175,0.12)]">
        <div class="mb-6">
          <h2 class="text-lg font-semibold text-gray-100 mb-1">{{ t('subscriptions.free.name') }}</h2>
          <div class="flex items-baseline gap-1">
            <span class="text-3xl font-bold text-gray-100">{{ t('subscriptions.free.price') }}</span>
            <span class="text-sm text-gray-500">/ {{ t('subscriptions.free.period') }}</span>
          </div>
        </div>
        <ul class="space-y-3 flex-1 mb-8">
          <li v-for="feature in tm('subscriptions.free.features')" :key="feature" class="flex items-start gap-2 text-sm text-gray-400">
            <span class="text-emerald-500 mt-0.5 shrink-0">✓</span>
            {{ feature }}
          </li>
        </ul>
        <RouterLink
          to="/register"
          class="w-full py-2.5 rounded-lg text-sm font-medium bg-emerald-600 hover:bg-emerald-500 text-white transition-colors text-center block"
        >
          {{ t('subscriptions.ctaFree') }}
        </RouterLink>
      </div>

      <!-- Monthly -->
      <div class="bg-gray-900 border border-gray-800 rounded-xl p-6 flex flex-col transition-all duration-300 hover:border-emerald-500/40 hover:shadow-[0_0_28px_rgba(52,211,153,0.12)]">
        <div class="mb-6">
          <h2 class="text-lg font-semibold text-gray-100 mb-1">{{ t('subscriptions.monthly.name') }}</h2>
          <div class="flex items-baseline gap-1">
            <span class="text-3xl font-bold text-gray-100">{{ t('subscriptions.monthly.price') }}</span>
            <span class="text-sm text-gray-500">/ {{ t('subscriptions.monthly.period') }}</span>
          </div>
        </div>
        <ul class="space-y-3 flex-1 mb-8">
          <li v-for="feature in tm('subscriptions.monthly.features')" :key="feature" class="flex items-start gap-2 text-sm text-gray-400">
            <span class="text-emerald-500 mt-0.5 shrink-0">✓</span>
            {{ feature }}
          </li>
        </ul>
        <button
          type="button"
          :disabled="!stripeEnabled || loading === 'monthly' || subscriptionPlan === 'monthly' || subscriptionPlan === 'yearly'"
          @click="checkout('monthly')"
          class="w-full py-2.5 rounded-lg text-sm font-medium transition-colors"
          :class="stripeEnabled && subscriptionPlan !== 'monthly' && subscriptionPlan !== 'yearly'
            ? 'bg-emerald-600 hover:bg-emerald-500 text-white disabled:opacity-50 disabled:cursor-not-allowed'
            : 'bg-gray-800 text-gray-500 cursor-not-allowed'"
        >
          {{ subscriptionPlan === 'monthly' ? t('subscriptions.currentPlan') : loading === 'monthly' ? t('subscriptions.redirecting') : t('subscriptions.ctaPaid') }}
        </button>
      </div>

      <!-- Yearly (highlighted) -->
      <div class="bg-gray-900 border-2 border-emerald-500/50 rounded-xl p-6 flex flex-col transition-all duration-300 hover:border-emerald-400/80 hover:shadow-[0_0_36px_rgba(52,211,153,0.22)]">
        <div class="mb-6">
          <div class="flex items-center justify-between mb-1">
            <h2 class="text-lg font-semibold text-gray-100">{{ t('subscriptions.yearly.name') }}</h2>
            <span class="px-2 py-0.5 text-xs font-semibold text-emerald-400 bg-emerald-400/10 rounded-full">
              {{ t('subscriptions.yearly.badge') }}
            </span>
          </div>
          <div class="flex items-baseline gap-1">
            <span class="text-3xl font-bold text-gray-100">{{ t('subscriptions.yearly.price') }}</span>
            <span class="text-sm text-gray-500">/ {{ t('subscriptions.yearly.period') }}</span>
          </div>
        </div>
        <ul class="space-y-3 flex-1 mb-8">
          <li v-for="feature in tm('subscriptions.yearly.features')" :key="feature" class="flex items-start gap-2 text-sm text-gray-400">
            <span class="text-emerald-500 mt-0.5 shrink-0">✓</span>
            {{ feature }}
          </li>
        </ul>
        <button
          type="button"
          :disabled="!stripeEnabled || loading === 'yearly' || subscriptionPlan === 'yearly'"
          @click="checkout('yearly')"
          class="w-full py-2.5 rounded-lg text-sm font-medium transition-colors border"
          :class="stripeEnabled && subscriptionPlan !== 'yearly'
            ? 'bg-emerald-600 hover:bg-emerald-500 text-white border-transparent disabled:opacity-50 disabled:cursor-not-allowed'
            : 'bg-emerald-600/30 text-emerald-400 cursor-not-allowed border-emerald-500/30'"
        >
          {{ subscriptionPlan === 'yearly' ? t('subscriptions.currentPlan') : loading === 'yearly' ? t('subscriptions.redirecting') : t('subscriptions.ctaPaid') }}
        </button>
      </div>
    </div>

    <!-- Disclaimer -->
    <p v-if="!isPremium" class="mt-4 text-center text-xs text-gray-500">
      {{ t('subscriptions.disclaimer') }}
      <RouterLink to="/terms" class="underline underline-offset-2 hover:text-gray-300 transition-colors">{{ t('subscriptions.disclaimerAgb') }}</RouterLink>.
    </p>

    <!-- Manage subscription (premium users) -->
    <div v-if="isPremium" class="mt-10 text-center">
      <button
        @click="openPortal"
        :disabled="portalLoading"
        class="text-sm text-gray-400 hover:text-gray-200 underline underline-offset-2 transition-colors disabled:opacity-50"
      >
        {{ portalLoading ? t('subscriptions.redirecting') : t('subscriptions.manageSubscription') }}
      </button>
    </div>

    <!-- Error -->
    <p v-if="error" class="mt-6 text-center text-sm text-red-400">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/authStore.js'
import client from '../api/client.js'
import { useSubscription } from '../composables/useSubscription.js'

const { t, tm } = useI18n()
const { isPremium, subscriptionPlan } = useSubscription()
const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const stripeEnabled = import.meta.env.VITE_STRIPE_ENABLED === 'true'
const loading = ref(null)   // 'monthly' | 'yearly' | null
const portalLoading = ref(false)
const error = ref('')

async function checkout(plan) {
  if (!auth.isAuthenticated) {
    router.push({ path: '/login', query: { redirect: route.fullPath } })
    return
  }
  loading.value = plan
  error.value = ''
  try {
    const { data } = await client.post('/api/subscription/checkout', { plan })
    window.location.href = data.url
  } catch {
    error.value = t('subscriptions.checkoutError')
    loading.value = null
  }
}

async function openPortal() {
  portalLoading.value = true
  error.value = ''
  try {
    const { data } = await client.post('/api/subscription/portal', {})
    window.location.href = data.url
  } catch {
    error.value = t('subscriptions.checkoutError')
    portalLoading.value = false
  }
}
</script>
