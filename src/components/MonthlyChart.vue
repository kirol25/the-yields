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
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { useDataStore } from '../stores/dataStore.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
)

const store = useDataStore()
const filter = ref('all')

const filterOptions = [
  { value: 'all', label: 'All' },
  { value: 'dividends', label: 'Dividends' },
  { value: 'yields', label: 'Yields' },
]

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
const MONTH_KEYS = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']

function sumByMonth(section) {
  const totals = Array(12).fill(0)
  for (const entry of Object.values(section)) {
    const months = entry.months || {}
    MONTH_KEYS.forEach((key, i) => {
      totals[i] += months[key] || 0
    })
  }
  return totals
}

const dividendTotals = computed(() => sumByMonth(store.yearData.dividends || {}))
const yieldTotals = computed(() => sumByMonth(store.yearData.yields || {}))

const hasData = computed(() => {
  return (
    dividendTotals.value.some((v) => v > 0) || yieldTotals.value.some((v) => v > 0)
  )
})

const chartData = computed(() => {
  const datasets = []
  if (filter.value !== 'yields') {
    datasets.push({
      label: 'Dividends',
      data: dividendTotals.value,
      backgroundColor: 'rgba(52, 211, 153, 0.8)',
      borderColor: 'rgb(52, 211, 153)',
      borderWidth: 1,
      stack: 'combined',
    })
  }
  if (filter.value !== 'dividends') {
    datasets.push({
      label: 'Yields',
      data: yieldTotals.value,
      backgroundColor: 'rgba(96, 165, 250, 0.8)',
      borderColor: 'rgb(96, 165, 250)',
      borderWidth: 1,
      stack: 'combined',
    })
  }
  return { labels: MONTHS, datasets }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      labels: { color: '#d1d5db' },
    },
    tooltip: {
      callbacks: {
        label: (ctx) => ` ${ctx.dataset.label}: $${ctx.parsed.y.toFixed(2)}`,
      },
    },
  },
  scales: {
    x: {
      stacked: true,
      ticks: { color: '#9ca3af' },
      grid: { color: 'rgba(75,85,99,0.3)' },
    },
    y: {
      stacked: true,
      ticks: {
        color: '#9ca3af',
        callback: (v) => `$${v}`,
      },
      grid: { color: 'rgba(75,85,99,0.3)' },
    },
  },
}
</script>
