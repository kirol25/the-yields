<template>
  <div>
    <div v-if="hasData" class="relative h-80">
      <Bar :data="chartData" :options="chartOptions" :plugins="plugins" />
    </div>
    <div v-else class="flex items-center justify-center h-64 text-gray-500 text-sm">
      No yearly data available yet. Add entries across multiple years to see trends.
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
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

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const store = useDataStore()
const settings = useSettingsStore()

const plugins = [ChartDataLabels]

function sectionTotal(data, section) {
  return Object.values(data[section] || {})
    .flatMap((e) => Object.values(e.months || {}))
    .reduce((a, b) => a + b, 0)
}

const ascYears = computed(() => store.years.slice().reverse())

const ascDividends = computed(() =>
  ascYears.value.map((y) => sectionTotal(store.allYearsData[y] || {}, 'dividends')),
)

const ascYields = computed(() =>
  ascYears.value.map((y) => sectionTotal(store.allYearsData[y] || {}, 'yields')),
)

const hasData = computed(
  () => ascDividends.value.some((v) => v > 0) || ascYields.value.some((v) => v > 0),
)

const chartData = computed(() => ({
  labels: ascYears.value.map(String),
  datasets: [
    {
      label: 'Dividends',
      data: ascDividends.value,
      backgroundColor: 'rgba(52, 211, 153, 0.8)',
      borderColor: 'rgb(52, 211, 153)',
      borderWidth: 1,
      borderRadius: 4,
    },
    {
      label: 'Yields',
      data: ascYields.value,
      backgroundColor: 'rgba(96, 165, 250, 0.8)',
      borderColor: 'rgb(96, 165, 250)',
      borderWidth: 1,
      borderRadius: 4,
    },
  ],
}))

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
        footer: (items) => {
          const total = items.reduce((s, i) => s + i.parsed.y, 0)
          return `Total: ${settings.fmt(total)}`
        },
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
  }
})
</script>
