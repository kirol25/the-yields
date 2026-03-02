<template>
  <div class="min-h-screen bg-gray-950 text-gray-100 flex flex-col">
    <nav class="bg-gray-900 border-b border-gray-800 px-6 py-4">
      <div class="max-w-7xl mx-auto flex items-center justify-between">
        <RouterLink to="/" class="text-xl font-bold text-emerald-400 tracking-tight hover:text-emerald-300 transition-colors">
          the-yield
        </RouterLink>

        <div v-if="auth.isAuthenticated" class="flex items-center gap-6">
          <RouterLink
            to="/"
            class="text-sm font-medium transition-colors hover:text-emerald-400"
            :class="$route.path === '/' ? 'text-emerald-400' : 'text-gray-400'"
          >
            {{ t('nav.dashboard') }}
          </RouterLink>
          <RouterLink
            to="/dividends"
            class="text-sm font-medium transition-colors hover:text-emerald-400"
            :class="$route.path === '/dividends' ? 'text-emerald-400' : 'text-gray-400'"
          >
            {{ t('nav.dividends') }}
          </RouterLink>
          <RouterLink
            to="/yields"
            class="text-sm font-medium transition-colors hover:text-emerald-400"
            :class="$route.path === '/yields' ? 'text-emerald-400' : 'text-gray-400'"
          >
            {{ t('nav.yields') }}
          </RouterLink>

          <button
            @click="bladeOpen = true"
            class="w-8 h-8 rounded-full bg-emerald-600/20 border border-emerald-500/50 flex items-center justify-center text-xs font-bold text-emerald-400 hover:bg-emerald-600/30 transition-colors select-none"
            aria-label="Open profile"
          >
            {{ initials }}
          </button>
        </div>
      </div>
    </nav>

    <main class="max-w-7xl mx-auto px-6 py-8 flex-1 w-full">
      <RouterView />
    </main>

    <footer class="mt-auto">
      <div class="max-w-7xl mx-auto px-6 py-6 border-t border-gray-800 flex flex-col items-center gap-3">
        <nav class="flex items-center gap-3">
          <RouterLink to="/impressum" class="text-sm text-gray-500 hover:text-gray-300 transition-colors">
            {{ t('footer.impressum') }}
          </RouterLink>
          <span class="w-1 h-1 rounded-full bg-gray-700" />
          <RouterLink to="/datenschutz" class="text-sm text-gray-500 hover:text-gray-300 transition-colors">
            {{ t('footer.datenschutz') }}
          </RouterLink>
        </nav>
        <p class="text-xs text-gray-600">© {{ new Date().getFullYear() }} Lorik Bajrami. {{ t('common.allRightsReserved') }}</p>
      </div>
    </footer>

    <ProfileBlade v-if="auth.isAuthenticated" :open="bladeOpen" @close="bladeOpen = false" />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDataStore } from './stores/dataStore.js'
import { useSettingsStore } from './stores/settingsStore.js'
import { useAuthStore } from './stores/authStore.js'
import ProfileBlade from './components/ProfileBlade.vue'

const { t } = useI18n()
const store = useDataStore()
const settings = useSettingsStore()
const auth = useAuthStore()
const bladeOpen = ref(false)

const initials = computed(() => {
  const name = (settings.profile.name || auth.user?.name || '').trim()
  if (!name) return '?'
  return name.split(' ').map((w) => w[0]).slice(0, 2).join('').toUpperCase()
})

// Only load data once authenticated
watch(
  () => auth.isAuthenticated,
  async (authed) => {
    if (authed) {
      await store.fetchYears()
      await Promise.all([store.loadYear(store.currentYear), store.loadAllYears()])
    }
  },
  { immediate: true },
)
</script>
