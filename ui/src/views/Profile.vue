<template>
  <div class="max-w-lg space-y-6">
    <h1 class="text-2xl font-bold">{{ t('profile.title') }}</h1>

    <!-- Profile info -->
    <div class="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-5">
      <!-- Avatar -->
      <div class="flex items-center gap-4">
        <div
          class="w-14 h-14 rounded-full bg-emerald-600/20 border-2 border-emerald-500 flex items-center justify-center text-xl font-bold text-emerald-400 select-none shrink-0"
        >
          {{ initials }}
        </div>
        <div>
          <p class="text-sm font-medium text-gray-100">{{ settings.profile.name || t('profile.noName') }}</p>
          <p class="text-xs text-gray-500">{{ auth.user?.email || '—' }}</p>
        </div>
      </div>

      <hr class="border-gray-800" />

      <!-- Name -->
      <div>
        <label class="block text-xs text-gray-400 mb-1.5">{{ t('profile.name') }}</label>
        <input
          v-model="settings.profile.name"
          type="text"
          :placeholder="t('profile.namePlaceholder')"
          class="w-full bg-gray-800 border border-gray-700 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 text-gray-100"
        />
      </div>

      <!-- Email (read-only) -->
      <div>
        <label class="block text-xs text-gray-400 mb-1.5">{{ t('profile.email') }}</label>
        <div class="w-full bg-gray-800/50 border border-gray-700/50 rounded-md px-3 py-2 text-sm text-gray-500 flex items-center gap-2 select-none">
          <svg class="w-3.5 h-3.5 shrink-0 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path stroke-linecap="round" stroke-linejoin="round" d="M7 11V7a5 5 0 0 1 10 0v4"/>
          </svg>
          {{ auth.user?.email || settings.profile.email || '—' }}
        </div>
        <p class="text-xs text-gray-600 mt-1">{{ t('profile.emailManaged') }}</p>
      </div>

      <button
        @click="save"
        class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-sm font-medium rounded-md transition-colors"
      >
        {{ t('common.save') }}
      </button>

      <hr class="border-gray-800" />

      <!-- Change password toggle row -->
      <button
        @click="pw.open = !pw.open"
        class="w-full flex items-center justify-between text-sm text-gray-400 hover:text-gray-200 transition-colors group"
      >
        <span>{{ t('profile.changePassword') }}</span>
        <svg
          class="w-3.5 h-3.5 transition-transform duration-200"
          :class="pw.open ? 'rotate-180' : ''"
          fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"
        >
          <polyline points="6 9 12 15 18 9"/>
        </svg>
      </button>

      <!-- Change password fields (expandable) -->
      <div v-if="pw.open" class="space-y-4 pt-1">
        <div>
          <label class="block text-xs text-gray-400 mb-1.5">{{ t('profile.currentPassword') }}</label>
          <input
            v-model="pw.current"
            type="password"
            autocomplete="current-password"
            class="w-full bg-gray-800 border border-gray-700 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 text-gray-100"
          />
        </div>
        <div>
          <label class="block text-xs text-gray-400 mb-1.5">{{ t('profile.newPassword') }}</label>
          <input
            v-model="pw.next"
            type="password"
            autocomplete="new-password"
            class="w-full bg-gray-800 border border-gray-700 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 text-gray-100"
          />
        </div>
        <div>
          <label class="block text-xs text-gray-400 mb-1.5">{{ t('profile.confirmNewPassword') }}</label>
          <input
            v-model="pw.confirm"
            type="password"
            autocomplete="new-password"
            class="w-full bg-gray-800 border border-gray-700 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 text-gray-100"
          />
        </div>
        <p v-if="pw.error" class="text-xs text-red-400">{{ pw.error }}</p>
        <button
          @click="submitPasswordChange"
          :disabled="pw.loading"
          class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium rounded-md transition-colors"
        >
          {{ pw.loading ? t('profile.saving') : t('profile.changePassword') }}
        </button>
      </div>
    </div>

    <!-- Danger Zone -->
    <div class="border border-red-900/60 rounded-xl p-6 space-y-4">
      <h2 class="text-xs uppercase tracking-wider text-red-500 font-medium">{{ t('profile.dangerZone') }}</h2>

      <div class="flex items-start justify-between gap-4">
        <div>
          <p class="text-sm font-medium text-gray-200">{{ t('profile.deleteAccount') }}</p>
          <p class="text-xs text-gray-500 mt-0.5">{{ t('profile.deleteAccountDesc') }}</p>
        </div>
        <button
          v-if="!confirmingDelete"
          @click="confirmingDelete = true"
          class="shrink-0 px-3 py-1.5 border border-red-700 text-red-400 hover:bg-red-900/30 text-sm font-medium rounded-md transition-colors"
        >
          {{ t('profile.deleteAccount') }}
        </button>
      </div>

      <div v-if="confirmingDelete" class="bg-red-950/40 border border-red-900/50 rounded-lg p-4 space-y-3">
        <p class="text-sm text-red-300">{{ t('profile.confirmDelete') }}</p>
        <p v-if="deleteError" class="text-xs text-red-400">{{ deleteError }}</p>
        <div class="flex gap-2">
          <button
            @click="submitDeleteAccount"
            :disabled="deleting"
            class="px-3 py-1.5 bg-red-700 hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium rounded-md transition-colors"
          >
            {{ deleting ? t('profile.deleting') : t('profile.confirmDeleteBtn') }}
          </button>
          <button
            @click="confirmingDelete = false; deleteError = ''"
            :disabled="deleting"
            class="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-sm text-gray-300 font-medium rounded-md transition-colors"
          >
            {{ t('common.cancel') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useSettingsStore } from '../stores/settingsStore.js'
import { useAuthStore } from '../stores/authStore.js'
import { useToastStore } from '../stores/toastStore.js'

const { t } = useI18n()
const settings = useSettingsStore()
const auth = useAuthStore()
const toast = useToastStore()
const router = useRouter()

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
  toast.add(t('profile.saved'), 'success')
}

// Change password
const pw = reactive({ open: false, current: '', next: '', confirm: '', loading: false, error: '' })

async function submitPasswordChange() {
  pw.error = ''
  pw.success = false
  if (pw.next !== pw.confirm) {
    pw.error = t('profile.passwordMismatch')
    return
  }
  pw.loading = true
  try {
    await auth.changePassword(pw.current, pw.next)
    pw.current = ''
    pw.next = ''
    pw.confirm = ''
    pw.open = false
    toast.add(t('profile.passwordChanged'), 'success')
  } catch (e) {
    pw.error = e.message
  } finally {
    pw.loading = false
  }
}

// Delete account
const confirmingDelete = ref(false)
const deleting = ref(false)
const deleteError = ref('')

async function submitDeleteAccount() {
  deleteError.value = ''
  deleting.value = true
  try {
    await auth.deleteAccount()
    router.push('/login')
  } catch (e) {
    deleteError.value = e.message
    deleting.value = false
  }
}
</script>
