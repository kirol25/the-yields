<template>
  <div ref="container" class="relative flex items-center gap-1 bg-gray-900 border border-gray-800 rounded-lg px-1 py-1">
    <button
      @click="toggleOpen"
      class="flex items-center gap-1.5 px-2 text-sm font-medium text-gray-100 hover:text-emerald-400 transition-colors max-w-[140px]"
    >
      <!-- layers / stacked-accounts icon -->
      <svg class="w-3.5 h-3.5 text-gray-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 2L2 7l10 5 10-5-10-5z"/>
        <path d="M2 12l10 5 10-5"/>
        <path d="M2 17l10 5 10-5"/>
      </svg>
      <span class="truncate">{{ depotStore.currentDepot?.name || '…' }}</span>
      <svg class="w-3 h-3 text-gray-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
        <polyline points="6 9 12 15 18 9"/>
      </svg>
    </button>

    <Teleport to="body">
      <div v-if="open" class="fixed inset-0 z-40" @click="close" />
      <div
        v-if="open"
        :style="dropdownStyle"
        class="fixed z-50 bg-gray-900 border border-gray-700 rounded-lg shadow-xl py-1 min-w-[180px]"
      >
        <!-- Existing depots -->
        <button
          v-for="depot in depotStore.depots"
          :key="depot.id"
          @click="select(depot.id)"
          :class="[
            'w-full px-4 py-1.5 text-sm text-left transition-colors',
            depot.id === depotStore.currentDepotId
              ? 'text-emerald-400 font-medium bg-emerald-500/10'
              : 'text-gray-300 hover:bg-gray-800',
          ]"
        >
          {{ depot.name }}
        </button>

        <div class="border-t border-gray-800 my-1" />

        <!-- Premium: inline add form -->
        <template v-if="isPremium">
          <div v-if="!addingDepot" class="px-4 py-1.5">
            <button
              @click.stop="addingDepot = true"
              class="text-sm text-emerald-500 hover:text-emerald-400 transition-colors"
            >
              + {{ t('settings.addDepot') }}
            </button>
          </div>
          <div v-else class="px-3 py-2 flex items-center gap-1.5" @click.stop>
            <input
              ref="nameInput"
              v-model="newDepotName"
              :placeholder="t('settings.depotNamePlaceholder')"
              @keydown.enter="createDepot"
              @keydown.escape="cancelAdd"
              class="flex-1 min-w-0 bg-gray-800 border border-gray-700 rounded-md px-2 py-1 text-xs text-gray-100 placeholder-gray-600 focus:outline-none focus:ring-1 focus:ring-emerald-500"
            />
            <button
              @click="createDepot"
              :disabled="!newDepotName.trim() || creating"
              class="shrink-0 text-emerald-400 hover:text-emerald-300 disabled:opacity-40 transition-colors"
              title="Save"
            >
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
            </button>
            <button
              @click="cancelAdd"
              class="shrink-0 text-gray-500 hover:text-gray-300 transition-colors"
              title="Cancel"
            >
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
        </template>

        <!-- Free tier: locked -->
        <template v-else>
          <div class="px-4 py-1.5 flex items-center gap-1.5">
            <svg class="w-3 h-3 text-gray-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path stroke-linecap="round" stroke-linejoin="round" d="M7 11V7a5 5 0 0 1 10 0v4"/>
            </svg>
            <RouterLink
              to="/subscriptions"
              @click="close"
              class="text-xs text-emerald-400 hover:text-emerald-300 transition-colors"
            >
              {{ t('settings.upgradeBtn') }} →
            </RouterLink>
          </div>
        </template>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDepotStore } from '../stores/depotStore.js'
import { useDataStore } from '../stores/dataStore.js'
import { useSubscription } from '../composables/useSubscription.js'

const { t } = useI18n()
const depotStore = useDepotStore()
const dataStore = useDataStore()
const { isPremium } = useSubscription()

const open = ref(false)
const container = ref(null)
const dropdownStyle = ref({})

const addingDepot = ref(false)
const newDepotName = ref('')
const creating = ref(false)
const nameInput = ref(null)

function toggleOpen() {
  if (!open.value) {
    const rect = container.value?.getBoundingClientRect()
    if (rect) {
      dropdownStyle.value = {
        top: `${rect.bottom + 4}px`,
        left: `${rect.left}px`,
        minWidth: `${rect.width}px`,
      }
    }
  }
  open.value = !open.value
}

function close() {
  open.value = false
  cancelAdd()
}

function cancelAdd() {
  addingDepot.value = false
  newDepotName.value = ''
}

async function select(id) {
  if (id === depotStore.currentDepotId) {
    close()
    return
  }
  depotStore.selectDepot(id)
  close()
  dataStore.clearYearCache()
  await dataStore.fetchYears()
  await dataStore.loadYear(dataStore.currentYear)
}

async function createDepot() {
  if (!newDepotName.value.trim() || creating.value) return
  creating.value = true
  try {
    await depotStore.createDepot(newDepotName.value.trim())
    cancelAdd()
  } catch {
    // error toast handled in store
  } finally {
    creating.value = false
  }
}

// Focus the input when the add form appears
watch(addingDepot, (val) => {
  if (val) nextTick(() => nameInput.value?.focus())
})
</script>
