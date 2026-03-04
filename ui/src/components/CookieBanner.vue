<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-transform duration-300 ease-out"
      enter-from-class="translate-y-full"
      enter-to-class="translate-y-0"
      leave-active-class="transition-transform duration-200 ease-in"
      leave-from-class="translate-y-0"
      leave-to-class="translate-y-full"
    >
      <div
        v-if="visible"
        class="fixed bottom-0 inset-x-0 z-50 bg-gray-900 border-t border-gray-800 px-6 py-4"
      >
        <div class="max-w-7xl mx-auto flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <p class="text-sm text-gray-400 leading-relaxed">
            {{ t('cookie.message') }}
          </p>
          <button
            @click="accept"
            class="shrink-0 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-lg transition-colors"
          >
            {{ t('cookie.accept') }}
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const visible = ref(localStorage.getItem('cookie-consent') !== 'accepted')

function accept() {
  localStorage.setItem('cookie-consent', 'accepted')
  visible.value = false
}
</script>
