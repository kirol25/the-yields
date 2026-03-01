<template>
  <Transition name="fade">
    <div v-if="open" class="fixed inset-0 z-40 bg-black/50" @click="$emit('close')" />
  </Transition>

  <Transition name="slide">
    <div
      v-if="open"
      class="fixed top-0 right-0 z-50 h-full w-80 bg-gray-900 border-l border-gray-800 flex flex-col shadow-2xl"
    >
      <div class="flex items-center justify-between px-5 py-4 border-b border-gray-800">
        <h2 class="font-semibold text-gray-100">Profile & Settings</h2>
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

      <div class="flex-1 overflow-y-auto px-5 py-6 space-y-6">
        <!-- Avatar -->
        <div class="flex justify-center">
          <div
            class="w-16 h-16 rounded-full bg-emerald-600/20 border-2 border-emerald-500 flex items-center justify-center text-2xl font-bold text-emerald-400 select-none"
          >
            {{ initials }}
          </div>
        </div>

        <!-- Profile -->
        <div class="space-y-3">
          <h3 class="text-xs uppercase tracking-wider text-gray-500 font-medium">Profile</h3>
          <div>
            <label class="block text-xs text-gray-400 mb-1">Name</label>
            <input
              v-model="settings.profile.name"
              type="text"
              placeholder="Your name"
              class="w-full bg-gray-800 border border-gray-700 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 text-gray-100"
            />
          </div>
          <div>
            <label class="block text-xs text-gray-400 mb-1">Email</label>
            <input
              v-model="settings.profile.email"
              type="email"
              placeholder="your@email.com"
              class="w-full bg-gray-800 border border-gray-700 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 text-gray-100"
            />
          </div>
        </div>

        <!-- Preferences -->
        <div class="space-y-3">
          <h3 class="text-xs uppercase tracking-wider text-gray-500 font-medium">Preferences</h3>
          <div>
            <label class="block text-xs text-gray-400 mb-1">Currency</label>
            <select
              v-model="settings.currency"
              @change="settings.save()"
              class="w-full bg-gray-800 border border-gray-700 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 text-gray-100"
            >
              <option v-for="c in settings.CURRENCIES" :key="c.code" :value="c.code">
                {{ c.code }} — {{ c.label }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <div class="px-5 py-4 border-t border-gray-800 space-y-2">
        <button
          @click="saveProfile"
          class="w-full py-2 bg-emerald-600 hover:bg-emerald-500 text-sm font-medium rounded-md transition-colors"
        >
          Save Profile
        </button>
        <button
          @click="auth.logout()"
          class="w-full py-2 bg-gray-800 hover:bg-gray-700 text-sm font-medium rounded-md text-gray-400 hover:text-red-400 transition-colors"
        >
          Sign out
        </button>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { computed, watch } from 'vue'
import { useSettingsStore } from '../stores/settingsStore.js'
import { useAuthStore } from '../stores/authStore.js'

defineProps({ open: { type: Boolean, required: true } })
defineEmits(['close'])

const settings = useSettingsStore()
const auth = useAuthStore()

// Pre-fill profile from Cognito on first open if fields are empty
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

function saveProfile() {
  settings.save()
}
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
