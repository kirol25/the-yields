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
            {{ m.short }}
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
          <td class="py-2 pr-4">
            <a
              :href="`https://finance.yahoo.com/quote/${ticker}/`"
              target="_blank"
              rel="noopener noreferrer"
              class="font-mono font-medium text-emerald-400 hover:text-emerald-300 hover:underline transition-colors"
            >
              {{ ticker }}
            </a>
          </td>
          <td class="py-2 pr-4 text-gray-300">{{ dividends[ticker].name || '' }}</td>
          <td
            v-for="m in MONTHS"
            :key="m.value"
            class="py-2 px-2 text-center text-gray-300"
          >
            {{ dividends[ticker].months?.[m.value] != null ? settings.fmt(dividends[ticker].months[m.value]) : '–' }}
          </td>
          <td class="py-2 px-2 text-right font-medium text-emerald-400">
            {{ settings.fmt(rowTotal(ticker)) }}
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
            {{ settings.fmt(colTotal(m.value)) }}
          </td>
          <td class="py-2 px-2 text-right font-medium text-emerald-300">
            {{ settings.fmt(grandTotal) }}
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
import { useSettingsStore } from '../stores/settingsStore.js'
import { MONTHS } from '../config.js'

const store = useDataStore()
const settings = useSettingsStore()

const dividends = computed(() => store.yearData.dividends || {})
const tickers = computed(() => Object.keys(dividends.value))

function rowTotal(ticker) {
  return Object.values(dividends.value[ticker]?.months || {}).reduce((a, b) => a + b, 0)
}

function colTotal(monthKey) {
  return Object.values(dividends.value).reduce(
    (sum, entry) => sum + (entry.months?.[monthKey] || 0),
    0,
  )
}

const grandTotal = computed(() =>
  Object.values(dividends.value)
    .flatMap((e) => Object.values(e.months || {}))
    .reduce((a, b) => a + b, 0),
)
</script>
