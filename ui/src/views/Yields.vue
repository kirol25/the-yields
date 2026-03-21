<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between gap-3 flex-wrap">
      <h1 class="text-2xl font-bold">{{ t('yields.title') }}</h1>
      <div class="flex items-center gap-3">
        <DepotSelector />
        <YearSelector />
        <button
          @click="showModal = true"
          class="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-sm font-medium rounded-md transition-colors whitespace-nowrap"
        >
          {{ t('common.addEntry') }}
        </button>
      </div>
    </div>

    <div class="bg-gray-900 border border-gray-800 rounded-xl p-6">
      <YieldsTable @add="showModal = true" />
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
import { useI18n } from 'vue-i18n'
import { useDataStore } from '../stores/dataStore.js'
import YearSelector from '../components/YearSelector.vue'
import DepotSelector from '../components/DepotSelector.vue'
import YieldsTable from '../components/YieldsTable.vue'
import AddEntryModal from '../components/AddEntryModal.vue'

const { t } = useI18n()
const store = useDataStore()
const showModal = ref(false)
</script>
