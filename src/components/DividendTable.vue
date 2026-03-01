<template>
  <div class="overflow-x-auto">
    <table v-if="tickers.length" class="w-full text-sm">
      <thead>
        <tr class="border-b border-gray-800">
          <th class="text-left py-2 pr-4 text-gray-400 font-medium w-32">Ticker</th>
          <th class="text-left py-2 pr-4 text-gray-400 font-medium">Name</th>
          <th
            v-for="m in MONTHS"
            :key="m.value"
            class="py-2 px-2 text-gray-400 font-medium text-center min-w-[56px]"
          >
            {{ m.label }}
          </th>
          <th class="py-2 px-2 text-gray-400 font-medium text-right">Total</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="ticker in tickers"
          :key="ticker"
          class="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors"
        >
          <td class="py-2 pr-4 font-mono font-medium text-emerald-400">{{ ticker }}</td>
          <td class="py-2 pr-4 text-gray-300">{{ dividends[ticker].name || '' }}</td>
          <td
            v-for="m in MONTHS"
            :key="m.value"
            class="py-2 px-2 text-center text-gray-300"
          >
            {{ dividends[ticker].months?.[m.value] != null ? `$${dividends[ticker].months[m.value].toFixed(2)}` : '–' }}
          </td>
          <td class="py-2 px-2 text-right font-medium text-emerald-400">
            ${{ rowTotal(ticker) }}
          </td>
        </tr>
      </tbody>
      <tfoot>
        <tr class="border-t border-gray-700">
          <td colspan="2" class="py-2 pr-4 text-gray-400 font-medium">Monthly Total</td>
          <td
            v-for="m in MONTHS"
            :key="m.value"
            class="py-2 px-2 text-center font-medium text-gray-200"
          >
            ${{ colTotal(m.value) }}
          </td>
          <td class="py-2 px-2 text-right font-medium text-emerald-300">
            ${{ grandTotal }}
          </td>
        </tr>
      </tfoot>
    </table>
    <div v-else class="text-gray-500 text-sm py-6 text-center">
      No dividends recorded for {{ store.currentYear }}.
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useDataStore } from '../stores/dataStore.js'

const store = useDataStore()

const MONTHS = [
  { value: '01', label: 'Jan' },
  { value: '02', label: 'Feb' },
  { value: '03', label: 'Mar' },
  { value: '04', label: 'Apr' },
  { value: '05', label: 'May' },
  { value: '06', label: 'Jun' },
  { value: '07', label: 'Jul' },
  { value: '08', label: 'Aug' },
  { value: '09', label: 'Sep' },
  { value: '10', label: 'Oct' },
  { value: '11', label: 'Nov' },
  { value: '12', label: 'Dec' },
]

const dividends = computed(() => store.yearData.dividends || {})
const tickers = computed(() => Object.keys(dividends.value))

function rowTotal(ticker) {
  return Object.values(dividends.value[ticker]?.months || {})
    .reduce((a, b) => a + b, 0)
    .toFixed(2)
}

function colTotal(monthKey) {
  return Object.values(dividends.value)
    .reduce((sum, entry) => sum + (entry.months?.[monthKey] || 0), 0)
    .toFixed(2)
}

const grandTotal = computed(() =>
  Object.values(dividends.value)
    .flatMap((e) => Object.values(e.months || {}))
    .reduce((a, b) => a + b, 0)
    .toFixed(2),
)
</script>
