<template>
  <div>
    <div class="flex gap-3 mb-4">
      <button
        v-for="opt in filterOptions"
        :key="opt.value"
        @click="filter = opt.value"
        :class="[
          'px-3 py-1 rounded-full text-xs font-medium transition-colors',
          filter === opt.value
            ? 'bg-emerald-600 text-white'
            : 'bg-gray-800 text-gray-400 hover:bg-gray-700',
        ]"
      >
        {{ opt.label }}
      </button>
    </div>

    <Bar v-if="hasData" :data="chartData" :options="chartOptions" class="max-h-80" />
    <div v-else class="flex items-center justify-center h-64 text-gray-500 text-sm">
      No data for {{ store.currentYear }}. Add dividends or yields to get started.
    </div>

    <!-- Quarterly summary table -->
    <div v-if="hasData" class="mt-6 grid grid-cols-4 gap-3">
      <div
        v-for="(q, i) in QUARTERS"
        :key="q.label"
        class="bg-gray-800/50 rounded-lg p-3 text-center"
      >
        <p class="text-xs text-gray-500 uppercase tracking-wide mb-2">{{ q.label }}</p>
        <p v-if="filter !== 'yields'" class="text-sm font-medium text-emerald-400">
          {{ settings.fmt(dividendTotals[i]) }}
        </p>
        <p v-if="filter !== 'dividends'" class="text-sm font-medium text-blue-400">
          {{ settings.fmt(yieldTotals[i]) }}
        </p>
        <p v-if="filter === 'all'" class="text-xs text-gray-500 mt-1 border-t border-gray-700 pt-1">
          {{ settings.fmt(dividendTotals[i] + yieldTotals[i]) }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { useI18n } from 'vue-i18n'
import { useDataStore } from '../stores/dataStore.js'
import { useSettingsStore } from '../stores/settingsStore.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const { t } = useI18n()
const store = useDataStore()
const settings = useSettingsStore()
const filter = ref('all')

const filterOptions = computed(() => [
  { value: 'all', label: t('dashboard.combined') },
  { value: 'dividends', label: t('dashboard.dividends') },
  { value: 'yields', label: t('dashboard.yields') },
])

const QUARTERS = [
  { label: 'Q1', months: ['01', '02', '03'] },
  { label: 'Q2', months: ['04', '05', '06'] },
  { label: 'Q3', months: ['07', '08', '09'] },
  { label: 'Q4', months: ['10', '11', '12'] },
]

function sumByQuarter(section) {
  return QUARTERS.map(({ months }) =>
    Object.values(section).reduce((total, entry) => {
      return total + months.reduce((s, m) => s + (entry.months?.[m] || 0), 0)
    }, 0),
  )
}

const dividendTotals = computed(() => sumByQuarter(store.yearData.dividends || {}))
const yieldTotals = computed(() => sumByQuarter(store.yearData.yields || {}))

const hasData = computed(
  () => dividendTotals.value.some((v) => v > 0) || yieldTotals.value.some((v) => v > 0),
)

const chartData = computed(() => {
  const datasets = []
  if (filter.value !== 'yields') {
    datasets.push({
      label: t('dashboard.dividends'),
      data: dividendTotals.value,
      backgroundColor: 'rgba(52, 211, 153, 0.8)',
      borderColor: 'rgb(52, 211, 153)',
      borderWidth: 1,
      borderRadius: 4,
    })
  }
  if (filter.value !== 'dividends') {
    datasets.push({
      label: t('dashboard.yields'),
      data: yieldTotals.value,
      backgroundColor: 'rgba(96, 165, 250, 0.8)',
      borderColor: 'rgb(96, 165, 250)',
      borderWidth: 1,
      borderRadius: 4,
    })
  }
  return { labels: QUARTERS.map((q) => q.label), datasets }
})

const chartOptions = computed(() => {
  void settings.currency // track as reactive dependency
  return {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { labels: { color: '#d1d5db' } },
    tooltip: {
      callbacks: {
        label: (ctx) => ` ${ctx.dataset.label}: ${settings.fmt(ctx.parsed.y)}`,
      },
    },
  },
  scales: {
    x: {
      ticks: { color: '#9ca3af' },
      grid: { color: 'rgba(75,85,99,0.3)' },
    },
    y: {
      ticks: { color: '#9ca3af', callback: (v) => settings.fmt(v) },
      grid: { color: 'rgba(75,85,99,0.3)' },
    },
  },
  }
})
</script>
