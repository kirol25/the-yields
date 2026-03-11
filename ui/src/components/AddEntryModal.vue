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

          <!-- Free-tier limit banner -->
          <div v-if="atLimit && selectedKey === '__new__'" class="flex items-start gap-3 bg-amber-500/10 border border-amber-500/30 rounded-lg px-4 py-3">
            <svg class="w-4 h-4 text-amber-400 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
            </svg>
            <div class="min-w-0">
              <p class="text-xs font-medium text-amber-400">{{ t('upsell.tickerLimitTitle', { n: store.freeTierLimit }) }}</p>
              <p class="text-xs text-amber-300/70 mt-0.5">{{ t('upsell.tickerLimitDesc') }}</p>
              <RouterLink to="/subscriptions" @click="$emit('close')" class="inline-block mt-1.5 text-xs font-medium text-emerald-400 hover:text-emerald-300 transition-colors">
                {{ t('upsell.upgrade') }} →
              </RouterLink>
            </div>
          </div>

          <!-- Ticker / Bank — custom dropdown -->
          <div>
            <label class="block text-xs font-medium text-gray-400 mb-1.5">
              {{ props.type === 'dividend' ? t('modal.ticker') : t('modal.bankAccount') }}
            </label>
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
                  v-for="key in props.existingKeys"
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
                <div v-if="props.existingKeys.length" class="border-t border-gray-800 my-1" />
                <button
                  type="button"
                  :disabled="atLimit"
                  @click="!atLimit && (selectedKey = '__new__', keyOpen = false)"
                  :class="[
                    'w-full px-3 py-2 text-sm text-left transition-colors',
                    atLimit ? 'text-gray-600 cursor-not-allowed' : selectedKey === '__new__' ? 'text-emerald-400 bg-emerald-500/10' : 'text-emerald-500 hover:bg-gray-800',
                  ]"
                >
                  {{ t('modal.addNew') }}{{ atLimit ? ` (${t('upsell.limitReached')})` : '' }}
                </button>
              </div>
            </div>
          </div>

          <!-- New ticker + name (side by side for dividends) -->
          <div v-if="selectedKey === '__new__'">
            <div v-if="props.type === 'dividend'" class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-medium text-gray-400 mb-1.5">{{ t('modal.tickerSymbol') }}</label>
                <input
                  v-model="newKey"
                  type="text"
                  placeholder="e.g. AAPL"
                  class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-sm text-gray-100 placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-emerald-500 hover:border-gray-600 transition-colors"
                />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-400 mb-1.5">{{ t('modal.name') }}</label>
                <input
                  v-model="newName"
                  type="text"
                  :placeholder="t('modal.companyNamePlaceholder')"
                  class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-sm text-gray-100 placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-emerald-500 hover:border-gray-600 transition-colors"
                />
              </div>
            </div>
            <div v-else>
              <label class="block text-xs font-medium text-gray-400 mb-1.5">{{ t('modal.name') }}</label>
              <input
                v-model="newKey"
                type="text"
                placeholder="e.g. Chase HYSA"
                class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-sm text-gray-100 placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-emerald-500 hover:border-gray-600 transition-colors"
              />
            </div>
          </div>

          <!-- Edit company name for existing dividend tickers -->
          <div v-if="selectedKey !== '__new__' && props.type === 'dividend'">
            <label class="block text-xs font-medium text-gray-400 mb-1.5">{{ t('modal.name') }}</label>
            <input
              v-model="existingName"
              type="text"
              :placeholder="t('modal.companyNamePlaceholder')"
              class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-sm text-gray-100 placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-emerald-500 hover:border-gray-600 transition-colors"
            />
          </div>

          <!-- Month — chip grid -->
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
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDataStore } from '../stores/dataStore.js'
import { useMonths } from '../composables/useMonths.js'
import { useSubscription } from '../composables/useSubscription.js'

const { t } = useI18n()
const { months } = useMonths()
const { isPremium } = useSubscription()

const props = defineProps({
  type: { type: String, required: true }, // 'dividend' | 'yield'
  existingKeys: { type: Array, default: () => [] },
})
const emit = defineEmits(['close', 'saved'])

const store = useDataStore()

// Free users cannot add more tickers/accounts than the server-defined limit
const atLimit = computed(
  () => !isPremium.value && props.existingKeys.length >= store.freeTierLimit,
)

const selectedKey = ref(atLimit.value ? '__new__' : (props.existingKeys[0] ?? '__new__'))
const keyOpen = ref(false)
const newKey = ref('')
const newName = ref('')
const existingName = ref(
  props.existingKeys[0] ? (store.yearData.dividends?.[props.existingKeys[0]]?.name ?? '') : '',
)
const selectedMonth = ref(String(new Date().getMonth() + 1).padStart(2, '0'))
const amount = ref(null)

watch(selectedKey, (key) => {
  if (key !== '__new__') {
    existingName.value = store.yearData.dividends?.[key]?.name ?? ''
  }
})

const resolvedKey = computed(() =>
  selectedKey.value === '__new__' ? newKey.value.trim() : selectedKey.value,
)

const isAddingNew = computed(() => selectedKey.value === '__new__')
const canSubmit = computed(
  () => resolvedKey.value && amount.value != null && amount.value >= 0 && !(atLimit.value && isAddingNew.value),
)

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

  // Update company name if changed for existing or new dividend entries
  if (props.type === 'dividend') {
    const name = selectedKey.value === '__new__' ? newName.value.trim() : existingName.value.trim()
    if (name) store.yearData[section][key].name = name
  }

  store.yearData[section][key].months[selectedMonth.value] = amount.value

  await store.saveData()
  emit('saved')
  emit('close')
}
</script>
