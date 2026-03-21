<template>
  <div class="min-h-screen bg-gray-950 text-gray-100 flex flex-col">
    <nav class="bg-gray-900 border-b border-gray-800 px-4 sm:px-6 py-4 relative z-50">
      <div class="max-w-7xl mx-auto flex items-center justify-between">
        <RouterLink to="/" class="flex items-center gap-2 text-xl font-bold text-emerald-400 tracking-tight hover:text-emerald-300 transition-colors">
          <img src="/favicon.svg" alt="" class="w-7 h-7" aria-hidden="true" />
          the-yields
        </RouterLink>

        <!-- Authenticated nav - desktop -->
        <div v-if="auth.isAuthenticated" class="hidden md:flex items-center gap-1">
          <RouterLink
            to="/dashboard"
            class="px-3 py-1.5 text-sm font-medium rounded-lg transition-colors hover:bg-gray-800 hover:text-emerald-400"
            :class="normalizedPath === '/dashboard' ? 'text-emerald-400' : 'text-gray-400'"
          >
            {{ t('nav.dashboard') }}
          </RouterLink>
          <RouterLink
            to="/dividends"
            class="px-3 py-1.5 text-sm font-medium rounded-lg transition-colors hover:bg-gray-800 hover:text-emerald-400"
            :class="normalizedPath === '/dividends' ? 'text-emerald-400' : 'text-gray-400'"
          >
            {{ t('nav.dividends') }}
          </RouterLink>
          <RouterLink
            to="/yields"
            class="px-3 py-1.5 text-sm font-medium rounded-lg transition-colors hover:bg-gray-800 hover:text-emerald-400"
            :class="normalizedPath === '/yields' ? 'text-emerald-400' : 'text-gray-400'"
          >
            {{ t('nav.yields') }}
          </RouterLink>
          <RouterLink
            v-if="!isPremium"
            to="/subscriptions"
            class="px-3 py-1.5 text-sm font-medium rounded-lg transition-colors hover:bg-gray-800 hover:text-emerald-400"
            :class="normalizedPath === '/subscriptions' ? 'text-emerald-400' : 'text-gray-400'"
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

        <!-- Guest nav - desktop -->
        <div v-else class="hidden md:flex items-center gap-1">
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
          <button
            @click="scrollToSection('subscription')"
            class="px-3 py-1.5 text-sm font-medium text-gray-400 hover:text-gray-100 hover:bg-gray-800 rounded-lg transition-colors"
          >
            {{ t('nav.subscriptions') }}
          </button>
          <RouterLink
            to="/login"
            class="ml-2 px-4 py-1.5 text-sm font-medium text-gray-900 bg-emerald-400 hover:bg-emerald-300 rounded-lg transition-colors"
          >
            {{ t('landing.signIn') }}
          </RouterLink>
        </div>

        <!-- Mobile right side -->
        <div class="flex md:hidden items-center gap-2">
          <!-- Profile avatar (authenticated) -->
          <button
            v-if="auth.isAuthenticated"
            @click="bladeOpen = true"
            class="w-8 h-8 rounded-full bg-emerald-600/20 border border-emerald-500/50 flex items-center justify-center text-xs font-bold text-emerald-400 hover:bg-emerald-600/30 transition-colors select-none"
            aria-label="Open profile"
          >
            {{ initials }}
          </button>
          <!-- Hamburger -->
          <button
            @click="mobileMenuOpen = !mobileMenuOpen"
            class="p-2 rounded-lg text-gray-400 hover:text-gray-100 hover:bg-gray-800 transition-colors"
            aria-label="Toggle menu"
          >
            <svg v-if="!mobileMenuOpen" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16"/>
            </svg>
            <svg v-else class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Mobile dropdown -->
      <Transition
        enter-active-class="transition-all duration-200 ease-out"
        enter-from-class="opacity-0 -translate-y-2"
        leave-active-class="transition-all duration-150 ease-in"
        leave-to-class="opacity-0 -translate-y-2"
      >
        <div
          v-if="mobileMenuOpen"
          class="md:hidden absolute top-full left-0 right-0 bg-gray-900 border-b border-gray-800 shadow-xl px-4 py-3 space-y-1"
        >
          <template v-if="auth.isAuthenticated">
            <RouterLink
              v-for="link in [
                { to: '/dashboard', label: t('nav.dashboard') },
                { to: '/dividends', label: t('nav.dividends') },
                { to: '/yields', label: t('nav.yields') },
                ...(!isPremium ? [{ to: '/subscriptions', label: t('nav.subscriptions') }] : []),
              ]"
              :key="link.to"
              :to="link.to"
              @click="closeMobileMenu"
              class="block px-4 py-2.5 text-sm font-medium rounded-lg transition-colors"
              :class="normalizedPath === link.to ? 'bg-gray-800 text-emerald-400' : 'text-gray-400 hover:bg-gray-800 hover:text-gray-100'"
            >
              {{ link.label }}
            </RouterLink>
          </template>
          <template v-else>
            <button
              @click="scrollToSection('features'); closeMobileMenu()"
              class="w-full text-left px-4 py-2.5 text-sm font-medium text-gray-400 hover:bg-gray-800 hover:text-gray-100 rounded-lg transition-colors"
            >
              {{ t('nav.features') }}
            </button>
            <button
              @click="scrollToSection('how-it-works'); closeMobileMenu()"
              class="w-full text-left px-4 py-2.5 text-sm font-medium text-gray-400 hover:bg-gray-800 hover:text-gray-100 rounded-lg transition-colors"
            >
              {{ t('nav.howItWorks') }}
            </button>
            <RouterLink
              to="/subscriptions"
              @click="closeMobileMenu"
              class="block px-4 py-2.5 text-sm font-medium rounded-lg transition-colors"
              :class="normalizedPath === '/subscriptions' ? 'bg-gray-800 text-emerald-400' : 'text-gray-400 hover:bg-gray-800 hover:text-gray-100'"
            >
              {{ t('nav.subscriptions') }}
            </RouterLink>
            <RouterLink
              to="/login"
              @click="closeMobileMenu"
              class="block px-4 py-2.5 text-sm font-medium text-gray-900 bg-emerald-400 hover:bg-emerald-300 rounded-lg transition-colors text-center mt-2"
            >
              {{ t('landing.signIn') }}
            </RouterLink>
          </template>
        </div>
      </Transition>
    </nav>

    <main :class="isLanding ? 'flex-1 w-full' : 'max-w-7xl mx-auto px-4 sm:px-6 pt-6 sm:pt-8 pb-16 flex-1 w-full'">
      <RouterView />
    </main>

    <footer class="mt-auto border-t border-gray-800 bg-gray-900/40">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 pt-8 pb-6">

        <!-- Columns -->
        <div class="grid grid-cols-3 sm:grid-cols-4 gap-6 sm:gap-8 mb-8">

          <!-- Brand -->
          <div class="col-span-3 sm:col-span-1 space-y-2">
            <span class="text-sm font-bold text-gray-100">the-yields</span>
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
        <div class="border-t border-gray-800 pt-5 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p class="text-xs text-gray-600">© {{ new Date().getFullYear() }} {{ APP_NAME }}. {{ t('common.allRightsReserved') }}</p>
          <div class="flex items-center gap-2 text-sm text-gray-500">
            <svg class="h-4 w-4 text-gray-600" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fill-rule="evenodd" d="M10 2a8 8 0 1 0 0 16 8 8 0 0 0 0-16Zm5.25 7h-2.02a12.2 12.2 0 0 0-1.18-4.06A6.52 6.52 0 0 1 15.25 9Zm-5.25 7a10.7 10.7 0 0 1-1.72-5h3.44A10.7 10.7 0 0 1 10 16Zm-1.72-7a10.7 10.7 0 0 1 1.72-5 10.7 10.7 0 0 1 1.72 5H8.28Zm-3.33 2h2.02c.17 1.46.57 2.84 1.18 4.06A6.52 6.52 0 0 1 4.95 11Zm0-2a6.52 6.52 0 0 1 3.1-4.06A12.2 12.2 0 0 0 6.87 9H4.95Zm7.1 6.06c.61-1.22 1.01-2.6 1.18-4.06h2.02a6.52 6.52 0 0 1-3.2 4.06Z" clip-rule="evenodd" />
            </svg>
            <button
              type="button"
              class="transition-colors"
              :class="settings.locale === 'de' ? 'text-gray-100' : 'hover:text-gray-200'"
              @click="setLanguage('de')"
            >
              {{ t('languages.de') }}
            </button>
            <span class="text-gray-700">·</span>
            <button
              type="button"
              class="transition-colors"
              :class="settings.locale === 'en' ? 'text-gray-100' : 'hover:text-gray-200'"
              @click="setLanguage('en')"
            >
              {{ t('languages.en') }}
            </button>
          </div>
        </div>

      </div>
    </footer>

    <ProfileBlade v-if="auth.isAuthenticated" :open="bladeOpen" @close="bladeOpen = false" />
    <CookieBanner />
    <ToastContainer />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { APP_NAME } from './config.js'
import { useRoute, useRouter } from 'vue-router'
import { localizePath, stripLocalePrefix } from './router/locale.js'
import { useDataStore } from './stores/dataStore.js'
import { useDepotStore } from './stores/depotStore.js'
import { useSettingsStore } from './stores/settingsStore.js'
import { useAuthStore } from './stores/authStore.js'
import { useSubscription } from './composables/useSubscription.js'
import ProfileBlade from './components/ProfileBlade.vue'
import ToastContainer from './components/ToastContainer.vue'
import CookieBanner from './components/CookieBanner.vue'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const store = useDataStore()
const depotStore = useDepotStore()
const settings = useSettingsStore()
const auth = useAuthStore()
const { isPremium } = useSubscription()
const bladeOpen = ref(false)
const mobileMenuOpen = ref(false)

function closeMobileMenu() { mobileMenuOpen.value = false }
function setLanguage(code) {
  settings.setLocale(code)
  const localizedPath = localizePath(route.path, code)
  if (localizedPath !== route.path) {
    router.push({ path: localizedPath, query: route.query, hash: route.hash })
  }
}

function onKeyDown(e) { if (e.key === 'Escape') closeMobileMenu() }
onMounted(() => { document.addEventListener('keydown', onKeyDown) })
onUnmounted(() => { document.removeEventListener('keydown', onKeyDown) })

watch(() => route.path, () => { mobileMenuOpen.value = false })

const normalizedPath = computed(() => stripLocalePrefix(route.path))

function scrollToSection(id) {
  if (normalizedPath.value === '/') {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
  } else {
    router.push({ path: localizePath('/', settings.locale), hash: `#${id}` })
  }
}

// Apply persisted theme immediately (also wires up system listener if needed)
settings.setTheme(settings.theme)

const isLanding = computed(() => ['/', '/login', '/register', '/confirm', '/forgot-password', '/reset-password'].includes(normalizedPath.value))

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
      await Promise.all([settings.loadFromServer(), store.fetchMe(), depotStore.fetchDepots()])
      await store.fetchYears()
      await Promise.all([store.loadYear(store.currentYear), store.loadAllYears()])
    }
  },
  { immediate: true },
)
</script>
