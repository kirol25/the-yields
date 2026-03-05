<template>
  <div class="min-h-screen bg-gray-950 text-gray-100 flex flex-col">
    <nav class="bg-gray-900 border-b border-gray-800 px-6 py-4">
      <div class="max-w-7xl mx-auto flex items-center justify-between">
        <RouterLink to="/" class="text-xl font-bold text-emerald-400 tracking-tight hover:text-emerald-300 transition-colors">
          the-yield
        </RouterLink>

        <!-- Authenticated nav -->
        <div v-if="auth.isAuthenticated" class="flex items-center gap-1">
          <RouterLink
            to="/dashboard"
            class="px-3 py-1.5 text-sm font-medium rounded-lg transition-colors hover:bg-gray-800 hover:text-emerald-400"
            :class="$route.path === '/dashboard' ? 'text-emerald-400' : 'text-gray-400'"
          >
            {{ t('nav.dashboard') }}
          </RouterLink>
          <RouterLink
            to="/dividends"
            class="px-3 py-1.5 text-sm font-medium rounded-lg transition-colors hover:bg-gray-800 hover:text-emerald-400"
            :class="$route.path === '/dividends' ? 'text-emerald-400' : 'text-gray-400'"
          >
            {{ t('nav.dividends') }}
          </RouterLink>
          <RouterLink
            to="/yields"
            class="px-3 py-1.5 text-sm font-medium rounded-lg transition-colors hover:bg-gray-800 hover:text-emerald-400"
            :class="$route.path === '/yields' ? 'text-emerald-400' : 'text-gray-400'"
          >
            {{ t('nav.yields') }}
          </RouterLink>
          <RouterLink
            to="/subscriptions"
            class="px-3 py-1.5 text-sm font-medium rounded-lg transition-colors hover:bg-gray-800 hover:text-emerald-400"
            :class="$route.path === '/subscriptions' ? 'text-emerald-400' : 'text-gray-400'"
          >
            {{ t('nav.subscriptions') }}
          </RouterLink>
          <button
            @click="bladeOpen = true"
            class="w-8 h-8 rounded-full bg-emerald-600/20 border border-emerald-500/50 flex items-center justify-center text-xs font-bold text-emerald-400 hover:bg-emerald-600/30 transition-colors select-none"
            aria-label="Open profile"
          >
            {{ initials }}
          </button>
        </div>

        <!-- Guest nav (landing page) -->
        <div v-else class="flex items-center gap-1">
          <button
            @click="scrollToSection('features')"
            class="px-3 py-1.5 text-sm font-medium text-gray-400 hover:text-gray-100 hover:bg-gray-800 rounded-lg transition-colors"
          >
            {{ t('nav.features') }}
          </button>
          <button
            @click="scrollToSection('how-it-works')"
            class="px-3 py-1.5 text-sm font-medium text-gray-400 hover:text-gray-100 hover:bg-gray-800 rounded-lg transition-colors"
          >
            {{ t('nav.howItWorks') }}
          </button>
          <RouterLink
            to="/subscriptions"
            class="px-3 py-1.5 text-sm font-medium hover:bg-gray-800 rounded-lg transition-colors"
            :class="$route.path === '/subscriptions' ? 'text-emerald-400' : 'text-gray-400 hover:text-gray-100'"
          >
            {{ t('nav.subscriptions') }}
          </RouterLink>
          <RouterLink
            to="/login"
            class="ml-2 px-4 py-1.5 text-sm font-medium text-gray-900 bg-emerald-400 hover:bg-emerald-300 rounded-lg transition-colors"
          >
            {{ t('landing.signIn') }}
          </RouterLink>
        </div>
      </div>
    </nav>

    <main :class="isLanding ? 'flex-1 w-full' : 'max-w-7xl mx-auto px-6 pt-8 pb-16 flex-1 w-full'">
      <RouterView />
    </main>

    <footer class="mt-auto border-t border-gray-800 bg-gray-900/40">
      <div class="max-w-7xl mx-auto px-6 pt-8 pb-6">

        <!-- Columns -->
        <div class="grid grid-cols-4 gap-8 mb-8">

          <!-- Brand -->
          <div class="space-y-2">
            <span class="text-sm font-bold text-gray-100">the-yield</span>
            <p class="text-sm text-gray-500 leading-relaxed">{{ t('footer.tagline') }}</p>
          </div>

          <!-- App links -->
          <div class="space-y-3 justify-self-center">
            <h3 class="text-xs font-semibold uppercase tracking-wider text-gray-600">{{ t('footer.app') }}</h3>
            <ul class="space-y-2">
              <li><RouterLink to="/dashboard" class="text-sm text-gray-400 hover:text-gray-200 transition-colors">{{ t('nav.dashboard') }}</RouterLink></li>
              <li><RouterLink to="/dividends" class="text-sm text-gray-400 hover:text-gray-200 transition-colors">{{ t('nav.dividends') }}</RouterLink></li>
              <li><RouterLink to="/yields" class="text-sm text-gray-400 hover:text-gray-200 transition-colors">{{ t('nav.yields') }}</RouterLink></li>
            </ul>
          </div>

          <!-- Service -->
          <div class="space-y-3 justify-self-center">
            <h3 class="text-xs font-semibold uppercase tracking-wider text-gray-600">{{ t('footer.service') }}</h3>
            <ul class="space-y-2">
              <li><RouterLink to="/feedback" class="text-sm text-gray-400 hover:text-gray-200 transition-colors">{{ t('footer.contact') }}</RouterLink></li>
              <li><RouterLink to="/subscriptions" class="text-sm text-gray-400 hover:text-gray-200 transition-colors">{{ t('nav.subscriptions') }}</RouterLink></li>
            </ul>
          </div>

          <!-- Legal -->
          <div class="space-y-3 justify-self-center">
            <h3 class="text-xs font-semibold uppercase tracking-wider text-gray-600">{{ t('footer.legal') }}</h3>
            <ul class="space-y-2">
              <li><RouterLink to="/impressum" class="text-sm text-gray-400 hover:text-gray-200 transition-colors">{{ t('footer.impressum') }}</RouterLink></li>
              <li><RouterLink to="/datenschutz" class="text-sm text-gray-400 hover:text-gray-200 transition-colors">{{ t('footer.datenschutz') }}</RouterLink></li>
              <li><RouterLink to="/terms" class="text-sm text-gray-400 hover:text-gray-200 transition-colors">{{ t('footer.terms') }}</RouterLink></li>
            </ul>
          </div>

        </div>

        <!-- Bottom bar -->
        <div class="border-t border-gray-800 pt-5 flex flex-col sm:flex-row items-center justify-between gap-3">
          <p class="text-xs text-gray-600">© {{ new Date().getFullYear() }} Lorik Bajrami. {{ t('common.allRightsReserved') }}</p>
        </div>

      </div>
    </footer>

    <ProfileBlade v-if="auth.isAuthenticated" :open="bladeOpen" @close="bladeOpen = false" />
    <CookieBanner />
    <ToastContainer />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { useDataStore } from './stores/dataStore.js'
import { useSettingsStore } from './stores/settingsStore.js'
import { useAuthStore } from './stores/authStore.js'
import ProfileBlade from './components/ProfileBlade.vue'
import ToastContainer from './components/ToastContainer.vue'
import CookieBanner from './components/CookieBanner.vue'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const store = useDataStore()
const settings = useSettingsStore()
const auth = useAuthStore()
const bladeOpen = ref(false)

function scrollToSection(id) {
  if (route.path === '/') {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
  } else {
    router.push({ path: '/', hash: `#${id}` })
  }
}

// Apply persisted theme immediately (also wires up system listener if needed)
settings.setTheme(settings.theme)

const isLanding = computed(() => ['/', '/login', '/register', '/confirm', '/forgot-password', '/reset-password'].includes(route.path))

const initials = computed(() => {
  const name = (settings.profile.name || auth.user?.name || '').trim()
  if (!name) return '?'
  return name.split(' ').map((w) => w[0]).slice(0, 2).join('').toUpperCase()
})

// Seed profile name/email from token as soon as the user object is available,
// so initials show correctly before Profile.vue ever mounts.
watch(
  () => auth.user,
  (u) => {
    if (!u) return
    if (u.name && !settings.profile.name) {
      settings.profile.name = u.name
      settings.save()
    }
    if (u.email && !settings.profile.email) {
      settings.profile.email = u.email
      settings.save()
    }
  },
  { immediate: true },
)

// Only load data once authenticated
watch(
  () => auth.isAuthenticated,
  async (authed) => {
    if (authed) {
      const valid = await auth.ensureValidToken()
      if (!valid) return
      await store.fetchYears()
      await Promise.all([store.loadYear(store.currentYear), store.loadAllYears()])
    }
  },
  { immediate: true },
)
</script>
