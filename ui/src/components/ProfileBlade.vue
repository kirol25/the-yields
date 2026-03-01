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
            <div class="w-full bg-gray-800/50 border border-gray-700/50 rounded-md px-3 py-2 text-sm text-gray-500 flex items-center gap-2 select-none">
              <svg class="w-3 h-3 shrink-0 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path stroke-linecap="round" stroke-linejoin="round" d="M7 11V7a5 5 0 0 1 10 0v4"/>
              </svg>
              {{ auth.user?.email || settings.profile.email || '—' }}
            </div>
          </div>
        </div>

        <!-- Preferences -->
        <div class="space-y-3">
          <h3 class="text-xs uppercase tracking-wider text-gray-500 font-medium">Preferences</h3>
          <div>
            <label class="block text-xs text-gray-400 mb-1">Currency</label>
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
import { computed, ref, watch } from 'vue'
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

// Currency dropdown
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
