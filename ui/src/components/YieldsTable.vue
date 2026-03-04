<template>
  <EditEntryModal
    v-if="editingKey"
    type="yield"
    :entry-key="editingKey"
    @close="editingKey = null"
  />

  <div class="overflow-x-auto">
    <!-- Toolbar -->
    <div class="flex justify-end mb-3 min-h-[28px]">
      <button
        v-if="banks.length && !deleteMode"
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

    <!-- Skeleton rows while loading -->
    <div v-if="store.loading" class="space-y-2 py-2">
      <div v-for="i in 4" :key="i" class="flex gap-3 items-center">
        <SkeletonBlock cls="h-4 w-32 shrink-0" />
        <SkeletonBlock cls="h-4 flex-1" />
      </div>
    </div>

    <table v-else-if="banks.length" class="w-full text-sm">
      <thead>
        <tr class="border-b border-gray-800">
          <th v-if="deleteMode" class="w-8 py-2 pr-2">
            <input
              type="checkbox"
              :checked="selected.size === banks.length"
              @change="toggleAll"
              class="accent-red-500 cursor-pointer"
            />
          </th>
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
          class="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors cursor-pointer"
          :class="{ 'opacity-50': deleteMode && selected.has(bank) }"
          @click="deleteMode ? toggleSelect(bank) : (editingKey = bank)"
        >
          <td v-if="deleteMode" class="w-8 py-2 pr-2" @click.stop="toggleSelect(bank)">
            <input
              type="checkbox"
              :checked="selected.has(bank)"
              class="accent-red-500 cursor-pointer"
              readonly
            />
          </td>
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
          <td v-if="deleteMode" />
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
    <div v-else-if="!store.loading" class="text-gray-500 text-sm py-6 text-center">
      No yield accounts recorded for {{ store.currentYear }}.
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useDataStore } from '../stores/dataStore.js'
import { useSettingsStore } from '../stores/settingsStore.js'
import { MONTHS } from '../config.js'
import EditEntryModal from './EditEntryModal.vue'
import SkeletonBlock from './SkeletonBlock.vue'

const store = useDataStore()
const settings = useSettingsStore()

const editingKey = ref(null)
const deleteMode = ref(false)
const selected = ref(new Set())

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

function toggleSelect(bank) {
  const s = new Set(selected.value)
  s.has(bank) ? s.delete(bank) : s.add(bank)
  selected.value = s
}

function toggleAll(e) {
  selected.value = e.target.checked ? new Set(banks.value) : new Set()
}

function cancelDelete() {
  deleteMode.value = false
  selected.value = new Set()
}

async function confirmDelete() {
  const keys = [...selected.value]
  cancelDelete()
  await store.deleteEntries('yields', keys)
}
</script>
