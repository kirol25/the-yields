<template>
  <div>
    <Bar v-if="hasData" :data="chartData" :options="chartOptions" class="h-80" />
    <div v-else class="flex items-center justify-center h-64 text-gray-500 text-sm">
      No yearly data available yet. Add entries across multiple years to see trends.
    </div>

    <!-- Yearly summary table -->
    <div v-if="hasData" class="mt-6 grid grid-cols-2 sm:grid-cols-4 gap-3">
      <div
        v-for="(year, i) in store.years"
        :key="year"
        class="bg-gray-800/50 rounded-lg p-3 text-center"
      >
        <p class="text-xs text-gray-500 uppercase tracking-wide mb-2">{{ year }}</p>
        <p class="text-sm font-medium text-emerald-400">{{ settings.fmt(dividendsByYear[i]) }}</p>
        <p class="text-sm font-medium text-blue-400">{{ settings.fmt(yieldsByYear[i]) }}</p>
        <p class="text-xs text-gray-500 mt-1 border-t border-gray-700 pt-1">
          {{ settings.fmt(dividendsByYear[i] + yieldsByYear[i]) }}
        </p>
      </div>
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
import { useDataStore } from '../stores/dataStore.js'
import { useSettingsStore } from '../stores/settingsStore.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const store = useDataStore()
const settings = useSettingsStore()

function sectionTotal(data, section) {
  return Object.values(data[section] || {})
    .flatMap((e) => Object.values(e.months || {}))
    .reduce((a, b) => a + b, 0)
}

const dividendsByYear = computed(() =>
  store.years.map((y) => sectionTotal(store.allYearsData[y] || {}, 'dividends')),
)

const yieldsByYear = computed(() =>
  store.years.map((y) => sectionTotal(store.allYearsData[y] || {}, 'yields')),
)

const hasData = computed(
  () => dividendsByYear.value.some((v) => v > 0) || yieldsByYear.value.some((v) => v > 0),
)

const chartData = computed(() => ({
  labels: store.years.map(String),
  datasets: [
    {
      label: 'Dividends',
      data: dividendsByYear.value,
      backgroundColor: 'rgba(52, 211, 153, 0.8)',
      borderColor: 'rgb(52, 211, 153)',
      borderWidth: 1,
      borderRadius: 4,
    },
    {
      label: 'Yields',
      data: yieldsByYear.value,
      backgroundColor: 'rgba(96, 165, 250, 0.8)',
      borderColor: 'rgb(96, 165, 250)',
      borderWidth: 1,
      borderRadius: 4,
    },
  ],
}))

const chartOptions = computed(() => ({
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
