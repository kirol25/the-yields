<template>
  <div v-if="depotStore.depots.length > 1" ref="container" class="relative flex items-center gap-1 bg-gray-900 border border-gray-800 rounded-lg px-1 py-1">
    <button
      @click="toggleOpen"
      class="flex items-center gap-1.5 px-2 text-sm font-medium text-gray-100 hover:text-emerald-400 transition-colors max-w-[140px]"
    >
      <!-- layers / stacked-accounts icon -->
      <svg class="w-3.5 h-3.5 text-gray-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 2L2 7l10 5 10-5-10-5z"/>
        <path d="M2 12l10 5 10-5"/>
        <path d="M2 17l10 5 10-5"/>
      </svg>
      <span class="truncate">{{ depotStore.currentDepot?.name || '…' }}</span>
      <svg class="w-3 h-3 text-gray-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
        <polyline points="6 9 12 15 18 9"/>
      </svg>
    </button>

    <Teleport to="body">
      <div v-if="open" class="fixed inset-0 z-40" @click="open = false" />
      <div
        v-if="open"
        :style="dropdownStyle"
        class="fixed z-50 bg-gray-900 border border-gray-700 rounded-lg shadow-xl py-1 min-w-[160px]"
      >
        <button
          v-for="depot in depotStore.depots"
          :key="depot.id"
          @click="select(depot.id)"
          :class="[
            'w-full px-4 py-1.5 text-sm text-left transition-colors',
            depot.id === depotStore.currentDepotId
              ? 'text-emerald-400 font-medium bg-emerald-500/10'
              : 'text-gray-300 hover:bg-gray-800',
          ]"
        >
          {{ depot.name }}
        </button>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useDepotStore } from '../stores/depotStore.js'
import { useDataStore } from '../stores/dataStore.js'

const depotStore = useDepotStore()
const dataStore = useDataStore()
const open = ref(false)
const container = ref(null)
const dropdownStyle = ref({})

function toggleOpen() {
  if (!open.value) {
    const rect = container.value?.getBoundingClientRect()
    if (rect) {
      dropdownStyle.value = {
        top: `${rect.bottom + 4}px`,
        left: `${rect.left}px`,
        minWidth: `${rect.width}px`,
      }
    }
  }
  open.value = !open.value
}

async function select(id) {
  if (id === depotStore.currentDepotId) {
    open.value = false
    return
  }
  depotStore.selectDepot(id)
  open.value = false
  // Reload data for the newly selected depot
  await dataStore.fetchYears()
  await Promise.all([dataStore.loadYear(dataStore.currentYear), dataStore.loadAllYears()])
}
</script>
