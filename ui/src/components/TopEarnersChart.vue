<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <div class="flex gap-2">
        <button
          v-for="opt in filterOptions"
          :key="opt.value"
          @click="filter = opt.value"
          :class="[
            'px-3 py-1 rounded-full text-xs font-medium transition-colors',
            filter === opt.value
              ? 'bg-emerald-600 text-white'
              : 'bg-gray-700 text-gray-400 hover:bg-gray-600',
          ]"
        >
          {{ opt.label }}
        </button>
      </div>
      <div class="flex gap-1.5">
        <button
          v-for="n in limitOptions"
          :key="n"
          @click="limit = n"
          :class="[
            'px-2.5 py-1 rounded-full text-xs font-medium transition-colors',
            limit === n
              ? 'bg-gray-600 text-gray-100'
              : 'bg-gray-800 text-gray-500 hover:bg-gray-700',
          ]"
        >
          Top {{ n }}
        </button>
      </div>
    </div>

    <div v-if="items.length > 0">
      <Bar :data="chartData" :options="chartOptions" :plugins="[ChartDataLabels]" :style="{ height: chartHeight + 'px' }" />
    </div>
    <p v-else class="text-sm text-gray-600 text-center py-6">
      {{ t('dashboard.noDataForYear', { year: store.currentYear }) }}
    </p>
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
  Tooltip,
  Legend,
} from 'chart.js'
import ChartDataLabels from 'chartjs-plugin-datalabels'
import { useI18n } from 'vue-i18n'

import { useDataStore } from '../stores/dataStore.js'
import { useSettingsStore } from '../stores/settingsStore.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend)

const { t } = useI18n()
const store = useDataStore()
const settings = useSettingsStore()

const props = defineProps({
  allYears: { type: Boolean, default: false },
})

const filter = ref('all')
const filterOptions = computed(() => [
  { value: 'all',       label: t('dashboard.combined') },
  { value: 'dividends', label: t('dashboard.dividends') },
  { value: 'yields',    label: t('dashboard.yields') },
])

const limit = ref(10)
const limitOptions = [10, 20, 50]

function sumSection(sectionData) {
  // returns { key: { amount, label } }
  const totals = {}
  for (const [key, entry] of Object.entries(sectionData || {})) {
    const amount = Object.values(entry.months || {}).reduce((a, b) => a + b, 0)
    if (!totals[key]) totals[key] = { amount: 0, label: entry.name || key }
    totals[key].amount += amount
  }
  return totals
}

const items = computed(() => {
  const dividendTotals = {}
  const yieldTotals = {}

  const yearDatasets = props.allYears
    ? Object.values(store.allYearsData)
    : [store.yearData]

  for (const data of yearDatasets) {
    for (const [k, v] of Object.entries(sumSection(data.dividends))) {
      if (!dividendTotals[k]) dividendTotals[k] = { amount: 0, label: v.label }
      dividendTotals[k].amount += v.amount
    }
    for (const [k, v] of Object.entries(sumSection(data.yields))) {
      if (!yieldTotals[k]) yieldTotals[k] = { amount: 0, label: v.label }
      yieldTotals[k].amount += v.amount
    }
  }

  const result = []

  if (filter.value !== 'yields') {
    for (const { label, amount } of Object.values(dividendTotals)) {
      if (amount > 0) result.push({ label, amount, type: 'dividend' })
    }
  }

  if (filter.value !== 'dividends') {
    for (const { label, amount } of Object.values(yieldTotals)) {
      if (amount > 0) result.push({ label, amount, type: 'yield' })
    }
  }

  return result.sort((a, b) => b.amount - a.amount).slice(0, limit.value)
})

const chartHeight = computed(() => Math.max(items.value.length * 40, 80))

const chartData = computed(() => ({
  labels: items.value.map((i) => i.label),
  datasets: [
    {
      data: items.value.map((i) => i.amount),
      backgroundColor: items.value.map((i) =>
        i.type === 'dividend' ? 'rgba(52, 211, 153, 0.75)' : 'rgba(96, 165, 250, 0.75)',
      ),
      borderColor: items.value.map((i) =>
        i.type === 'dividend' ? 'rgb(52, 211, 153)' : 'rgb(96, 165, 250)',
      ),
      borderWidth: 1,
      borderRadius: 4,
    },
  ],
}))

const chartOptions = computed(() => {
  void settings.currency
  return {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (ctx) => ` ${settings.fmt(ctx.parsed.x)}`,
        },
      },
      datalabels: {
        anchor: 'end',
        align: 'end',
        color: '#9ca3af',
        font: { size: 11, weight: '500' },
        formatter: (v) => settings.fmt(v),
      },
    },
    scales: {
      x: {
        ticks: { color: '#9ca3af', callback: (v) => settings.fmt(v) },
        grid: { color: 'rgba(75,85,99,0.3)' },
      },
      y: {
        ticks: { color: '#d1d5db', font: { family: 'monospace', size: 12 } },
        grid: { display: false },
      },
    },
    layout: { padding: { right: 80 } },
  }
})
</script>
