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
      <button
        v-if="tickers.length && !deleteMode"
        @click="deleteMode = true"
        class="text-gray-500 hover:text-red-400 transition-colors"
        title="Delete entries"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="3 6 5 6 21 6"/>
          <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
          <path d="M10 11v6M14 11v6"/>
          <path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>
        </svg>
      </button>
    </div>

    <!-- Delete action bar -->
    <Transition
      enter-active-class="transition-all duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-1"
      leave-active-class="transition-all duration-150 ease-in"
      leave-to-class="opacity-0 -translate-y-1"
    >
      <div v-if="deleteMode" class="flex items-center justify-between px-4 py-2.5 mb-3 bg-red-950/40 border border-red-900/50 rounded-lg">
        <p class="text-sm text-gray-400">
          <span class="font-semibold text-white">{{ selected.size }}</span>
          {{ selected.size === 1 ? 'entry' : 'entries' }} selected
        </p>
        <div class="flex items-center gap-2">
          <button
            @click="cancelDelete"
            class="px-3 py-1.5 text-xs rounded-md text-gray-400 hover:text-gray-200 hover:bg-white/5 transition-colors"
          >
            Cancel
          </button>
          <button
            @click="confirmDelete"
            :disabled="!selected.size"
            class="px-3 py-1.5 text-xs rounded-md bg-red-600 hover:bg-red-500 text-white font-medium disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            Delete{{ selected.size ? ` (${selected.size})` : '' }}
          </button>
        </div>
      </div>
    </Transition>

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
          <th class="text-left py-2 pr-4 w-32">
            <button @click="setSort('ticker')" class="flex items-center gap-1 text-gray-400 font-medium hover:text-gray-200 transition-colors">
              Ticker
              <SortIcon :active="sortKey === 'ticker'" :asc="sortDir === 'asc'" />
            </button>
          </th>
          <th class="text-left py-2 pr-4">
            <button @click="setSort('name')" class="flex items-center gap-1 text-gray-400 font-medium hover:text-gray-200 transition-colors">
              Name
              <SortIcon :active="sortKey === 'name'" :asc="sortDir === 'asc'" />
            </button>
          </th>
          <th
            v-for="m in months"
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
            v-for="m in months"
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
            v-for="m in months"
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
import { ref, computed, defineComponent, h } from 'vue'
import { useDataStore } from '../stores/dataStore.js'
import { useSettingsStore } from '../stores/settingsStore.js'
import { useMonths } from '../composables/useMonths.js'
import EditEntryModal from './EditEntryModal.vue'

const store = useDataStore()
const settings = useSettingsStore()
const { months } = useMonths()

const editingKey = ref(null)
const deleteMode = ref(false)
const selected = ref(new Set())
const sortKey = ref('ticker')
const sortDir = ref('asc')

function setSort(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'asc'
  }
}

const dividends = computed(() => store.yearData.dividends || {})

const tickers = computed(() => {
  return Object.keys(dividends.value).slice().sort((a, b) => {
    const valA = sortKey.value === 'ticker' ? a : (dividends.value[a].name || '').toLowerCase()
    const valB = sortKey.value === 'ticker' ? b : (dividends.value[b].name || '').toLowerCase()
    const cmp = valA < valB ? -1 : valA > valB ? 1 : 0
    return sortDir.value === 'asc' ? cmp : -cmp
  })
})

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
  const keys = [...selected.value]
  cancelDelete()
  await store.deleteEntries('dividends', keys)
}

const SortIcon = defineComponent({
  props: { active: Boolean, asc: Boolean },
  render({ active, asc }) {
    return h('svg', {
      class: ['w-3 h-3 transition-colors', active ? 'text-emerald-400' : 'text-gray-600'],
      viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2.5',
      'stroke-linecap': 'round', 'stroke-linejoin': 'round',
    }, [
      active && !asc
        ? h('path', { d: 'M12 5l-7 7h14l-7-7z M12 5v14' })
        : h('path', { d: 'M12 19l7-7H5l7 7z M12 19V5' }),
    ])
  },
})
</script>
