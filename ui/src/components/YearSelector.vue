<template>
  <div ref="container" class="relative flex items-center gap-1 bg-gray-900 border border-gray-800 rounded-lg px-1 py-1">
    <button
      @click="step(-1)"
      :disabled="currentIndex <= 0 || store.loading"
      class="p-1 rounded text-gray-500 hover:text-gray-200 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="15 18 9 12 15 6"/>
      </svg>
    </button>

    <button
      @click="toggleOpen"
      :disabled="store.loading"
      class="relative text-sm font-medium text-gray-100 w-12 text-center tabular-nums hover:text-emerald-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
    >
      <span :class="{ 'opacity-0': store.loading && !store.initializing }">{{ store.currentYear }}</span>
      <svg
        v-if="store.loading && !store.initializing"
        class="absolute inset-0 m-auto w-3.5 h-3.5 animate-spin text-emerald-400"
        viewBox="0 0 24 24" fill="none"
      >
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"/>
      </svg>
    </button>

    <button
      @click="step(1)"
      :disabled="currentIndex >= store.years.length - 1 || store.loading"
      class="p-1 rounded text-gray-500 hover:text-gray-200 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="9 18 15 12 9 6"/>
      </svg>
    </button>

    <!-- Dropdown -->
    <Teleport to="body">
      <div v-if="open" class="fixed inset-0 z-40" @click="open = false" />
      <div
        v-if="open"
        :style="dropdownStyle"
        class="fixed z-50 bg-gray-900 border border-gray-700 rounded-lg shadow-xl py-1 min-w-[80px]"
      >
        <button
          v-for="year in store.years"
          :key="year"
          @click="select(year)"
          :class="[
            'w-full px-4 py-1.5 text-sm text-center tabular-nums transition-colors flex items-center justify-center gap-1.5',
            year === store.currentYear
              ? 'text-emerald-400 font-medium bg-emerald-500/10'
              : 'text-gray-300 hover:bg-gray-800',
          ]"
        >
          {{ year }}
        </button>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useDataStore } from '../stores/dataStore.js'

const store = useDataStore()
const open = ref(false)
const container = ref(null)
const dropdownStyle = ref({})

const currentIndex = computed(() => store.years.indexOf(store.currentYear))

function toggleOpen() {
  if (!open.value) {
    const rect = container.value.getBoundingClientRect()
    dropdownStyle.value = {
      top: `${rect.bottom + 4}px`,
      left: `${rect.left}px`,
    }
  }
  open.value = !open.value
}

async function step(dir) {
  const next = store.years[currentIndex.value + dir]
  if (next !== undefined) await store.loadYear(next)
}

async function select(year) {
  open.value = false
  await store.loadYear(year)
}
</script>
