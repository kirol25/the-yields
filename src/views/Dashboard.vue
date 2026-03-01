<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold">Dashboard</h1>
      <YearSelector />
    </div>

    <!-- Summary cards -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="bg-gray-900 border border-gray-800 rounded-xl p-4">
        <p class="text-xs text-gray-400 uppercase tracking-wide mb-1">Total Dividends</p>
        <p class="text-2xl font-bold text-emerald-400">${{ totalDividends }}</p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-xl p-4">
        <p class="text-xs text-gray-400 uppercase tracking-wide mb-1">Total Yields</p>
        <p class="text-2xl font-bold text-blue-400">${{ totalYields }}</p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-xl p-4">
        <p class="text-xs text-gray-400 uppercase tracking-wide mb-1">Combined Income</p>
        <p class="text-2xl font-bold text-white">${{ combined }}</p>
      </div>
    </div>

    <!-- Chart -->
    <div class="bg-gray-900 border border-gray-800 rounded-xl p-6">
      <h2 class="text-sm font-medium text-gray-400 uppercase tracking-wide mb-4">
        Monthly Income — {{ store.currentYear }}
      </h2>
      <MonthlyChart />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useDataStore } from '../stores/dataStore.js'
import YearSelector from '../components/YearSelector.vue'
import MonthlyChart from '../components/MonthlyChart.vue'

const store = useDataStore()

function sumSection(section) {
  return Object.values(section)
    .flatMap((e) => Object.values(e.months || {}))
    .reduce((a, b) => a + b, 0)
    .toFixed(2)
}

const totalDividends = computed(() => sumSection(store.yearData.dividends || {}))
const totalYields = computed(() => sumSection(store.yearData.yields || {}))
const combined = computed(() =>
  (parseFloat(totalDividends.value) + parseFloat(totalYields.value)).toFixed(2),
)
</script>
