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
    <Bar v-if="hasData" :data="chartData" :options="chartOptions" :plugins="plugins" class="max-h-80" />
    <div v-else class="flex items-center justify-center h-64 text-gray-500 text-sm">
      No data for {{ store.currentYear }}. Add dividends or yields to get started.
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
import ChartDataLabels from 'chartjs-plugin-datalabels'
import { useDataStore } from '../stores/dataStore.js'
import { useSettingsStore } from '../stores/settingsStore.js'
import { MONTHS as MONTHS_CONFIG } from '../config.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const store = useDataStore()
const settings = useSettingsStore()
const filter = ref('all')
const plugins = [ChartDataLabels]

const filterOptions = [
  { value: 'all', label: 'All' },
  { value: 'dividends', label: 'Dividends only' },
  { value: 'yields', label: 'Yields only' },
]

function sumByMonth(section) {
  const totals = Array(12).fill(0)
  for (const entry of Object.values(section)) {
    const months = entry.months || {}
    MONTHS_CONFIG.forEach(({ value }, i) => {
      totals[i] += months[value] || 0
    })
  }
  return totals
}

const dividendTotals = computed(() => sumByMonth(store.yearData.dividends || {}))
const yieldTotals = computed(() => sumByMonth(store.yearData.yields || {}))

const hasData = computed(
  () => dividendTotals.value.some((v) => v > 0) || yieldTotals.value.some((v) => v > 0),
)

const chartData = computed(() => {
  const datasets = []
  if (filter.value !== 'yields') {
    datasets.push({
      label: 'Dividends',
      data: dividendTotals.value,
      backgroundColor: 'rgba(52, 211, 153, 0.8)',
      borderColor: 'rgb(52, 211, 153)',
      borderWidth: 1,
      borderRadius: 4,
    })
  }
  if (filter.value !== 'dividends') {
    datasets.push({
      label: 'Yields',
      data: yieldTotals.value,
      backgroundColor: 'rgba(96, 165, 250, 0.8)',
      borderColor: 'rgb(96, 165, 250)',
      borderWidth: 1,
      borderRadius: 4,
    })
  }
  return { labels: MONTHS_CONFIG.map((m) => m.short), datasets }
})

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { labels: { color: '#d1d5db' } },
    tooltip: {
      callbacks: {
        label: (ctx) => ` ${ctx.dataset.label}: ${settings.fmt(ctx.parsed.y)}`,
      },
    },
    datalabels: {
      anchor: 'end',
      align: 'end',
      offset: 2,
      color: '#9ca3af',
      font: { size: 10, weight: '500' },
      formatter: (value) => value > 0 ? settings.fmt(value) : '',
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
}))
</script>
