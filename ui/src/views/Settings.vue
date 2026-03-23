<template>
  <div class="max-w-lg mx-auto space-y-6">
    <h1 class="text-2xl font-bold">{{ t('settings.title') }}</h1>

    <!-- Finance -->
    <div class="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-5">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium">{{ t('settings.finance') }}</h2>

      <!-- Currency -->
      <div>
        <label class="block text-xs text-gray-400 mb-1.5">{{ t('settings.currency') }}</label>
        <div ref="currencyContainer" class="relative">
          <button
            type="button"
            @click="toggleCurrency"
            class="w-full flex items-center justify-between bg-gray-800 border border-gray-700 rounded-md px-3 py-2 text-sm text-gray-100 hover:border-gray-600 focus:outline-none focus:ring-2 focus:ring-emerald-500 transition-colors"
          >
            <span>{{ settings.currency }} - {{ settings.CURRENCIES.find(c => c.code === settings.currency)?.label }}</span>
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
                {{ c.code }} - {{ c.label }}
              </button>
            </div>
          </Teleport>
        </div>
      </div>
    </div>

    <!-- Depots -->
    <div class="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-4">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium">{{ t('settings.depots') }}</h2>
      <p class="text-xs text-gray-500">{{ t('settings.depotsDesc') }}</p>

      <!-- Depot list -->
      <ul class="space-y-2">
        <li
          v-for="depot in depotStore.depots"
          :key="depot.id"
          class="flex items-center justify-between gap-3 bg-gray-800 rounded-lg px-3 py-2"
        >
          <span v-if="editingDepotId !== depot.id" class="text-sm text-gray-200 flex-1 truncate">
            {{ depot.name }}
          </span>
          <input
            v-else
            v-model="editingName"
            @keydown.enter="saveRename(depot.id)"
            @keydown.escape="cancelEdit"
            class="flex-1 bg-gray-700 border border-gray-600 rounded px-2 py-0.5 text-sm text-gray-100 focus:outline-none focus:ring-1 focus:ring-emerald-500"
          />
          <div class="flex items-center gap-1 shrink-0">
            <template v-if="editingDepotId === depot.id">
              <button
                @click="saveRename(depot.id)"
                :disabled="!editingName.trim()"
                class="px-2 py-1 text-xs bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 rounded transition-colors"
              >
                {{ t('common.save') }}
              </button>
              <button
                @click="cancelEdit"
                class="px-2 py-1 text-xs text-gray-400 hover:text-gray-200 transition-colors"
              >
                {{ t('common.cancel') }}
              </button>
            </template>
            <template v-else>
              <button
                @click="startEdit(depot)"
                class="p-1 text-gray-500 hover:text-gray-200 transition-colors"
                :title="t('settings.renameDepot')"
              >
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                </svg>
              </button>
              <button
                v-if="depotStore.depots.length > 1"
                @click="confirmDelete(depot)"
                class="p-1 text-gray-500 hover:text-red-400 transition-colors"
                :title="t('settings.deleteDepot')"
              >
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <polyline points="3 6 5 6 21 6"/>
                  <path stroke-linecap="round" stroke-linejoin="round" d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6m5 0V4a1 1 0 011-1h2a1 1 0 011 1v2"/>
                </svg>
              </button>
            </template>
          </div>
        </li>
      </ul>

      <!-- Delete confirmation -->
      <div v-if="deletingDepot" class="bg-red-950/40 border border-red-800 rounded-lg p-3 space-y-2">
        <p class="text-sm text-red-300">{{ t('settings.deleteDepotConfirm', { name: deletingDepot.name }) }}</p>
        <div class="flex gap-2">
          <button
            @click="doDelete"
            :disabled="deleting"
            class="px-3 py-1.5 text-xs bg-red-600 hover:bg-red-500 disabled:opacity-40 rounded transition-colors"
          >
            {{ deleting ? t('settings.deleting') : t('settings.deleteDepot') }}
          </button>
          <button @click="deletingDepot = null" class="px-3 py-1.5 text-xs text-gray-400 hover:text-gray-200 transition-colors">
            {{ t('common.cancel') }}
          </button>
        </div>
      </div>

      <!-- Add depot -->
      <template v-if="isPremium">
        <div v-if="!addingDepot">
          <button
            @click="addingDepot = true"
            class="text-sm text-emerald-400 hover:text-emerald-300 transition-colors"
          >
            + {{ t('settings.addDepot') }}
          </button>
        </div>
        <div v-else class="flex gap-2">
          <input
            v-model="newDepotName"
            :placeholder="t('settings.depotNamePlaceholder')"
            @keydown.enter="createDepot"
            @keydown.escape="addingDepot = false; newDepotName = ''"
            class="flex-1 bg-gray-800 border border-gray-700 rounded-md px-3 py-2 text-sm text-gray-100 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          />
          <button
            @click="createDepot"
            :disabled="!newDepotName.trim() || creatingDepot"
            class="shrink-0 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 text-sm font-medium rounded-md transition-colors"
          >
            {{ t('common.save') }}
          </button>
          <button
            @click="addingDepot = false; newDepotName = ''"
            class="shrink-0 px-3 py-2 text-sm text-gray-400 hover:text-gray-200 transition-colors"
          >
            {{ t('common.cancel') }}
          </button>
        </div>
      </template>
      <template v-else>
        <div class="flex items-center gap-1.5 text-xs text-gray-500">
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path stroke-linecap="round" stroke-linejoin="round" d="M7 11V7a5 5 0 0 1 10 0v4"/>
          </svg>
          {{ t('settings.depotsLocked') }}
          <RouterLink to="/subscriptions" class="text-emerald-400 hover:text-emerald-300 transition-colors">
            {{ t('settings.upgradeBtn') }} →
          </RouterLink>
        </div>
      </template>
    </div>

    <!-- Goals -->
    <div class="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-4">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium">{{ t('settings.goals') }}</h2>
      <div>
        <label class="block text-xs text-gray-400 mb-1">
          {{ t('settings.dividendGoal') }} <span class="text-gray-600">({{ store.currentYear }})</span>
        </label>
        <p class="text-xs text-gray-500 mb-2">{{ t('settings.dividendGoalDesc') }}</p>
        <div class="flex gap-2">
          <input
            type="number"
            v-model.number="goalInput"
            min="0"
            :placeholder="t('settings.dividendGoalPlaceholder')"
            class="w-full bg-gray-800 border border-gray-700 rounded-md px-3 py-2 text-sm text-gray-100 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          />
          <button
            @click="saveGoal"
            :disabled="goalInput === (settings.dividendGoal[store.currentYear] || 0)"
            class="shrink-0 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 disabled:cursor-not-allowed text-sm font-medium rounded-md transition-colors"
          >
            {{ t('common.save') }}
          </button>
        </div>
      </div>

      <hr class="border-gray-800" />

      <!-- Yield goal -->
      <div>
        <label class="block text-xs text-gray-400 mb-1">
          {{ t('settings.yieldGoal') }} <span class="text-gray-600">({{ store.currentYear }})</span>
        </label>
        <p class="text-xs text-gray-500 mb-2">{{ t('settings.yieldGoalDesc') }}</p>
        <div class="flex gap-2">
          <input
            type="number"
            v-model.number="yieldGoalInput"
            min="0"
            :placeholder="t('settings.yieldGoalPlaceholder')"
            class="w-full bg-gray-800 border border-gray-700 rounded-md px-3 py-2 text-sm text-gray-100 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          />
          <button
            @click="saveYieldGoal"
            :disabled="yieldGoalInput === (settings.yieldGoal[store.currentYear] || 0)"
            class="shrink-0 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 disabled:cursor-not-allowed text-sm font-medium rounded-md transition-colors"
          >
            {{ t('common.save') }}
          </button>
        </div>
      </div>

      <hr class="border-gray-800" />

      <!-- Steuerfreibetrag -->
      <div>
        <label class="block text-xs text-gray-400 mb-1">
          {{ t('settings.steuerfreibetrag') }} <span class="text-gray-600">({{ store.currentYear }})</span>
        </label>
        <p class="text-xs text-gray-500 mb-2">{{ t('settings.steuerfreibetragDesc') }}</p>
        <div class="flex gap-2">
          <input
            type="number"
            v-model.number="steuerInput"
            min="0"
            max="2000"
            :placeholder="t('settings.steuerfreibetragPlaceholder')"
            :class="[
              'w-full bg-gray-800 rounded-md px-3 py-2 text-sm text-gray-100 focus:outline-none focus:ring-2 transition-colors',
              steuerInvalid
                ? 'border border-red-500 focus:ring-red-500 text-red-300'
                : 'border border-gray-700 focus:ring-emerald-500',
            ]"
          />
          <button
            @click="saveSteuer"
            :disabled="steuerInvalid || steuerInput === (settings.steuerfreibetrag[store.currentYear] ?? 1000)"
            class="shrink-0 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 disabled:cursor-not-allowed text-sm font-medium rounded-md transition-colors"
          >
            {{ t('common.save') }}
          </button>
        </div>
        <p v-if="steuerInvalid" class="text-xs text-red-400 mt-1.5">{{ t('settings.steuerfreibetragMax') }}</p>
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
        <!-- Premium: show export button -->
        <button
          v-if="isPremium"
          @click="exportCsv"
          :disabled="exporting || !hasData"
          class="shrink-0 flex items-center gap-1.5 px-3 py-1.5 bg-gray-800 hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed border border-gray-700 text-sm text-gray-200 font-medium rounded-md transition-colors"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
          </svg>
          {{ exporting ? t('settings.exporting') : t('settings.exportCsv') }}
        </button>
        <!-- Free: show locked state -->
        <div v-else class="shrink-0 flex flex-col items-end gap-1.5">
          <div class="flex items-center gap-1.5 text-xs text-gray-500">
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path stroke-linecap="round" stroke-linejoin="round" d="M7 11V7a5 5 0 0 1 10 0v4"/>
            </svg>
            {{ t('settings.exportLocked') }}
          </div>
          <RouterLink
            to="/subscriptions"
            class="text-xs font-medium text-emerald-400 hover:text-emerald-300 transition-colors"
          >
            {{ t('settings.upgradeBtn') }} →
          </RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSettingsStore } from '../stores/settingsStore.js'
import { useDataStore } from '../stores/dataStore.js'
import { useDepotStore } from '../stores/depotStore.js'
import { useSubscription } from '../composables/useSubscription.js'

const { t } = useI18n()
const settings = useSettingsStore()
const store = useDataStore()
const depotStore = useDepotStore()
const { isPremium } = useSubscription()

// ── Depot management ───────────────────────────────────────────────────────────
const addingDepot = ref(false)
const newDepotName = ref('')
const creatingDepot = ref(false)
const editingDepotId = ref(null)
const editingName = ref('')
const deletingDepot = ref(null)
const deleting = ref(false)

function startEdit(depot) {
  editingDepotId.value = depot.id
  editingName.value = depot.name
}

function cancelEdit() {
  editingDepotId.value = null
  editingName.value = ''
}

async function saveRename(id) {
  if (!editingName.value.trim()) return
  try {
    await depotStore.renameDepot(id, editingName.value.trim())
    cancelEdit()
  } catch {
    // error toast handled in store
  }
}

async function createDepot() {
  if (!newDepotName.value.trim() || creatingDepot.value) return
  creatingDepot.value = true
  try {
    await depotStore.createDepot(newDepotName.value.trim())
    newDepotName.value = ''
    addingDepot.value = false
  } catch {
    // error toast handled in store
  } finally {
    creatingDepot.value = false
  }
}

function confirmDelete(depot) {
  deletingDepot.value = depot
}

async function doDelete() {
  if (!deletingDepot.value || deleting.value) return
  deleting.value = true
  try {
    await depotStore.deleteDepot(deletingDepot.value.id)
    deletingDepot.value = null
  } catch {
    // error toast handled in store
  } finally {
    deleting.value = false
  }
}

// Goals
const goalInput      = ref(settings.dividendGoal[store.currentYear] || 0)
const yieldGoalInput = ref(settings.yieldGoal[store.currentYear] || 0)
const steuerInput    = ref(settings.steuerfreibetrag[store.currentYear] ?? 1000)

watch(() => store.currentYear, (y) => {
  goalInput.value      = settings.dividendGoal[y] || 0
  yieldGoalInput.value = settings.yieldGoal[y] || 0
  steuerInput.value    = settings.steuerfreibetrag[y] ?? 1000
})

const steuerInvalid = computed(() => steuerInput.value > 2000 || steuerInput.value < 0)

function saveGoal()      { settings.setDividendGoal(store.currentYear, goalInput.value || 0) }
function saveYieldGoal() { settings.setYieldGoal(store.currentYear, yieldGoalInput.value || 0) }
function saveSteuer()    { if (!steuerInvalid.value) settings.setSteuerfreibetrag(store.currentYear, steuerInput.value || 0) }

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
  settings.setCurrency(code)
  currencyOpen.value = false
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
    a.download = `the-yields-${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
  } finally {
    exporting.value = false
  }
}
</script>
