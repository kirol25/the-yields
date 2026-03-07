<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between gap-3 flex-wrap">
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

    <!-- Goal donuts (monthly tab only) — always 3 columns -->
    <div
      v-if="activeTab === 'monthly' && !store.initializing"
      class="grid grid-cols-1 sm:grid-cols-3 gap-4"
      :style="{ opacity: store.loading && !store.initializing ? '0.5' : '' }"
    >
      <!-- Dividend goal -->
      <div class="bg-gray-900 border border-gray-800 rounded-xl p-5 flex items-center gap-5">
        <GoalDonutChart :achieved="totalDividends" :goal="currentYearGoal" color="emerald" />
        <div class="space-y-1.5 min-w-0">
          <p class="text-xs text-gray-400 uppercase tracking-wide">{{ t('dashboard.goalProgress') }} {{ store.currentYear }}</p>
          <p class="text-xl font-bold text-emerald-400">{{ settings.fmt(totalDividends) }}</p>
          <p class="text-xs text-gray-500">
            <template v-if="currentYearGoal > 0">
              {{ totalDividends >= currentYearGoal ? t('dashboard.goalReached') : t('dashboard.goalRemaining', { amount: settings.fmt(currentYearGoal - totalDividends) }) }}
            </template>
            <template v-else>{{ t('dashboard.noGoalSet') }}</template>
          </p>
        </div>
      </div>

      <!-- Yield goal -->
      <div class="bg-gray-900 border border-gray-800 rounded-xl p-5 flex items-center gap-5">
        <GoalDonutChart :achieved="totalYields" :goal="currentYearYieldGoal" color="blue" />
        <div class="space-y-1.5 min-w-0">
          <p class="text-xs text-gray-400 uppercase tracking-wide">{{ t('dashboard.yieldGoalProgress') }} {{ store.currentYear }}</p>
          <p class="text-xl font-bold text-blue-400">{{ settings.fmt(totalYields) }}</p>
          <p class="text-xs text-gray-500">
            <template v-if="currentYearYieldGoal > 0">
              {{ totalYields >= currentYearYieldGoal ? t('dashboard.goalReached') : t('dashboard.goalRemaining', { amount: settings.fmt(currentYearYieldGoal - totalYields) }) }}
            </template>
            <template v-else>{{ t('dashboard.noGoalSet') }}</template>
          </p>
        </div>
      </div>

      <!-- Steuerfreibetrag -->
      <div class="bg-gray-900 border border-gray-800 rounded-xl p-5 flex items-center gap-5">
        <GoalDonutChart :achieved="totalDividends" :goal="currentYearSteuer" counterclockwise can-exceed />
        <div class="space-y-1.5 min-w-0">
          <p class="text-xs text-gray-400 uppercase tracking-wide">{{ t('dashboard.steuerProgress') }} {{ store.currentYear }}</p>
          <p class="text-xl font-bold" :class="currentYearSteuer > 0 && totalDividends > currentYearSteuer ? 'text-amber-400' : 'text-amber-300'">
            {{ settings.fmt(totalDividends) }}
          </p>
          <p class="text-xs" :class="currentYearSteuer > 0 && totalDividends > currentYearSteuer ? 'text-amber-500' : 'text-gray-500'">
            <template v-if="currentYearSteuer > 0">
              {{ totalDividends > currentYearSteuer ? t('dashboard.steuerExceeded', { amount: settings.fmt(totalDividends - currentYearSteuer) }) : t('dashboard.steuerRemaining', { amount: settings.fmt(currentYearSteuer - totalDividends) }) }}
            </template>
            <template v-else>{{ t('dashboard.noGoalSet') }}</template>
          </p>
        </div>
      </div>
    </div>

    <!-- Chart card with tabs -->
    <div class="bg-gray-900 border border-gray-800 rounded-xl">
      <!-- Tab bar -->
      <div class="flex border-b border-gray-800 overflow-x-auto scrollbar-none">
        <button
          v-for="tab in tabs"
          :key="tab.value"
          @click="activeTab = tab.value"
          :class="[
            'px-4 sm:px-5 py-3 text-sm font-medium transition-colors border-b-2 -mb-px shrink-0',
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
          <!-- Wrap in blur+overlay when free user is on a premium tab -->
          <div :class="{ 'relative': isLockedTab }">
            <div :class="{ 'blur-sm pointer-events-none select-none': isLockedTab }">
              <p v-if="activeTab === 'monthly' || activeTab === 'quarterly'" class="text-xs text-gray-500 uppercase tracking-wider mb-4">
                {{
                  activeTab === 'monthly'
                    ? t('dashboard.monthlyBreakdown', { year: store.currentYear })
                    : t('dashboard.quarterlyBreakdown', { year: store.currentYear })
                }}
              </p>
              <MonthlyChart v-if="activeTab === 'monthly'" />
              <QuarterlyChart v-else-if="activeTab === 'quarterly'" />
              <template v-else-if="activeTab === 'yearly'">
                <div class="space-y-4">
                  <div class="bg-gray-800 border border-gray-700/60 rounded-xl p-5">
                    <p class="text-xs text-gray-500 uppercase tracking-wider mb-4">{{ t('dashboard.incomeByYear') }}</p>
                    <YearlyChart />
                  </div>
                  <div class="bg-gray-800 border border-gray-700/60 rounded-xl p-5">
                    <p class="text-xs text-gray-500 uppercase tracking-wider mb-4">{{ t('dashboard.topEarners') }}</p>
                    <TopEarnersChart all-years />
                  </div>
                  <div class="bg-gray-800 border border-gray-700/60 rounded-xl p-5">
                    <p class="text-xs text-gray-500 uppercase tracking-wider mb-4">{{ t('dashboard.heatmap') }}</p>
                    <IncomeHeatmap />
                  </div>
                </div>
              </template>
              <template v-else-if="activeTab === 'cumulative'">
                <p class="text-xs text-gray-500 uppercase tracking-wider mb-4">{{ t('dashboard.cumulativeThisYear', { year: store.currentYear }) }}</p>
                <CumulativeChart />
                <template v-if="store.years.length > 1">
                  <div class="border-t border-gray-800 mt-10 pt-8">
                    <p class="text-xs text-gray-500 uppercase tracking-wider mb-4">{{ t('dashboard.cumulativeAllYears') }}</p>
                    <YearlyCumulativeChart />
                  </div>
                </template>
              </template>
              <template v-else-if="activeTab === 'breakdown'">
                <div class="space-y-4">
                  <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    <div class="bg-gray-800 border border-gray-700/60 rounded-xl p-5">
                      <p class="text-xs text-gray-500 uppercase tracking-wider mb-4">{{ t('dashboard.dividends') }}</p>
                      <PortfolioBreakdown section="dividends" />
                    </div>
                    <div class="bg-gray-800 border border-gray-700/60 rounded-xl p-5">
                      <p class="text-xs text-gray-500 uppercase tracking-wider mb-4">{{ t('dashboard.yields') }}</p>
                      <PortfolioBreakdown section="yields" />
                    </div>
                  </div>
                  <div class="bg-gray-800 border border-gray-700/60 rounded-xl p-5">
                    <p class="text-xs text-gray-500 uppercase tracking-wider mb-4">{{ t('dashboard.topEarners') }}</p>
                    <TopEarnersChart />
                  </div>
                </div>
              </template>
            </div>

            <!-- Upsell overlay (only shown for free users on premium tabs) -->
            <div v-if="isLockedTab" class="absolute inset-0 flex flex-col items-center justify-center">
              <div class="bg-gray-900/80 backdrop-blur-sm border border-gray-700 rounded-2xl px-8 py-6 shadow-xl flex flex-col items-center gap-3 text-center">
                <svg class="w-8 h-8 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                </svg>
                <div>
                  <p class="text-sm font-semibold text-gray-100">{{ t('upsell.analyticsTitle') }}</p>
                  <p class="text-xs text-gray-400 mt-1 max-w-xs">{{ t('upsell.analyticsDesc') }}</p>
                </div>
                <RouterLink to="/subscriptions" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-sm font-medium rounded-lg transition-colors">
                  {{ t('upsell.upgrade') }}
                </RouterLink>
              </div>
            </div>
          </div>
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
import { useSubscription } from '../composables/useSubscription.js'
import YearSelector from '../components/YearSelector.vue'
import MonthlyChart from '../components/MonthlyChart.vue'
import QuarterlyChart from '../components/QuarterlyChart.vue'
import YearlyChart from '../components/YearlyChart.vue'
import PortfolioBreakdown from '../components/PortfolioBreakdown.vue'
import TopEarnersChart from '../components/TopEarnersChart.vue'
import CumulativeChart from '../components/CumulativeChart.vue'
import YearlyCumulativeChart from '../components/YearlyCumulativeChart.vue'
import IncomeHeatmap from '../components/IncomeHeatmap.vue'
import SkeletonBlock from '../components/SkeletonBlock.vue'
import GoalDonutChart from '../components/GoalDonutChart.vue'

const { t } = useI18n()
const store = useDataStore()
const settings = useSettingsStore()
const { isPremium } = useSubscription()

const tabs = computed(() => [
  { value: 'monthly',    label: t('dashboard.monthly'),    premium: false },
  { value: 'quarterly',  label: t('dashboard.quarterly'),  premium: true },
  { value: 'yearly',     label: t('dashboard.yearly'),     premium: true },
  { value: 'cumulative', label: t('dashboard.cumulative'), premium: true },
  { value: 'breakdown',  label: t('dashboard.breakdown'),  premium: true },
])
const activeTab = ref('monthly')

const isLockedTab = computed(
  () => !isPremium.value && tabs.value.find((t) => t.value === activeTab.value)?.premium === true,
)

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

const currentYearGoal      = computed(() => settings.dividendGoal[store.currentYear] || 0)
const currentYearYieldGoal = computed(() => settings.yieldGoal[store.currentYear] || 0)
const currentYearSteuer    = computed(() => settings.steuerfreibetrag[store.currentYear] ?? 1000)

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
