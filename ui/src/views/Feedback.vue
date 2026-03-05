<template>
  <div class="max-w-lg mx-auto space-y-6">
    <h1 class="text-2xl font-bold">{{ t('feedback.title') }}</h1>

    <!-- Success state -->
    <div v-if="submitted" class="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-4 text-center">
      <div class="w-12 h-12 rounded-full bg-emerald-600/20 border border-emerald-500/40 flex items-center justify-center mx-auto">
        <svg class="w-6 h-6 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
        </svg>
      </div>
      <div>
        <p class="font-medium text-gray-100">{{ t('feedback.successTitle') }}</p>
        <p class="text-sm text-gray-400 mt-1">{{ t('feedback.successSub') }}</p>
      </div>
      <button
        @click="reset"
        class="text-sm text-emerald-400 hover:text-emerald-300 transition-colors"
      >
        {{ t('feedback.sendAnother') }}
      </button>
    </div>

    <!-- Form -->
    <div v-else class="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-5">
      <p class="text-sm text-gray-400">{{ t('feedback.subtitle') }}</p>

      <!-- Category -->
      <div class="space-y-2">
        <label class="text-sm font-medium text-gray-300">{{ t('feedback.category') }}</label>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="cat in categories"
            :key="cat.value"
            @click="category = cat.value"
            :class="[
              'px-3 py-1.5 rounded-full text-xs font-medium transition-colors',
              category === cat.value
                ? 'bg-emerald-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700',
            ]"
          >
            {{ cat.label }}
          </button>
        </div>
      </div>

      <!-- Message -->
      <div class="space-y-2">
        <label class="text-sm font-medium text-gray-300">{{ t('feedback.message') }}</label>
        <textarea
          v-model="message"
          rows="5"
          :placeholder="t('feedback.messagePlaceholder')"
          class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 resize-none"
        />
      </div>

      <!-- Submit -->
      <div class="pt-1">
        <button
          @click="submit"
          :disabled="!message.trim() || submitting"
          :class="[
            'w-full px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
            message.trim() && !submitting
              ? 'bg-emerald-600 hover:bg-emerald-500 text-white'
              : 'bg-gray-700 text-gray-500 cursor-not-allowed',
          ]"
        >
          {{ submitting ? t('feedback.submitting') : t('feedback.submit') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import { API_BASE } from '../config.js'
import { useAuthStore } from '../stores/authStore.js'
import { useToastStore } from '../stores/toastStore.js'

const { t } = useI18n()
const auth = useAuthStore()
const toast = useToastStore()

const category = ref('feedback')
const message = ref('')
const submitting = ref(false)
const submitted = ref(false)

const categories = computed(() => [
  { value: 'feedback', label: t('feedback.categoryFeedback') },
  { value: 'bug',      label: t('feedback.categoryBug') },
  { value: 'feature',  label: t('feedback.categoryFeature') },
])

async function submit() {
  if (!message.value.trim() || submitting.value) return
  submitting.value = true
  try {
    await axios.post(
      `${API_BASE}/api/feedback`,
      { category: category.value, message: message.value },
      { headers: { 'X-User-Email': auth.user?.email ?? '' } },
    )
    submitted.value = true
  } catch {
    toast.add(t('feedback.submit') + ' failed. Please try again.', 'error')
  } finally {
    submitting.value = false
  }
}

function reset() {
  message.value = ''
  category.value = 'feedback'
  submitted.value = false
}
</script>
