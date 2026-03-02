<template>
  <Teleport to="body">
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/60" @click.self="$emit('close')">
    <div class="bg-gray-900 border border-gray-700 rounded-xl p-6 w-full max-w-lg shadow-2xl">

      <!-- Header -->
      <div class="mb-5">
        <div class="font-mono font-semibold text-lg" :class="props.type === 'dividend' ? 'text-emerald-400' : 'text-blue-400'">
          {{ props.entryKey }}
        </div>
        <div v-if="props.type === 'dividend'" class="mt-1">
          <input
            v-model="entryName"
            type="text"
            :placeholder="t('modal.companyNamePlaceholder')"
            class="bg-transparent text-sm text-gray-200 placeholder-gray-600 focus:outline-none border-b border-gray-700 focus:border-gray-400 transition-colors w-48"
          />
        </div>
      </div>

      <!-- Month grid -->
      <div class="grid grid-cols-4 gap-2">
        <div v-for="m in months" :key="m.value">
          <label class="block text-xs text-gray-500 mb-1 text-center">{{ m.short }}</label>
          <input
            v-model.number="monthValues[m.value]"
            type="number"
            min="0"
            step="0.01"
            placeholder="–"
            class="w-full bg-gray-800 border border-gray-700 rounded px-2 py-1.5 text-sm text-center text-gray-100 focus:outline-none focus:ring-1 focus:ring-emerald-500 placeholder-gray-600"
          />
        </div>
      </div>

      <!-- Footer -->
      <div class="flex gap-3 mt-6 justify-end">
        <button
          @click="$emit('close')"
          class="px-4 py-2 text-sm rounded-md bg-gray-800 hover:bg-gray-700 transition-colors"
        >
          {{ t('common.cancel') }}
        </button>
        <button
          @click="save"
          class="px-4 py-2 text-sm rounded-md bg-emerald-600 hover:bg-emerald-500 transition-colors font-medium"
        >
          {{ t('common.save') }}
        </button>
      </div>
    </div>
  </div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDataStore } from '../stores/dataStore.js'
import { useMonths } from '../composables/useMonths.js'

const { t } = useI18n()
const { months } = useMonths()

const props = defineProps({
  type: { type: String, required: true }, // 'dividend' | 'yield'
  entryKey: { type: String, required: true },
})
const emit = defineEmits(['close'])

const store = useDataStore()
const section = props.type === 'dividend' ? 'dividends' : 'yields'
const entry = store.yearData[section][props.entryKey]

const entryName = ref(entry?.name ?? '')
const monthValues = ref(
  Object.fromEntries(['01','02','03','04','05','06','07','08','09','10','11','12'].map((v) => [v, entry?.months?.[v] ?? null]))
)

function save() {
  const months = {}
  for (const [k, v] of Object.entries(monthValues.value)) {
    if (v != null && v !== '') months[k] = v
  }
  store.yearData[section][props.entryKey].months = months
  if (props.type === 'dividend') {
    store.yearData[section][props.entryKey].name = entryName.value.trim() || props.entryKey
  }
  emit('close')
  store.saveData()
}
</script>
