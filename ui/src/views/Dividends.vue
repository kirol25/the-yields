<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold">{{ t('dividends.title') }}</h1>
      <div class="flex items-center gap-4">
        <YearSelector />
        <button
          @click="showModal = true"
          class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-sm font-medium rounded-md transition-colors"
        >
          {{ t('common.addEntry') }}
        </button>
      </div>
    </div>

    <div class="bg-gray-900 border border-gray-800 rounded-xl p-6">
      <DividendTable />
    </div>

    <AddEntryModal
      v-if="showModal"
      type="dividend"
      :existingKeys="Object.keys(store.yearData.dividends || {})"
      @close="showModal = false"
      @saved="showModal = false"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDataStore } from '../stores/dataStore.js'
import YearSelector from '../components/YearSelector.vue'
import DividendTable from '../components/DividendTable.vue'
import AddEntryModal from '../components/AddEntryModal.vue'

const { t } = useI18n()
const store = useDataStore()
const showModal = ref(false)
</script>
