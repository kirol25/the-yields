<template>
  <div class="max-w-2xl mx-auto py-4 space-y-8 text-sm text-gray-300 leading-relaxed">
    <h1 class="text-2xl font-bold text-gray-100">{{ t('terms.title') }}</h1>

    <section class="space-y-3">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium mb-3">{{ t('terms.acceptanceTitle') }}</h2>
      <p>{{ t('terms.acceptanceBody') }}</p>
    </section>

    <section class="space-y-3">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium mb-3">{{ t('terms.useTitle') }}</h2>
      <p>{{ t('terms.useBody') }}</p>
    </section>

    <section class="space-y-3">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium mb-3">{{ t('terms.noAdviceTitle') }}</h2>
      <p>{{ t('terms.noAdviceBody') }}</p>
    </section>

    <section class="space-y-3">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium mb-3">{{ t('terms.dataTitle') }}</h2>
      <p>{{ t('terms.dataBody') }}</p>
    </section>

    <section class="space-y-3">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium mb-3">{{ t('terms.changesTitle') }}</h2>
      <p>{{ t('terms.changesBody') }}</p>
    </section>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
</script>
