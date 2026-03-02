<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold">{{ t('dashboard.title') }}</h1>
      <YearSelector v-if="activeTab !== 'yearly'" />
    </div>

    <!-- Summary cards -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
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
      <div class="p-6">
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
</script>
