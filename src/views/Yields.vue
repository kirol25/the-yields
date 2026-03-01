<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold">Yields</h1>
      <div class="flex items-center gap-4">
        <YearSelector />
        <button
          @click="showModal = true"
          class="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-sm font-medium rounded-md transition-colors"
        >
          + Add Entry
        </button>
      </div>
    </div>

    <div class="bg-gray-900 border border-gray-800 rounded-xl p-6">
      <YieldsTable />
    </div>

    <AddEntryModal
      v-if="showModal"
      type="yield"
      :existingKeys="Object.keys(store.yearData.yields || {})"
      @close="showModal = false"
      @saved="showModal = false"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useDataStore } from '../stores/dataStore.js'
import YearSelector from '../components/YearSelector.vue'
import YieldsTable from '../components/YieldsTable.vue'
import AddEntryModal from '../components/AddEntryModal.vue'

const store = useDataStore()
const showModal = ref(false)
</script>
