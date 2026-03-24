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
          v-if="!auth.isAuthenticated"
          to="/register"
          class="w-full py-2.5 rounded-lg text-sm font-medium bg-emerald-600 hover:bg-emerald-500 text-white transition-colors text-center block"
        >
          {{ t('subscriptions.ctaFree') }}
        </RouterLink>
        <button
          v-else
          disabled
          class="w-full py-2.5 rounded-lg text-sm font-medium bg-gray-800 text-gray-500 cursor-not-allowed"
        >
          {{ t('subscriptions.ctaFree') }}
        </button>
      </div>

      <!-- Monthly -->
      <div class="bg-gray-900 border rounded-xl p-6 flex flex-col transition-all duration-300"
        :class="isMonthly || isUnknownPlan
          ? 'border-emerald-500/50'
          : 'border-gray-800 hover:border-emerald-500/40 hover:shadow-[0_0_28px_rgba(52,211,153,0.12)]'"
      >
        <div class="mb-6">
          <div class="flex items-center justify-between mb-1">
            <h2 class="text-lg font-semibold text-gray-100">{{ t('subscriptions.monthly.name') }}</h2>
            <span v-if="isMonthly || isUnknownPlan" class="px-2 py-0.5 text-xs font-semibold text-emerald-400 bg-emerald-400/10 rounded-full">
              {{ t('subscriptions.currentPlan') }}
            </span>
          </div>
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
          :disabled="!stripeEnabled || loading === 'monthly' || isMonthly || isYearly || isUnknownPlan"
          @click="checkout('monthly')"
          class="w-full py-2.5 rounded-lg text-sm font-medium transition-colors"
          :class="isMonthly || isUnknownPlan
            ? 'bg-emerald-600/20 text-emerald-400 border border-emerald-500/30 cursor-not-allowed'
            : stripeEnabled && !isYearly
              ? 'bg-emerald-600 hover:bg-emerald-500 text-white disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer'
              : 'bg-gray-800 text-gray-500 cursor-not-allowed'"
        >
          {{ isMonthly || isUnknownPlan ? t('subscriptions.currentPlan') : loading === 'monthly' ? t('subscriptions.redirecting') : t('subscriptions.ctaPaid') }}
        </button>
      </div>

      <!-- Yearly (highlighted) -->
      <div class="bg-gray-900 border-2 border-emerald-500/50 rounded-xl p-6 flex flex-col transition-all duration-300"
        :class="!isYearly ? 'hover:border-emerald-400/80 hover:shadow-[0_0_36px_rgba(52,211,153,0.22)]' : ''"
      >
        <div class="mb-6">
          <div class="flex items-center justify-between mb-1">
            <h2 class="text-lg font-semibold text-gray-100">{{ t('subscriptions.yearly.name') }}</h2>
            <span class="px-2 py-0.5 text-xs font-semibold text-emerald-400 bg-emerald-400/10 rounded-full">
              {{ isYearly ? t('subscriptions.currentPlan') : t('subscriptions.yearly.badge') }}
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
          :disabled="!stripeEnabled || loading === 'yearly' || isYearly || isUnknownPlan"
          @click="checkout('yearly')"
          class="w-full py-2.5 rounded-lg text-sm font-medium transition-colors border"
          :class="isYearly
            ? 'bg-emerald-600/20 text-emerald-400 border-emerald-500/30 cursor-not-allowed'
            : stripeEnabled && !isUnknownPlan
              ? 'bg-emerald-600 hover:bg-emerald-500 text-white border-transparent disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer'
              : 'bg-emerald-600/30 text-emerald-400 cursor-not-allowed border-emerald-500/30'"
        >
          {{ isYearly ? t('subscriptions.currentPlan') : loading === 'yearly' ? t('subscriptions.redirecting') : t('subscriptions.ctaPaid') }}
        </button>
      </div>
    </div>

    <!-- Disclaimer -->
    <p v-if="!isPremium" class="mt-4 text-center text-xs text-gray-500">
      {{ t('subscriptions.disclaimer') }}
      <RouterLink to="/terms" class="underline underline-offset-2 hover:text-gray-300 transition-colors">{{ t('subscriptions.disclaimerAgb') }}</RouterLink>.
    </p>

    <!-- Manage subscription (premium users) -->
    <div v-if="isPremium" class="mt-10 text-center space-y-3">
      <!-- Cancellation confirm step -->
      <template v-if="cancelConfirm">
        <p class="text-sm text-gray-300">{{ t('subscriptions.cancelConfirm') }}</p>
        <div class="flex justify-center gap-3">
          <button
            @click="cancelConfirm = false"
            class="px-4 py-1.5 text-sm rounded-lg border border-gray-700 text-gray-400 hover:text-gray-200 hover:border-gray-500 transition-colors"
          >
            {{ t('subscriptions.cancelAbort') }}
          </button>
          <button
            @click="confirmCancel"
            :disabled="cancelLoading"
            class="px-4 py-1.5 text-sm rounded-lg bg-red-600 hover:bg-red-500 text-white transition-colors disabled:opacity-50"
          >
            {{ cancelLoading ? t('subscriptions.cancelling') : t('subscriptions.cancelConfirmBtn') }}
          </button>
        </div>
      </template>

      <!-- Cancelled state -->
      <p v-else-if="cancelledUntil !== undefined" class="text-sm text-gray-400">
        {{ cancelledUntil ? t('subscriptions.cancelledUntil', { date: cancelledUntil }) : t('subscriptions.cancelledGeneric') }}
      </p>

      <!-- Default actions -->
      <template v-else>
        <button
          @click="cancelConfirm = true"
          class="text-sm text-red-400 hover:text-red-300 underline underline-offset-2 transition-colors"
        >
          {{ t('subscriptions.cancelSubscription') }}
        </button>
      </template>
    </div>

    <!-- Subscription details (premium only) -->
    <div v-if="isPremium" class="mt-10 bg-gray-900 border border-gray-800 rounded-xl p-6">
      <h3 class="text-xs uppercase tracking-wider text-gray-500 font-medium mb-4">{{ t('subscriptions.details.title') }}</h3>
      <!-- Stripe data loaded -->
      <dl v-if="subStatus.active" class="grid grid-cols-2 gap-x-6 gap-y-4">
        <div>
          <dt class="text-xs text-gray-500 mb-0.5">{{ t('subscriptions.details.startedOn') }}</dt>
          <dd class="text-sm text-gray-200">{{ fmtDate(subStatus.started_at) }}</dd>
        </div>
        <div>
          <dt class="text-xs text-gray-500 mb-0.5">{{ t('subscriptions.details.billingInterval') }}</dt>
          <dd class="text-sm text-gray-200">{{ subStatus.interval ? t('subscriptions.details.interval_' + subStatus.interval) : '—' }}</dd>
        </div>
        <div>
          <dt class="text-xs text-gray-500 mb-0.5">{{ t('subscriptions.details.periodStart') }}</dt>
          <dd class="text-sm text-gray-200">{{ fmtDate(subStatus.current_period_start) }}</dd>
        </div>
        <div>
          <dt class="text-xs text-gray-500 mb-0.5">{{ subStatus.cancel_at_period_end ? t('subscriptions.details.accessUntil') : t('subscriptions.details.nextRenewal') }}</dt>
          <dd class="text-sm" :class="subStatus.cancel_at_period_end ? 'text-amber-400' : 'text-gray-200'">{{ fmtDate(subStatus.current_period_end) }}</dd>
        </div>
      </dl>
      <!-- Stripe not reachable (e.g. dev environment) -->
      <p v-else class="text-sm text-gray-500">{{ t('subscriptions.details.unavailable') }}</p>
      <p v-if="subStatus.cancel_at_period_end" class="mt-4 text-xs text-amber-400/80">
        {{ t('subscriptions.details.cancelNotice') }}
      </p>
    </div>

    <!-- Error -->
    <p v-if="error" class="mt-6 text-center text-sm text-red-400">{{ error }}</p>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/authStore.js'
import client from '../api/client.js'
import { useSubscription } from '../composables/useSubscription.js'
import { useSubscriptionStatus } from '../composables/useSubscriptionStatus.js'

const { t, tm } = useI18n()
const { isPremium, subscriptionPlan } = useSubscription()

// True when the user is on this specific plan
const isMonthly = computed(() => subscriptionPlan.value === 'monthly')
const isYearly  = computed(() => subscriptionPlan.value === 'yearly')
// True when premium but we don't know the exact plan (e.g. legacy row without plan set)
const isUnknownPlan = computed(() => isPremium.value && !subscriptionPlan.value)
const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const stripeEnabled = import.meta.env.VITE_STRIPE_ENABLED === 'true'
const loading = ref(null)   // 'monthly' | 'yearly' | null
const error = ref('')

const cancelConfirm  = ref(false)
const cancelLoading  = ref(false)
const cancelledUntil = ref(undefined) // undefined = not cancelled; null = cancelled, no date; string = date

const { subStatus, fetchStatus, markCancelled } = useSubscriptionStatus()

onMounted(() => { if (isPremium.value) fetchStatus() })

// Clear local cancellation message when reactivation happens (shared state updated via Profile modal)
watch(() => subStatus.value.cancel_at_period_end, (isPending) => {
  if (!isPending) cancelledUntil.value = undefined
})

function fmtDate(ts) {
  return ts ? new Date(ts * 1000).toLocaleDateString() : '—'
}

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

async function confirmCancel() {
  cancelLoading.value = true
  error.value = ''
  try {
    const { data } = await client.post('/api/subscription/cancel')
    const date = data.ends_at
      ? new Date(data.ends_at * 1000).toLocaleDateString()
      : null
    cancelledUntil.value = date
    cancelConfirm.value = false
    markCancelled(data.ends_at)
  } catch {
    error.value = t('subscriptions.cancelError')
  } finally {
    cancelLoading.value = false
  }
}
</script>
