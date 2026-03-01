<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold">Dashboard</h1>
      <YearSelector />
    </div>

    <!-- Summary cards -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="bg-gray-900 border border-gray-800 rounded-xl p-4">
        <p class="text-xs text-gray-400 uppercase tracking-wide mb-1">
          Dividends {{ store.currentYear }}
        </p>
        <p class="text-2xl font-bold text-emerald-400">{{ settings.fmt(totalDividends) }}</p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-xl p-4">
        <p class="text-xs text-gray-400 uppercase tracking-wide mb-1">
          Yields {{ store.currentYear }}
        </p>
        <p class="text-2xl font-bold text-blue-400">{{ settings.fmt(totalYields) }}</p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-xl p-4">
        <p class="text-xs text-gray-400 uppercase tracking-wide mb-1">
          Combined {{ store.currentYear }}
        </p>
        <p class="text-2xl font-bold text-white">{{ settings.fmt(totalDividends + totalYields) }}</p>
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
          {{ activeTab === 'monthly' ? `Monthly breakdown — ${store.currentYear}` : 'Income by year' }}
        </p>
        <MonthlyChart v-if="activeTab === 'monthly'" />
        <YearlyChart v-else />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useDataStore } from '../stores/dataStore.js'
import { useSettingsStore } from '../stores/settingsStore.js'
import YearSelector from '../components/YearSelector.vue'
import MonthlyChart from '../components/MonthlyChart.vue'
import YearlyChart from '../components/YearlyChart.vue'

const store = useDataStore()
const settings = useSettingsStore()

const tabs = [
  { value: 'monthly', label: 'Monthly' },
  { value: 'yearly', label: 'Yearly' },
]
const activeTab = ref('monthly')

function sumSection(section) {
  return Object.values(section)
    .flatMap((e) => Object.values(e.months || {}))
    .reduce((a, b) => a + b, 0)
}

const totalDividends = computed(() => sumSection(store.yearData.dividends || {}))
const totalYields = computed(() => sumSection(store.yearData.yields || {}))

onMounted(() => store.loadAllYears())
</script>
