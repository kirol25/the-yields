<template>
  <Teleport to="body">
    <div
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      @click.self="$emit('close')"
    >
      <div class="bg-gray-900 border border-gray-800 rounded-2xl p-6 w-full max-w-md shadow-2xl">

        <!-- Header -->
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-base font-semibold text-gray-100">
            {{ props.type === 'dividend' ? t('modal.addDividend') : t('modal.addYield') }}
          </h2>
          <button
            @click="$emit('close')"
            class="text-gray-500 hover:text-gray-300 transition-colors rounded-md p-1 hover:bg-gray-800"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <div class="space-y-5">

          <!-- Year picker -->
          <div>
            <label class="block text-xs font-medium text-gray-400 mb-1.5">{{ t('modal.year') }}</label>
            <div class="relative">
              <select
                v-model.number="selectedYear"
                class="w-full appearance-none bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-sm text-gray-100 hover:border-gray-600 focus:outline-none focus:ring-2 focus:ring-emerald-500 transition-colors"
              >
                <option v-for="y in availableYears" :key="y" :value="y">{{ y }}</option>
              </select>
              <svg class="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <polyline points="6 9 12 15 18 9"/>
              </svg>
            </div>
          </div>

          <!-- Dividends: searchable ticker dropdown from /api/tickers -->
          <div v-if="props.type === 'dividend'">
            <label class="block text-xs font-medium text-gray-400 mb-1.5">{{ t('modal.ticker') }}</label>
            <div class="relative">
              <button
                type="button"
                @click="keyOpen = !keyOpen"
                class="w-full flex items-center justify-between bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-sm text-gray-100 hover:border-gray-600 focus:outline-none focus:ring-2 focus:ring-emerald-500 transition-colors"
              >
                <span v-if="selectedKey">
                  <span class="font-medium">{{ selectedKey }}</span>
                  <span v-if="tickerName(selectedKey)" class="text-gray-400 ml-1.5">{{ tickerName(selectedKey) }}</span>
                </span>
                <span v-else class="text-gray-500">{{ t('modal.selectTicker') }}</span>
                <svg class="w-3.5 h-3.5 text-gray-500 transition-transform duration-150" :class="keyOpen ? 'rotate-180' : ''" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                  <polyline points="6 9 12 15 18 9"/>
                </svg>
              </button>

              <div
                v-if="keyOpen"
                class="absolute z-10 mt-1 w-full bg-gray-900 border border-gray-700 rounded-lg shadow-xl"
              >
                <!-- Search input -->
                <div class="p-2 border-b border-gray-800">
                  <input
                    v-model="tickerSearch"
                    type="text"
                    :placeholder="t('modal.searchTicker')"
                    class="w-full bg-gray-800 border border-gray-700 rounded-md px-3 py-1.5 text-sm text-gray-100 placeholder-gray-600 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                    @click.stop
                  />
                </div>
                <div class="max-h-48 overflow-y-auto py-1">
                  <!-- Existing (already tracked this year) -->
                  <template v-if="filteredExisting.length">
                    <div class="px-3 py-1 text-xs text-gray-600 uppercase tracking-wide">{{ t('modal.alreadyTracked') }}</div>
                    <button
                      v-for="t_ in filteredExisting"
                      :key="t_.symbol"
                      type="button"
                      @click="selectedKey = t_.symbol; keyOpen = false; tickerSearch = ''"
                      :class="[
                        'w-full px-3 py-2 text-sm text-left transition-colors flex items-center justify-between',
                        selectedKey === t_.symbol ? 'text-emerald-400 bg-emerald-500/10' : 'text-gray-300 hover:bg-gray-800',
                      ]"
                    >
                      <span class="font-medium">{{ t_.symbol }}</span>
                      <span class="text-gray-500 text-xs truncate ml-2">{{ t_.name }}</span>
                    </button>
                    <div v-if="filteredNew.length" class="border-t border-gray-800 my-1" />
                  </template>
                  <!-- All other tickers -->
                  <button
                    v-for="t_ in filteredNew"
                    :key="t_.symbol"
                    type="button"
                    @click="selectedKey = t_.symbol; keyOpen = false; tickerSearch = ''"
                    :class="[
                      'w-full px-3 py-2 text-sm text-left transition-colors flex items-center justify-between',
                      selectedKey === t_.symbol ? 'text-emerald-400 bg-emerald-500/10' : 'text-gray-300 hover:bg-gray-800',
                    ]"
                  >
                    <span class="font-medium">{{ t_.symbol }}</span>
                    <span class="text-gray-500 text-xs truncate ml-2">{{ t_.name }}</span>
                  </button>
                  <div v-if="!filteredExisting.length && !filteredNew.length" class="px-3 py-4 text-sm text-gray-600 text-center">
                    {{ t('modal.noTickersFound') }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Yields: existing dropdown + "Add New" free-text -->
          <div v-else>
            <label class="block text-xs font-medium text-gray-400 mb-1.5">{{ t('modal.bankAccount') }}</label>
            <div class="relative">
              <button
                type="button"
                @click="keyOpen = !keyOpen"
                class="w-full flex items-center justify-between bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-sm text-gray-100 hover:border-gray-600 focus:outline-none focus:ring-2 focus:ring-emerald-500 transition-colors"
              >
                <span :class="selectedKey === '__new__' ? 'text-emerald-400' : ''">
                  {{ selectedKey === '__new__' ? t('modal.addNew') : selectedKey }}
                </span>
                <svg class="w-3.5 h-3.5 text-gray-500 transition-transform duration-150" :class="keyOpen ? 'rotate-180' : ''" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                  <polyline points="6 9 12 15 18 9"/>
                </svg>
              </button>

              <div
                v-if="keyOpen"
                class="absolute z-10 mt-1 w-full bg-gray-900 border border-gray-700 rounded-lg shadow-xl py-1 max-h-48 overflow-y-auto"
              >
                <button
                  v-for="key in resolvedExistingKeys"
                  :key="key"
                  type="button"
                  @click="selectedKey = key; keyOpen = false"
                  :class="[
                    'w-full px-3 py-2 text-sm text-left transition-colors',
                    selectedKey === key ? 'text-emerald-400 bg-emerald-500/10' : 'text-gray-300 hover:bg-gray-800',
                  ]"
                >
                  {{ key }}
                </button>
                <div v-if="resolvedExistingKeys.length" class="border-t border-gray-800 my-1" />
                <button
                  type="button"
                  @click="selectedKey = '__new__'; keyOpen = false"
                  :class="[
                    'w-full px-3 py-2 text-sm text-left transition-colors',
                    selectedKey === '__new__' ? 'text-emerald-400 bg-emerald-500/10' : 'text-emerald-500 hover:bg-gray-800',
                  ]"
                >
                  {{ t('modal.addNew') }}
                </button>
              </div>
            </div>
          </div>

          <!-- New yield account name input -->
          <div v-if="props.type === 'yield' && selectedKey === '__new__'">
            <label class="block text-xs font-medium text-gray-400 mb-1.5">{{ t('modal.name') }}</label>
            <input
              v-model="newKey"
              type="text"
              placeholder="e.g. Chase HYSA"
              class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-sm text-gray-100 placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-emerald-500 hover:border-gray-600 transition-colors"
            />
          </div>

          <!-- Month - chip grid -->
          <div>
            <label class="block text-xs font-medium text-gray-400 mb-2">{{ t('modal.month') }}</label>
            <div class="grid grid-cols-4 gap-1.5">
              <button
                v-for="m in months"
                :key="m.value"
                type="button"
                @click="selectedMonth = m.value"
                :class="[
                  'py-2 rounded-lg text-xs font-medium transition-colors',
                  selectedMonth === m.value
                    ? 'bg-emerald-600 text-white'
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-gray-200',
                ]"
              >
                {{ m.short }}
              </button>
            </div>
          </div>

          <!-- Amount -->
          <div>
            <label class="block text-xs font-medium text-gray-400 mb-1.5">{{ t('modal.amount') }}</label>
            <input
              v-model.number="amount"
              type="number"
              min="0"
              step="0.01"
              placeholder="0.00"
              class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-sm text-gray-100 placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-emerald-500 hover:border-gray-600 transition-colors"
            />
          </div>

        </div>

        <!-- Footer -->
        <div class="flex gap-2 mt-6 justify-end">
          <button
            @click="$emit('close')"
            class="px-4 py-2 text-sm rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 transition-colors"
          >
            {{ t('common.cancel') }}
          </button>
          <button
            @click="submit"
            :disabled="!canSubmit"
            class="px-4 py-2 text-sm rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 disabled:cursor-not-allowed text-white font-medium transition-colors"
          >
            {{ t('common.save') }}
          </button>
        </div>

      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDataStore } from '../stores/dataStore.js'
import { useMonths } from '../composables/useMonths.js'
import client from '../api/client.js'

const { t } = useI18n()
const { months } = useMonths()

const props = defineProps({
  type: { type: String, required: true }, // 'dividend' | 'yield'
  existingKeys: { type: Array, default: () => [] },
})
const emit = defineEmits(['close', 'saved'])

const store = useDataStore()

const THIS_YEAR = new Date().getFullYear()
const selectedYear = ref(store.currentYear)
const availableYears = computed(() => {
  const years = []
  for (let y = THIS_YEAR; y >= 2000; y--) years.push(y)
  return years
})

// Keys already tracked for the selected year (falls back to prop for current year)
const resolvedExistingKeys = computed(() => {
  if (selectedYear.value === store.currentYear) return props.existingKeys
  const data = store.allYearsData[selectedYear.value]
  if (!data) return []
  return Object.keys(data[props.type === 'dividend' ? 'dividends' : 'yields'] || {})
})


// Tickers reference list (dividends only)
const allTickers = ref([])
onMounted(async () => {
  if (props.type === 'dividend') {
    const { data } = await client.get('/api/tickers')
    allTickers.value = data
  }
})

const tickerSearch = ref('')

const filteredExisting = computed(() => {
  const q = tickerSearch.value.trim().toLowerCase()
  return allTickers.value.filter(
    (t_) =>
      resolvedExistingKeys.value.includes(t_.symbol) &&
      (!q || t_.symbol.toLowerCase().includes(q) || t_.name.toLowerCase().includes(q)),
  )
})

const filteredNew = computed(() => {
  const q = tickerSearch.value.trim().toLowerCase()
  return allTickers.value.filter(
    (t_) =>
      !resolvedExistingKeys.value.includes(t_.symbol) &&
      (!q || t_.symbol.toLowerCase().includes(q) || t_.name.toLowerCase().includes(q)),
  )
})

function tickerName(symbol) {
  return allTickers.value.find((t_) => t_.symbol === symbol)?.name ?? ''
}

// Initial selection
const selectedKey = ref(
  props.type === 'dividend'
    ? (resolvedExistingKeys.value[0] ?? '')
    : (resolvedExistingKeys.value[0] ?? '__new__'),
)
const keyOpen = ref(false)
const newKey = ref('') // yield "Add New" account name only
const selectedMonth = ref(String(new Date().getMonth() + 1).padStart(2, '0'))
const amount = ref(null)

const resolvedKey = computed(() =>
  props.type === 'yield' && selectedKey.value === '__new__'
    ? newKey.value.trim()
    : selectedKey.value,
)

const canSubmit = computed(
  () =>
    resolvedKey.value &&
    amount.value != null &&
    amount.value >= 0,
)

async function submit() {
  if (!canSubmit.value) return
  const key = resolvedKey.value
  const section = props.type === 'dividend' ? 'dividends' : 'yields'
  const name = props.type === 'dividend' ? (tickerName(key) || key) : undefined
  await store.saveEntryToYear(selectedYear.value, section, key, selectedMonth.value, amount.value, name)
  emit('saved')
  emit('close')
}
</script>
