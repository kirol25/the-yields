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

    <Line v-if="hasData" :data="chartData" :options="chartOptions" class="max-h-80" />
    <div v-else class="flex items-center justify-center h-64 text-gray-500 text-sm">
      {{ t('dashboard.noDataForYear', { year: store.currentYear }) }}
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  LineElement,
  PointElement,
  Filler,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { useI18n } from 'vue-i18n'
import { useDataStore } from '../stores/dataStore.js'
import { useSettingsStore } from '../stores/settingsStore.js'
import { MONTHS as MONTHS_CONFIG } from '../config.js'

ChartJS.register(CategoryScale, LinearScale, LineElement, PointElement, Filler, Title, Tooltip, Legend)

const { t } = useI18n()
const store = useDataStore()
const settings = useSettingsStore()

const filter = ref('all')
const filterOptions = computed(() => [
  { value: 'all',       label: t('dashboard.combined') },
  { value: 'dividends', label: t('dashboard.dividends') },
  { value: 'yields',    label: t('dashboard.yields') },
])

function sumByMonth(section) {
  return MONTHS_CONFIG.map(({ value }) =>
    Object.values(section).reduce((s, e) => s + (e.months?.[value] || 0), 0),
  )
}

function cumulate(arr) {
  let running = 0
  return arr.map((v) => (running += v))
}

const dividendMonthly = computed(() => sumByMonth(store.yearData.dividends || {}))
const yieldMonthly    = computed(() => sumByMonth(store.yearData.yields || {}))
const combinedMonthly = computed(() => dividendMonthly.value.map((v, i) => v + yieldMonthly.value[i]))

const dividendCumul = computed(() => cumulate(dividendMonthly.value))
const yieldCumul    = computed(() => cumulate(yieldMonthly.value))
const combinedCumul = computed(() => cumulate(combinedMonthly.value))

const hasData = computed(() =>
  dividendMonthly.value.some((v) => v > 0) || yieldMonthly.value.some((v) => v > 0),
)

const chartData = computed(() => {
  const datasets = []
  const isAll = filter.value === 'all'

  if (isAll || filter.value === 'dividends') {
    datasets.push({
      label: t('dashboard.dividends'),
      data: dividendCumul.value,
      borderColor: 'rgb(52, 211, 153)',
      backgroundColor: 'rgba(52, 211, 153, 0.08)',
      fill: true,
      tension: 0.35,
      pointRadius: 3,
      pointHoverRadius: 5,
    })
  }

  if (isAll || filter.value === 'yields') {
    datasets.push({
      label: t('dashboard.yields'),
      data: yieldCumul.value,
      borderColor: 'rgb(96, 165, 250)',
      backgroundColor: 'rgba(96, 165, 250, 0.08)',
      fill: true,
      tension: 0.35,
      pointRadius: 3,
      pointHoverRadius: 5,
    })
  }

  if (isAll) {
    datasets.push({
      label: t('dashboard.combined'),
      data: combinedCumul.value,
      borderColor: 'rgba(255,255,255,0.6)',
      backgroundColor: 'transparent',
      fill: false,
      tension: 0.35,
      borderWidth: 1.5,
      pointRadius: 2,
      pointHoverRadius: 4,
    })
  }

  return { labels: MONTHS_CONFIG.map((m) => m.short), datasets }
})

const chartOptions = computed(() => {
  void settings.currency
  return {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
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
        min: 0,
      },
    },
  }
})
</script>
