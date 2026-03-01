<template>
  <EditEntryModal
    v-if="editingKey"
    type="dividend"
    :entry-key="editingKey"
    @close="editingKey = null"
  />

  <div class="overflow-x-auto">
    <!-- Toolbar -->
    <div class="flex justify-end mb-3 min-h-[28px]">
      <template v-if="!deleteMode">
        <button
          v-if="tickers.length"
          @click="deleteMode = true"
          class="text-xs text-red-400 hover:text-red-300 transition-colors"
        >
          Delete entries
        </button>
      </template>
      <template v-else>
        <div class="flex items-center gap-3">
          <span class="text-xs text-gray-500">{{ selected.size }} selected</span>
          <button
            @click="cancelDelete"
            class="text-xs text-gray-400 hover:text-gray-300 transition-colors"
          >
            Cancel
          </button>
          <button
            @click="confirmDelete"
            :disabled="!selected.size"
            class="text-xs text-red-400 hover:text-red-300 disabled:opacity-40 disabled:cursor-not-allowed transition-colors font-medium"
          >
            Delete ({{ selected.size }})
          </button>
        </div>
      </template>
    </div>

    <table v-if="tickers.length" class="w-full text-sm">
      <thead>
        <tr class="border-b border-gray-800">
          <th v-if="deleteMode" class="w-8 py-2 pr-2">
            <input
              type="checkbox"
              :checked="selected.size === tickers.length"
              @change="toggleAll"
              class="accent-red-500 cursor-pointer"
            />
          </th>
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
          class="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors cursor-pointer"
          :class="{ 'opacity-50': deleteMode && selected.has(ticker) }"
          @click="deleteMode ? toggleSelect(ticker) : (editingKey = ticker)"
        >
          <td v-if="deleteMode" class="w-8 py-2 pr-2" @click.stop="toggleSelect(ticker)">
            <input
              type="checkbox"
              :checked="selected.has(ticker)"
              class="accent-red-500 cursor-pointer"
              readonly
            />
          </td>
          <td class="py-2 pr-4">
            <span class="font-mono font-medium text-emerald-400">{{ ticker }}</span>
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
          <td v-if="deleteMode" />
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
import { ref, computed } from 'vue'
import { useDataStore } from '../stores/dataStore.js'
import { useSettingsStore } from '../stores/settingsStore.js'
import { MONTHS } from '../config.js'
import EditEntryModal from './EditEntryModal.vue'

const store = useDataStore()
const settings = useSettingsStore()

const editingKey = ref(null)
const deleteMode = ref(false)
const selected = ref(new Set())

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

function toggleSelect(ticker) {
  const s = new Set(selected.value)
  s.has(ticker) ? s.delete(ticker) : s.add(ticker)
  selected.value = s
}

function toggleAll(e) {
  selected.value = e.target.checked ? new Set(tickers.value) : new Set()
}

function cancelDelete() {
  deleteMode.value = false
  selected.value = new Set()
}

async function confirmDelete() {
  for (const key of selected.value) {
    delete store.yearData.dividends[key]
  }
  cancelDelete()
  await store.saveData()
}
</script>
