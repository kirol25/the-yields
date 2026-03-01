<template>
  <div class="flex items-center gap-2">
    <label class="text-sm text-gray-400">Year</label>
    <select
      :value="store.currentYear"
      @change="onChange"
      class="bg-gray-800 border border-gray-700 text-gray-100 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
    >
      <option v-for="year in store.years" :key="year" :value="year">{{ year }}</option>
    </select>
  </div>
</template>

<script setup>
import { useDataStore } from '../stores/dataStore.js'

const store = useDataStore()

async function onChange(e) {
  await store.loadYear(Number(e.target.value))
}
</script>
