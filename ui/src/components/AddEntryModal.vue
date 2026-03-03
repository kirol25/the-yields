<template>
  <Teleport to="body">
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/60" @click.self="$emit('close')">
    <div class="bg-gray-900 border border-gray-700 rounded-xl p-6 w-full max-w-md shadow-2xl">
      <h2 class="text-lg font-semibold mb-4">
        {{ props.type === 'dividend' ? t('modal.addDividend') : t('modal.addYield') }}
      </h2>

      <div class="space-y-4">
        <!-- Ticker / Bank selector -->
        <div>
          <label class="block text-sm text-gray-400 mb-1">
            {{ props.type === 'dividend' ? t('modal.ticker') : t('modal.bankAccount') }}
          </label>
          <select
            v-model="selectedKey"
            class="w-full bg-gray-800 border border-gray-700 rounded-md px-3 py-2 text-sm text-gray-100 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          >
            <option v-for="key in props.existingKeys" :key="key" :value="key">{{ key }}</option>
            <option value="__new__">{{ t('modal.addNew') }}</option>
          </select>
        </div>

        <!-- New name input -->
        <div v-if="selectedKey === '__new__'">
          <label class="block text-sm text-gray-400 mb-1">
            {{ props.type === 'dividend' ? t('modal.tickerSymbol') : t('modal.name') }}
          </label>
          <input
            v-model="newKey"
            type="text"
            :placeholder="props.type === 'dividend' ? 'e.g. AAPL' : 'e.g. Chase HYSA'"
            class="w-full bg-gray-800 border border-gray-700 rounded-md px-3 py-2 text-sm text-gray-100 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          />
          <!-- Name field for dividends -->
          <div v-if="props.type === 'dividend'" class="mt-2">
            <label class="block text-sm text-gray-400 mb-1">{{ t('modal.companyNameOptional') }}</label>
            <input
              v-model="newName"
              type="text"
              :placeholder="t('modal.companyNamePlaceholder')"
              class="w-full bg-gray-800 border border-gray-700 rounded-md px-3 py-2 text-sm text-gray-100 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>
        </div>

        <!-- Month selector -->
        <div>
          <label class="block text-sm text-gray-400 mb-1">{{ t('modal.month') }}</label>
          <select
            v-model="selectedMonth"
            class="w-full bg-gray-800 border border-gray-700 rounded-md px-3 py-2 text-sm text-gray-100 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          >
            <option v-for="m in months" :key="m.value" :value="m.value">{{ m.label }}</option>
          </select>
        </div>

        <!-- Amount -->
        <div>
          <label class="block text-sm text-gray-400 mb-1">{{ t('modal.amount') }}</label>
          <input
            v-model.number="amount"
            type="number"
            min="0"
            step="0.01"
            placeholder="0.00"
            class="w-full bg-gray-800 border border-gray-700 rounded-md px-3 py-2 text-sm text-gray-100 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          />
        </div>
      </div>

      <div class="flex gap-3 mt-6 justify-end">
        <button
          @click="$emit('close')"
          class="px-4 py-2 text-sm rounded-md bg-gray-800 hover:bg-gray-700 transition-colors"
        >
          {{ t('common.cancel') }}
        </button>
        <button
          @click="submit"
          :disabled="!canSubmit"
          class="px-4 py-2 text-sm rounded-md bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
        >
          {{ t('common.save') }}
        </button>
      </div>
    </div>
  </div>
  </Teleport>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDataStore } from '../stores/dataStore.js'
import { useMonths } from '../composables/useMonths.js'

const { t } = useI18n()
const { months } = useMonths()

const props = defineProps({
  type: { type: String, required: true }, // 'dividend' | 'yield'
  existingKeys: { type: Array, default: () => [] },
})
const emit = defineEmits(['close', 'saved'])

const store = useDataStore()

const selectedKey = ref(props.existingKeys[0] ?? '__new__')
const newKey = ref('')
const newName = ref('')
const selectedMonth = ref(String(new Date().getMonth() + 1).padStart(2, '0'))
const amount = ref(null)

const resolvedKey = computed(() =>
  selectedKey.value === '__new__' ? newKey.value.trim() : selectedKey.value,
)

const canSubmit = computed(() => resolvedKey.value && amount.value != null && amount.value >= 0)

async function submit() {
  if (!canSubmit.value) return

  const key = resolvedKey.value
  const section = props.type === 'dividend' ? 'dividends' : 'yields'

  if (!store.yearData[section][key]) {
    if (props.type === 'dividend') {
      store.yearData[section][key] = { name: newName.value.trim() || key, months: {} }
    } else {
      store.yearData[section][key] = { months: {} }
    }
  }

  store.yearData[section][key].months[selectedMonth.value] = amount.value

  await store.saveData()
  emit('saved')
  emit('close')
}
</script>
