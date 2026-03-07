<template>
  <div ref="container" class="relative flex items-center gap-1 bg-gray-900 border border-gray-800 rounded-lg px-1 py-1">
    <button
      @click="step(-1)"
      :disabled="currentIndex <= 0 || store.loading || isLocked(store.years[currentIndex - 1])"
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
      :disabled="currentIndex >= store.years.length - 1 || store.loading || isLocked(store.years[currentIndex + 1])"
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
          :disabled="isLocked(year)"
          :class="[
            'w-full px-4 py-1.5 text-sm text-center tabular-nums transition-colors flex items-center justify-center gap-1.5',
            isLocked(year)
              ? 'text-gray-600 cursor-not-allowed'
              : year === store.currentYear
                ? 'text-emerald-400 font-medium bg-emerald-500/10'
                : 'text-gray-300 hover:bg-gray-800',
          ]"
        >
          {{ year }}
          <svg v-if="isLocked(year)" class="w-3 h-3 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path stroke-linecap="round" stroke-linejoin="round" d="M7 11V7a5 5 0 0 1 10 0v4"/>
          </svg>
        </button>
        <template v-if="!isPremium && store.years.some(y => y !== THIS_YEAR)">
          <div class="border-t border-gray-800 my-1" />
          <RouterLink
            to="/subscriptions"
            @click="open = false"
            class="w-full px-4 py-1.5 text-xs text-emerald-400 hover:text-emerald-300 text-center block transition-colors"
          >
            Upgrade for all years →
          </RouterLink>
        </template>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useDataStore } from '../stores/dataStore.js'
import { useSubscription } from '../composables/useSubscription.js'

const THIS_YEAR = new Date().getFullYear()

const store = useDataStore()
const { isPremium } = useSubscription()
const open = ref(false)
const container = ref(null)
const dropdownStyle = ref({})

const currentIndex = computed(() => store.years.indexOf(store.currentYear))

function isLocked(year) {
  return !isPremium.value && year !== THIS_YEAR
}

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
  if (next !== undefined && !isLocked(next)) await store.loadYear(next)
}

async function select(year) {
  if (isLocked(year)) return
  open.value = false
  await store.loadYear(year)
}
</script>
