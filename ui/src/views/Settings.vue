<template>
  <div class="max-w-lg space-y-6">
    <h1 class="text-2xl font-bold">{{ t('settings.title') }}</h1>

    <div class="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-5">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium">{{ t('settings.preferences') }}</h2>

      <!-- Currency -->
      <div>
        <label class="block text-xs text-gray-400 mb-1.5">{{ t('settings.currency') }}</label>
        <div ref="currencyContainer" class="relative">
          <button
            type="button"
            @click="toggleCurrency"
            class="w-full flex items-center justify-between bg-gray-800 border border-gray-700 rounded-md px-3 py-2 text-sm text-gray-100 hover:border-gray-600 focus:outline-none focus:ring-2 focus:ring-emerald-500 transition-colors"
          >
            <span>{{ settings.currency }} — {{ settings.CURRENCIES.find(c => c.code === settings.currency)?.label }}</span>
            <svg class="w-3.5 h-3.5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <polyline points="6 9 12 15 18 9"/>
            </svg>
          </button>
          <Teleport to="body">
            <div v-if="currencyOpen" class="fixed inset-0 z-40" @click="currencyOpen = false" />
            <div
              v-if="currencyOpen"
              :style="currencyStyle"
              class="fixed z-50 bg-gray-900 border border-gray-700 rounded-lg shadow-xl py-1 min-w-[200px]"
            >
              <button
                v-for="c in settings.CURRENCIES"
                :key="c.code"
                type="button"
                @click="selectCurrency(c.code)"
                :class="[
                  'w-full px-4 py-1.5 text-sm text-left transition-colors',
                  c.code === settings.currency
                    ? 'text-emerald-400 font-medium bg-emerald-500/10'
                    : 'text-gray-300 hover:bg-gray-800',
                ]"
              >
                {{ c.code }} — {{ c.label }}
              </button>
            </div>
          </Teleport>
        </div>
      </div>

      <!-- Language -->
      <div>
        <label class="block text-xs text-gray-400 mb-1.5">{{ t('settings.language') }}</label>
        <div ref="langContainer" class="relative">
          <button
            type="button"
            @click="toggleLang"
            class="w-full flex items-center justify-between bg-gray-800 border border-gray-700 rounded-md px-3 py-2 text-sm text-gray-100 hover:border-gray-600 focus:outline-none focus:ring-2 focus:ring-emerald-500 transition-colors"
          >
            <span>{{ settings.LANGUAGES.find(l => l.code === settings.locale)?.label }}</span>
            <svg class="w-3.5 h-3.5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <polyline points="6 9 12 15 18 9"/>
            </svg>
          </button>
          <Teleport to="body">
            <div v-if="langOpen" class="fixed inset-0 z-40" @click="langOpen = false" />
            <div
              v-if="langOpen"
              :style="langStyle"
              class="fixed z-50 bg-gray-900 border border-gray-700 rounded-lg shadow-xl py-1 min-w-[200px]"
            >
              <button
                v-for="l in settings.LANGUAGES"
                :key="l.code"
                type="button"
                @click="selectLang(l.code)"
                :class="[
                  'w-full px-4 py-1.5 text-sm text-left transition-colors',
                  l.code === settings.locale
                    ? 'text-emerald-400 font-medium bg-emerald-500/10'
                    : 'text-gray-300 hover:bg-gray-800',
                ]"
              >
                {{ l.label }}
              </button>
            </div>
          </Teleport>
        </div>
      </div>
    </div>

    <!-- Data -->
    <div class="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-4">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium">{{ t('settings.data') }}</h2>

      <div class="flex items-start justify-between gap-4">
        <div>
          <p class="text-sm font-medium text-gray-200">{{ t('settings.exportCsv') }}</p>
          <p class="text-xs text-gray-500 mt-0.5">{{ t('settings.exportCsvDesc') }}</p>
        </div>
        <button
          @click="exportCsv"
          :disabled="exporting || !hasData"
          class="shrink-0 flex items-center gap-1.5 px-3 py-1.5 bg-gray-800 hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed border border-gray-700 text-sm text-gray-200 font-medium rounded-md transition-colors"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
          </svg>
          {{ exporting ? t('settings.exporting') : t('settings.exportCsv') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSettingsStore } from '../stores/settingsStore.js'
import { useDataStore } from '../stores/dataStore.js'

const { t } = useI18n()
const settings = useSettingsStore()
const store = useDataStore()

const currencyContainer = ref(null)
const currencyOpen = ref(false)
const currencyStyle = ref({})

function toggleCurrency() {
  if (!currencyOpen.value) {
    const rect = currencyContainer.value?.getBoundingClientRect()
    if (rect) {
      currencyStyle.value = {
        top: `${rect.bottom + 4}px`,
        left: `${rect.left}px`,
        width: `${rect.width}px`,
      }
    }
  }
  currencyOpen.value = !currencyOpen.value
}

function selectCurrency(code) {
  settings.currency = code
  settings.save()
  currencyOpen.value = false
}

const langContainer = ref(null)
const langOpen = ref(false)
const langStyle = ref({})

function toggleLang() {
  if (!langOpen.value) {
    const rect = langContainer.value?.getBoundingClientRect()
    if (rect) {
      langStyle.value = {
        top: `${rect.bottom + 4}px`,
        left: `${rect.left}px`,
        width: `${rect.width}px`,
      }
    }
  }
  langOpen.value = !langOpen.value
}

function selectLang(code) {
  settings.setLocale(code)
  langOpen.value = false
}

// ── CSV export ────────────────────────────────────────────────────────────────

const MONTH_KEYS = ['01','02','03','04','05','06','07','08','09','10','11','12']
const MONTH_LABELS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

const exporting = ref(false)

const hasData = computed(() => Object.keys(store.allYearsData).length > 0)

function buildRows() {
  const rows = [['Year', 'Type', 'Ticker / Account', 'Name', ...MONTH_LABELS, 'Total']]
  const sortedYears = Object.keys(store.allYearsData).map(Number).sort((a, b) => a - b)

  for (const year of sortedYears) {
    const { dividends = {}, yields = {} } = store.allYearsData[year]

    for (const [ticker, entry] of Object.entries(dividends)) {
      const monthly = MONTH_KEYS.map((m) => entry.months?.[m] ?? '')
      const total = monthly.reduce((s, v) => s + (v || 0), 0)
      rows.push([year, 'Dividend', ticker, entry.name ?? '', ...monthly, total])
    }

    for (const [account, entry] of Object.entries(yields)) {
      const monthly = MONTH_KEYS.map((m) => entry.months?.[m] ?? '')
      const total = monthly.reduce((s, v) => s + (v || 0), 0)
      rows.push([year, 'Yield', account, '', ...monthly, total])
    }
  }

  return rows
}

function toCsv(rows) {
  return rows
    .map((row) =>
      row
        .map((cell) => {
          const s = String(cell ?? '')
          return s.includes(';') || s.includes('"') || s.includes('\n')
            ? `"${s.replace(/"/g, '""')}"`
            : s
        })
        .join(';'),
    )
    .join('\n')
}

async function exportCsv() {
  if (exporting.value) return
  exporting.value = true
  try {
    if (!hasData.value) await store.loadAllYears()
    const csv = toCsv(buildRows())
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `the-yield-${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
  } finally {
    exporting.value = false
  }
}
</script>
