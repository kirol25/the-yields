<template>
  <div class="min-h-screen bg-gray-950 flex flex-col items-center justify-center px-4">
    <div class="text-center space-y-4">
      <p class="text-8xl font-bold text-gray-800">404</p>
      <h1 class="text-2xl font-semibold text-gray-100">{{ t('notFound.title') }}</h1>
      <p class="text-sm text-gray-500">{{ t('notFound.subtitle') }}</p>
      <RouterLink
        to="/"
        class="inline-block mt-2 px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-xl transition-colors"
      >
        {{ t('notFound.backHome') }}
      </RouterLink>
    </div>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
</script>
