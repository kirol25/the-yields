<template>
  <Transition name="fade">
    <div v-if="open" class="fixed inset-0 z-40 bg-black/50" @click="$emit('close')" />
  </Transition>

  <Transition name="slide">
    <div
      v-if="open"
      class="fixed top-0 right-0 z-50 h-full w-72 bg-gray-900 border-l border-gray-800 flex flex-col shadow-2xl"
    >
      <!-- Header -->
      <div class="flex items-center justify-between px-5 py-4 border-b border-gray-800">
        <h2 class="font-semibold text-gray-100">{{ t('blade.account') }}</h2>
        <button
          @click="$emit('close')"
          class="text-gray-400 hover:text-white transition-colors"
          aria-label="Close"
        >
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- User identity -->
      <div class="px-5 py-5 border-b border-gray-800 flex items-center gap-3">
        <div
          class="w-10 h-10 rounded-full bg-emerald-600/20 border-2 border-emerald-500 flex items-center justify-center text-sm font-bold text-emerald-400 select-none shrink-0"
        >
          {{ initials }}
        </div>
        <div class="min-w-0">
          <p class="text-sm font-medium text-gray-100 truncate">
            {{ settings.profile.name || t('profile.noName') }}
          </p>
          <p class="text-xs text-gray-500 truncate">
            {{ auth.user?.email || settings.profile.email || '—' }}
          </p>
        </div>
      </div>

      <!-- Nav items -->
      <nav class="flex-1 px-3 py-3 space-y-0.5">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          @click="$emit('close')"
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-gray-300 hover:bg-gray-800 hover:text-gray-100 transition-colors group"
          active-class="bg-gray-800 text-gray-100"
        >
          <span class="w-4 h-4 text-gray-500 group-hover:text-gray-400 shrink-0" v-html="item.icon" />
          {{ item.label }}
        </RouterLink>
      </nav>

      <!-- Theme toggle -->
      <div class="px-5 py-3 border-t border-gray-800 flex items-center justify-between">
        <span class="text-xs text-gray-500">{{ t('settings.theme') }}</span>
        <div class="flex items-center gap-1">
          <button
            v-for="opt in themeOptions"
            :key="opt.value"
            type="button"
            @click="settings.setTheme(opt.value)"
            :title="opt.title"
            :class="[
              'p-1.5 rounded-md transition-colors',
              settings.theme === opt.value
                ? 'bg-gray-700 text-gray-100'
                : 'text-gray-500 hover:text-gray-300 hover:bg-gray-800',
            ]"
            v-html="opt.icon"
          />
        </div>
      </div>

      <!-- Sign out -->
      <div class="px-5 py-4 border-t border-gray-800">
        <button
          @click="signOut"
          class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-gray-400 hover:bg-gray-800 hover:text-red-400 transition-colors"
        >
          <svg class="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          {{ t('blade.signOut') }}
        </button>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useSettingsStore } from '../stores/settingsStore.js'
import { useAuthStore } from '../stores/authStore.js'

const { t } = useI18n()

defineProps({ open: { type: Boolean, required: true } })
defineEmits(['close'])

const settings = useSettingsStore()
const auth = useAuthStore()
const router = useRouter()

async function signOut() {
  await auth.logout()
  router.push('/login')
}

const initials = computed(() => {
  const name = settings.profile.name.trim()
  if (!name) return '?'
  return name
    .split(' ')
    .map((w) => w[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
})

const themeOptions = [
  {
    value: 'dark',
    title: t('settings.themeDark'),
    icon: '<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M21 12.79A9 9 0 1111.21 3a7 7 0 109.79 9.79z"/></svg>',
  },
  {
    value: 'light',
    title: t('settings.themeLight'),
    icon: '<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>',
  },
  {
    value: 'system',
    title: t('settings.themeSystem'),
    icon: '<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" stroke-linecap="round" stroke-linejoin="round"/><path stroke-linecap="round" stroke-linejoin="round" d="M8 21h8M12 17v4"/></svg>',
  },
]

const navItems = computed(() => [
  {
    label: t('blade.profile'),
    to: '/profile',
    icon: '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>',
  },
  {
    label: t('blade.settings'),
    to: '/settings',
    icon: '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><circle cx="12" cy="12" r="3" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  },
])
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.25s ease;
}
.slide-enter-from,
.slide-leave-to {
  transform: translateX(100%);
}
</style>
