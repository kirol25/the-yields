<template>
  <div>
    <!-- Filter -->
    <div class="flex gap-2 mb-5">
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

    <template v-if="hasData">
      <!-- Scrollable grid -->
      <div class="overflow-x-auto scrollbar-none">
        <div class="min-w-[400px]">
          <!-- Month headers -->
          <div class="flex gap-1 mb-1.5" style="padding-left: 2.75rem">
            <div
              v-for="m in MONTHS"
              :key="m.value"
              class="flex-1 text-center text-xs text-gray-500"
            >
              {{ m.short }}
            </div>
          </div>

          <!-- Year rows -->
          <div
            v-for="year in store.years"
            :key="year"
            class="flex items-center gap-1 mb-1"
          >
            <div class="w-9 text-right text-xs text-gray-500 shrink-0 pr-2">{{ year }}</div>
            <div
              v-for="m in MONTHS"
              :key="m.value"
              class="relative group flex-1 h-7 rounded-md transition-transform hover:scale-110 hover:z-10 cursor-default"
              :style="{ backgroundColor: cellColor(grid[year]?.[m.value] ?? 0) }"
            >
              <!-- Tooltip -->
              <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 z-20 hidden group-hover:block pointer-events-none">
                <div class="bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-xs whitespace-nowrap shadow-2xl">
                  <div class="font-medium text-gray-200 mb-0.5">{{ m.label }} {{ year }}</div>
                  <div
                    class="font-mono font-semibold"
                    :class="(grid[year]?.[m.value] ?? 0) > 0 ? 'text-emerald-400' : 'text-gray-600'"
                  >
                    {{ settings.fmt(grid[year]?.[m.value] ?? 0) }}
                  </div>
                </div>
                <div class="w-2 h-2 bg-gray-950 border-r border-b border-gray-700 rotate-45 mx-auto -mt-1" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <p v-else class="text-sm text-gray-600 text-center py-8">
      {{ t('dashboard.noDataForYear', { year: store.currentYear }) }}
    </p>

    <!-- Legend -->
    <div v-if="hasData" class="flex items-center gap-1.5 mt-4 justify-end">
      <span class="text-xs text-gray-600 mr-1">{{ t('dashboard.less') }}</span>
      <div
        v-for="(c, i) in legendColors"
        :key="i"
        class="w-3.5 h-3.5 rounded-sm"
        :style="{ backgroundColor: c }"
      />
      <span class="text-xs text-gray-600 ml-1">{{ t('dashboard.more') }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDataStore } from '../stores/dataStore.js'
import { useSettingsStore } from '../stores/settingsStore.js'
import { useMonths } from '../composables/useMonths.js'

const { t } = useI18n()
const store = useDataStore()
const settings = useSettingsStore()
const { months: MONTHS } = useMonths()

const filter = ref('all')
const filterOptions = computed(() => [
  { value: 'all',       label: t('dashboard.combined') },
  { value: 'dividends', label: t('dashboard.dividends') },
  { value: 'yields',    label: t('dashboard.yields') },
])

const grid = computed(() => {
  const result = {}
  for (const year of store.years) {
    const data = store.allYearsData[year] || {}
    result[year] = {}
    for (const m of MONTHS.value) {
      let total = 0
      if (filter.value !== 'yields') {
        for (const entry of Object.values(data.dividends || {})) {
          total += entry.months?.[m.value] || 0
        }
      }
      if (filter.value !== 'dividends') {
        for (const entry of Object.values(data.yields || {})) {
          total += entry.months?.[m.value] || 0
        }
      }
      result[year][m.value] = total
    }
  }
  return result
})

const maxValue = computed(() => {
  let max = 0
  for (const yearData of Object.values(grid.value)) {
    for (const v of Object.values(yearData)) {
      if (v > max) max = v
    }
  }
  return max
})

const hasData = computed(() => maxValue.value > 0)

function cellColor(amount) {
  if (amount === 0 || maxValue.value === 0) return 'rgba(55, 65, 81, 0.35)'
  const t = Math.sqrt(amount / maxValue.value) // sqrt scale for better mid-range contrast
  const alpha = 0.15 + t * 0.85
  return `rgba(52, 211, 153, ${alpha.toFixed(3)})`
}

const legendColors = [
  'rgba(55, 65, 81, 0.35)',
  'rgba(52, 211, 153, 0.20)',
  'rgba(52, 211, 153, 0.42)',
  'rgba(52, 211, 153, 0.65)',
  'rgba(52, 211, 153, 0.88)',
  'rgba(52, 211, 153, 1.00)',
]
</script>
