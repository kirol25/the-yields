<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold">{{ t('dashboard.title') }}</h1>
      <YearSelector v-if="activeTab !== 'yearly'" />
    </div>

    <!-- Summary cards -->
    <div
      class="grid grid-cols-1 sm:grid-cols-3 gap-4"
      :style="{ opacity: store.loading && !store.initializing ? '0.5' : '' }"
    >
      <template v-if="store.initializing">
        <div v-for="i in 3" :key="i" class="bg-gray-900 border border-gray-800 rounded-xl p-4 space-y-3">
          <SkeletonBlock cls="h-3 w-24" />
          <SkeletonBlock cls="h-7 w-32" />
        </div>
      </template>
      <template v-else>
        <div class="bg-gray-900 border border-gray-800 rounded-xl p-4">
          <p class="text-xs text-gray-400 uppercase tracking-wide mb-1">
            {{ t('dashboard.dividends') }}
            <span v-if="activeTab !== 'yearly'">{{ store.currentYear }}</span>
          </p>
          <p class="text-2xl font-bold text-emerald-400">{{ settings.fmt(cardDividends) }}</p>
        </div>
        <div class="bg-gray-900 border border-gray-800 rounded-xl p-4">
          <p class="text-xs text-gray-400 uppercase tracking-wide mb-1">
            {{ t('dashboard.yields') }}
            <span v-if="activeTab !== 'yearly'">{{ store.currentYear }}</span>
          </p>
          <p class="text-2xl font-bold text-blue-400">{{ settings.fmt(cardYields) }}</p>
        </div>
        <div class="bg-gray-900 border border-gray-800 rounded-xl p-4">
          <p class="text-xs text-gray-400 uppercase tracking-wide mb-1">
            {{ t('dashboard.combined') }}
            <span v-if="activeTab !== 'yearly'">{{ store.currentYear }}</span>
          </p>
          <p class="text-2xl font-bold text-white">{{ settings.fmt(cardDividends + cardYields) }}</p>
        </div>
      </template>
    </div>

    <!-- Average cards (monthly tab only) -->
    <div
      v-if="activeTab === 'monthly' && !store.initializing"
      class="grid grid-cols-1 sm:grid-cols-3 gap-4"
      :style="{ opacity: store.loading && !store.initializing ? '0.5' : '' }"
    >
      <div class="bg-gray-900 border border-gray-800 rounded-xl p-4">
        <p class="text-xs text-gray-400 uppercase tracking-wide mb-1">{{ t('dashboard.avgDividends') }}</p>
        <p class="text-2xl font-bold text-emerald-300">{{ settings.fmt(avgMonthlyDividends) }}</p>
        <p v-if="monthsWithDividends > 0" class="text-xs text-gray-600 mt-1">
          {{ t('dashboard.avgPerMonthHint', { n: monthsWithDividends }) }}
        </p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-xl p-4">
        <p class="text-xs text-gray-400 uppercase tracking-wide mb-1">{{ t('dashboard.avgYields') }}</p>
        <p class="text-2xl font-bold text-blue-300">{{ settings.fmt(avgMonthlyYields) }}</p>
        <p v-if="monthsWithYields > 0" class="text-xs text-gray-600 mt-1">
          {{ t('dashboard.avgPerMonthHint', { n: monthsWithYields }) }}
        </p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-xl p-4">
        <p class="text-xs text-gray-400 uppercase tracking-wide mb-1">{{ t('dashboard.avgCombined') }}</p>
        <p class="text-2xl font-bold text-gray-300">{{ settings.fmt(avgMonthlyTotal) }}</p>
        <p v-if="monthsWithAnyData > 0" class="text-xs text-gray-600 mt-1">
          {{ t('dashboard.avgPerMonthHint', { n: monthsWithAnyData }) }}
        </p>
      </div>
    </div>

    <!-- Dividend goal progress (monthly tab only, when a goal is set for this year) -->
    <div
      v-if="activeTab === 'monthly' && currentYearGoal > 0 && !store.initializing"
      class="bg-gray-900 border border-gray-800 rounded-xl p-5 flex items-center gap-6"
      :style="{ opacity: store.loading && !store.initializing ? '0.5' : '' }"
    >
      <GoalDonutChart :achieved="totalDividends" :goal="currentYearGoal" />
      <div class="space-y-1.5 min-w-0">
        <p class="text-xs text-gray-400 uppercase tracking-wide">{{ t('dashboard.goalProgress') }} {{ store.currentYear }}</p>
        <p class="text-2xl font-bold text-emerald-400">
          {{ settings.fmt(totalDividends) }}
          <span class="text-sm font-normal text-gray-500">/ {{ settings.fmt(currentYearGoal) }}</span>
        </p>
        <p class="text-xs text-gray-500">
          {{
            totalDividends >= currentYearGoal
              ? t('dashboard.goalReached')
              : t('dashboard.goalRemaining', { amount: settings.fmt(currentYearGoal - totalDividends) })
          }}
        </p>
      </div>
    </div>

    <!-- Chart card with tabs -->
    <div class="bg-gray-900 border border-gray-800 rounded-xl">
      <!-- Tab bar -->
      <div class="flex border-b border-gray-800">
        <button
          v-for="tab in tabs"
          :key="tab.value"
          @click="activeTab = tab.value"
          :class="[
            'px-5 py-3 text-sm font-medium transition-colors border-b-2 -mb-px',
            activeTab === tab.value
              ? 'border-emerald-500 text-emerald-400'
              : 'border-transparent text-gray-400 hover:text-gray-200',
          ]"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Chart body -->
      <div class="p-6" :class="{ 'opacity-50 transition-opacity': store.loading && !store.initializing }">
        <template v-if="store.initializing">
          <SkeletonBlock cls="h-3 w-48 mb-4" />
          <SkeletonBlock cls="h-48 w-full rounded-lg" />
        </template>
        <template v-else>
          <p class="text-xs text-gray-500 uppercase tracking-wider mb-4">
            {{
              activeTab === 'monthly'
                ? t('dashboard.monthlyBreakdown', { year: store.currentYear })
                : activeTab === 'quarterly'
                ? t('dashboard.quarterlyBreakdown', { year: store.currentYear })
                : t('dashboard.incomeByYear')
            }}
          </p>
          <MonthlyChart v-if="activeTab === 'monthly'" />
          <QuarterlyChart v-else-if="activeTab === 'quarterly'" />
          <YearlyChart v-else />
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDataStore } from '../stores/dataStore.js'
import { useSettingsStore } from '../stores/settingsStore.js'
import YearSelector from '../components/YearSelector.vue'
import MonthlyChart from '../components/MonthlyChart.vue'
import QuarterlyChart from '../components/QuarterlyChart.vue'
import YearlyChart from '../components/YearlyChart.vue'
import SkeletonBlock from '../components/SkeletonBlock.vue'
import GoalDonutChart from '../components/GoalDonutChart.vue'

const { t } = useI18n()
const store = useDataStore()
const settings = useSettingsStore()

const tabs = computed(() => [
  { value: 'monthly', label: t('dashboard.monthly') },
  { value: 'quarterly', label: t('dashboard.quarterly') },
  { value: 'yearly', label: t('dashboard.yearly') },
])
const activeTab = ref('monthly')

function sumSection(section) {
  return Object.values(section)
    .flatMap((e) => Object.values(e.months || {}))
    .reduce((a, b) => a + b, 0)
}

const totalDividends = computed(() => sumSection(store.yearData.dividends || {}))
const totalYields = computed(() => sumSection(store.yearData.yields || {}))

const allYearsDividends = computed(() =>
  Object.values(store.allYearsData).reduce((sum, d) => sum + sumSection(d.dividends || {}), 0),
)
const allYearsYields = computed(() =>
  Object.values(store.allYearsData).reduce((sum, d) => sum + sumSection(d.yields || {}), 0),
)

const cardDividends = computed(() => activeTab.value === 'yearly' ? allYearsDividends.value : totalDividends.value)
const cardYields = computed(() => activeTab.value === 'yearly' ? allYearsYields.value : totalYields.value)

const currentYearGoal = computed(() => settings.dividendGoal[store.currentYear] || 0)

function monthsWithData(section) {
  const months = new Set()
  for (const entry of Object.values(section)) {
    for (const [month, val] of Object.entries(entry.months || {})) {
      if (val > 0) months.add(month)
    }
  }
  return months.size
}

const monthsWithDividends = computed(() => monthsWithData(store.yearData.dividends || {}))
const monthsWithYields    = computed(() => monthsWithData(store.yearData.yields || {}))
const monthsWithAnyData   = computed(() => {
  const months = new Set()
  for (const section of [store.yearData.dividends || {}, store.yearData.yields || {}]) {
    for (const entry of Object.values(section)) {
      for (const [month, val] of Object.entries(entry.months || {})) {
        if (val > 0) months.add(month)
      }
    }
  }
  return months.size
})

const avgMonthlyDividends = computed(() =>
  monthsWithDividends.value > 0 ? totalDividends.value / monthsWithDividends.value : 0,
)
const avgMonthlyYields = computed(() =>
  monthsWithYields.value > 0 ? totalYields.value / monthsWithYields.value : 0,
)
const avgMonthlyTotal = computed(() =>
  monthsWithAnyData.value > 0 ? (totalDividends.value + totalYields.value) / monthsWithAnyData.value : 0,
)
</script>
