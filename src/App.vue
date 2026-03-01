<template>
  <div class="min-h-screen bg-gray-950 text-gray-100">
    <nav class="bg-gray-900 border-b border-gray-800 px-6 py-4">
      <div class="max-w-7xl mx-auto flex items-center justify-between">
        <span class="text-xl font-bold text-emerald-400 tracking-tight">the-yield</span>
        <div class="flex gap-6">
          <RouterLink
            to="/"
            class="text-sm font-medium transition-colors hover:text-emerald-400"
            :class="$route.path === '/' ? 'text-emerald-400' : 'text-gray-400'"
          >
            Dashboard
          </RouterLink>
          <RouterLink
            to="/dividends"
            class="text-sm font-medium transition-colors hover:text-emerald-400"
            :class="$route.path === '/dividends' ? 'text-emerald-400' : 'text-gray-400'"
          >
            Dividends
          </RouterLink>
          <RouterLink
            to="/yields"
            class="text-sm font-medium transition-colors hover:text-emerald-400"
            :class="$route.path === '/yields' ? 'text-emerald-400' : 'text-gray-400'"
          >
            Yields
          </RouterLink>
        </div>
      </div>
    </nav>
    <main class="max-w-7xl mx-auto px-6 py-8">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useDataStore } from './stores/dataStore.js'

const store = useDataStore()

onMounted(async () => {
  await store.fetchYears()
  await store.loadYear(store.currentYear)
})
</script>
