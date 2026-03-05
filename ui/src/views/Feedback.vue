<template>
  <div class="max-w-lg mx-auto space-y-6">
    <h1 class="text-2xl font-bold">{{ t('feedback.title') }}</h1>

    <div class="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-5">
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
          class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 resize-none"
        />
      </div>

      <!-- Submit -->
      <a
        :href="mailtoHref"
        :class="[
          'block w-full text-center px-4 py-2 text-sm font-medium rounded-lg transition-colors',
          message.trim()
            ? 'bg-emerald-600 hover:bg-emerald-500 text-white'
            : 'bg-gray-700 text-gray-500 pointer-events-none',
        ]"
      >
        {{ t('feedback.submit') }}
      </a>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const category = ref('feedback')
const message = ref('')

const categories = computed(() => [
  { value: 'feedback', label: t('feedback.categoryFeedback') },
  { value: 'bug',      label: t('feedback.categoryBug') },
  { value: 'feature',  label: t('feedback.categoryFeature') },
])

const mailtoHref = computed(() => {
  const subject = encodeURIComponent(`[${category.value}] the-yield`)
  const body = encodeURIComponent(message.value)
  return `mailto:contact@the-yield.app?subject=${subject}&body=${body}`
})
</script>
