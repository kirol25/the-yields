<template>
  <div class="max-w-lg space-y-6">
    <h1 class="text-2xl font-bold">Profile</h1>

    <div class="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-5">
      <!-- Avatar -->
      <div class="flex items-center gap-4">
        <div
          class="w-14 h-14 rounded-full bg-emerald-600/20 border-2 border-emerald-500 flex items-center justify-center text-xl font-bold text-emerald-400 select-none shrink-0"
        >
          {{ initials }}
        </div>
        <div>
          <p class="text-sm font-medium text-gray-100">{{ settings.profile.name || 'No name set' }}</p>
          <p class="text-xs text-gray-500">{{ auth.user?.email || '—' }}</p>
        </div>
      </div>

      <hr class="border-gray-800" />

      <!-- Name -->
      <div>
        <label class="block text-xs text-gray-400 mb-1.5">Name</label>
        <input
          v-model="settings.profile.name"
          type="text"
          placeholder="Your name"
          class="w-full bg-gray-800 border border-gray-700 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 text-gray-100"
        />
      </div>

      <!-- Email (read-only) -->
      <div>
        <label class="block text-xs text-gray-400 mb-1.5">Email</label>
        <div class="w-full bg-gray-800/50 border border-gray-700/50 rounded-md px-3 py-2 text-sm text-gray-500 flex items-center gap-2 select-none">
          <svg class="w-3.5 h-3.5 shrink-0 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path stroke-linecap="round" stroke-linejoin="round" d="M7 11V7a5 5 0 0 1 10 0v4"/>
          </svg>
          {{ auth.user?.email || settings.profile.email || '—' }}
        </div>
        <p class="text-xs text-gray-600 mt-1">Email is managed by your account provider.</p>
      </div>

      <button
        @click="save"
        class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-sm font-medium rounded-md transition-colors"
      >
        Save
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, watch } from 'vue'
import { useSettingsStore } from '../stores/settingsStore.js'
import { useAuthStore } from '../stores/authStore.js'

const settings = useSettingsStore()
const auth = useAuthStore()

watch(
  () => auth.user,
  (u) => {
    if (!u) return
    if (!settings.profile.name && u.name) settings.profile.name = u.name
    if (!settings.profile.email && u.email) settings.profile.email = u.email
  },
  { immediate: true },
)

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

function save() {
  settings.save()
}
</script>
