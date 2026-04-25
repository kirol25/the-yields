<template>
  <div class="max-w-4xl mx-auto py-4 space-y-8 text-sm text-gray-300 leading-relaxed">
    <h1 class="text-2xl font-bold text-gray-100">{{ t('termsPage.title') }}</h1>

    <section class="space-y-3">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium">{{ t('termsPage.scopeTitle') }}</h2>
      <p>{{ t('termsPage.scopeBody', legalVars) }}</p>
    </section>

    <section class="space-y-3">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium">{{ t('termsPage.accountTitle') }}</h2>
      <p>{{ t('termsPage.accountBody') }}</p>
    </section>

    <section class="space-y-3">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium">{{ t('termsPage.serviceTitle') }}</h2>
      <p>{{ t('termsPage.serviceBody', legalVars) }}</p>
    </section>

    <section class="space-y-3">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium">{{ t('termsPage.permittedTitle') }}</h2>
      <p>{{ t('termsPage.permittedBody') }}</p>
    </section>

    <section class="space-y-3">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium">{{ t('termsPage.noAdviceTitle') }}</h2>
      <p>{{ t('termsPage.noAdviceBody', legalVars) }}</p>
    </section>

    <section class="space-y-3">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium">{{ t('termsPage.availabilityTitle') }}</h2>
      <p>{{ t('termsPage.availabilityBody') }}</p>
    </section>

    <section class="space-y-3">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium">{{ t('termsPage.liabilityTitle') }}</h2>
      <p>{{ t('termsPage.liabilityBody') }}</p>
    </section>

    <section class="space-y-3">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium">{{ t('termsPage.terminationTitle') }}</h2>
      <p>{{ t('termsPage.terminationBody') }}</p>
    </section>

    <section class="space-y-3">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium">{{ t('termsPage.privacyTitle') }}</h2>
      <p>
        {{ t('termsPage.privacyBody') }}
        <RouterLink to="/datenschutz" class="text-emerald-400 hover:text-emerald-300">
          {{ t('termsPage.privacyLink') }}
        </RouterLink>.
      </p>
    </section>

    <section class="space-y-3">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium">{{ t('termsPage.lawTitle') }}</h2>
      <p>{{ t('termsPage.lawBody') }}</p>
    </section>

    <p class="text-xs text-gray-600 pt-4 border-t border-gray-800">
      {{ t('legalMeta.lastUpdated', { date: lastUpdated }) }}
    </p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { APP_NAME } from '../config.js'

const LEGAL = {
  appName: APP_NAME,
  operatorName: '[Your Name]',
  lastUpdatedDe: '[Datum]',
  lastUpdatedEn: '[Date]',
}

const { t, locale } = useI18n()
const lastUpdated = computed(() => (locale.value === 'de' ? LEGAL.lastUpdatedDe : LEGAL.lastUpdatedEn))
const legalVars = computed(() => ({
  appName: LEGAL.appName,
  operatorName: LEGAL.operatorName,
}))
</script>
