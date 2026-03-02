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
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSettingsStore } from '../stores/settingsStore.js'

const { t } = useI18n()
const settings = useSettingsStore()

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
</script>
