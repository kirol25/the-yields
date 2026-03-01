<template>
  <div class="overflow-x-auto">
    <table v-if="banks.length" class="w-full text-sm">
      <thead>
        <tr class="border-b border-gray-800">
          <th class="text-left py-2 pr-4 text-gray-400 font-medium w-48">Account</th>
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
          v-for="bank in banks"
          :key="bank"
          class="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors"
        >
          <td class="py-2 pr-4 font-medium text-blue-400">{{ bank }}</td>
          <td
            v-for="m in MONTHS"
            :key="m.value"
            class="py-2 px-2 text-center text-gray-300"
          >
            {{ yields[bank].months?.[m.value] != null ? settings.fmt(yields[bank].months[m.value]) : '–' }}
          </td>
          <td class="py-2 px-2 text-right font-medium text-blue-400">
            {{ settings.fmt(rowTotal(bank)) }}
          </td>
        </tr>
      </tbody>
      <tfoot>
        <tr class="border-t border-gray-700">
          <td class="py-2 pr-4 text-gray-400 font-medium">Monthly Total</td>
          <td
            v-for="m in MONTHS"
            :key="m.value"
            class="py-2 px-2 text-center font-medium text-gray-200"
          >
            {{ settings.fmt(colTotal(m.value)) }}
          </td>
          <td class="py-2 px-2 text-right font-medium text-blue-300">
            {{ settings.fmt(grandTotal) }}
          </td>
        </tr>
      </tfoot>
    </table>
    <div v-else class="text-gray-500 text-sm py-6 text-center">
      No yield accounts recorded for {{ store.currentYear }}.
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

const yields = computed(() => store.yearData.yields || {})
const banks = computed(() => Object.keys(yields.value))

function rowTotal(bank) {
  return Object.values(yields.value[bank]?.months || {}).reduce((a, b) => a + b, 0)
}

function colTotal(monthKey) {
  return Object.values(yields.value).reduce(
    (sum, entry) => sum + (entry.months?.[monthKey] || 0),
    0,
  )
}

const grandTotal = computed(() =>
  Object.values(yields.value)
    .flatMap((e) => Object.values(e.months || {}))
    .reduce((a, b) => a + b, 0),
)
</script>
