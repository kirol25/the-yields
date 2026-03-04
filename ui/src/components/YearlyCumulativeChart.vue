<template>
  <Line :data="chartData" :options="chartOptions" class="max-h-64" />
</template>

<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  LineElement,
  PointElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js'
import { useDataStore } from '../stores/dataStore.js'
import { useSettingsStore } from '../stores/settingsStore.js'
import { useI18n } from 'vue-i18n'

ChartJS.register(CategoryScale, LinearScale, LineElement, PointElement, Filler, Tooltip, Legend)

const { t } = useI18n()
const store = useDataStore()
const settings = useSettingsStore()

function sectionTotal(data, section) {
  return Object.values(data[section] || {})
    .flatMap((e) => Object.values(e.months || {}))
    .reduce((a, b) => a + b, 0)
}

function cumulate(arr) {
  let running = 0
  return arr.map((v) => (running += v))
}

const ascYears = computed(() => store.years.slice().reverse())

const cumulDividends = computed(() =>
  cumulate(ascYears.value.map((y) => sectionTotal(store.allYearsData[y] || {}, 'dividends'))),
)
const cumulYields = computed(() =>
  cumulate(ascYears.value.map((y) => sectionTotal(store.allYearsData[y] || {}, 'yields'))),
)
const cumulCombined = computed(() =>
  cumulDividends.value.map((d, i) => d + cumulYields.value[i]),
)

const chartData = computed(() => ({
  labels: ascYears.value.map(String),
  datasets: [
    {
      label: t('dashboard.dividends'),
      data: cumulDividends.value,
      borderColor: 'rgb(52, 211, 153)',
      backgroundColor: 'rgba(52, 211, 153, 0.08)',
      fill: true,
      tension: 0.35,
      pointRadius: 4,
      pointHoverRadius: 6,
    },
    {
      label: t('dashboard.yields'),
      data: cumulYields.value,
      borderColor: 'rgb(96, 165, 250)',
      backgroundColor: 'rgba(96, 165, 250, 0.08)',
      fill: true,
      tension: 0.35,
      pointRadius: 4,
      pointHoverRadius: 6,
    },
    {
      label: t('dashboard.combined'),
      data: cumulCombined.value,
      borderColor: 'rgba(255,255,255,0.5)',
      backgroundColor: 'transparent',
      fill: false,
      tension: 0.35,
      borderWidth: 1.5,
      borderDash: [4, 3],
      pointRadius: 3,
      pointHoverRadius: 5,
    },
  ],
}))

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
