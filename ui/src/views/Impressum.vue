<template>
  <div class="max-w-3xl mx-auto py-4 space-y-8 text-sm text-gray-300 leading-relaxed">
    <section
      v-if="missingFields.length"
      class="rounded-2xl border border-amber-500/30 bg-amber-500/10 px-4 py-4 text-amber-100"
    >
      <p class="font-semibold">{{ t('legalMeta.completeBeforeLaunch') }}</p>
      <p class="mt-2 text-sm text-amber-50/90">{{ missingFields.join(', ') }}</p>
      <p class="mt-2 text-xs text-amber-50/70">{{ t('legalMeta.updateIn') }}</p>
    </section>

    <h1 class="text-2xl font-bold text-gray-100">{{ t('legalNoticePage.title') }}</h1>

    <section class="space-y-2">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium">{{ t('legalNoticePage.noticeTitle') }}</h2>
      <p class="font-medium text-gray-100">{{ LEGAL.operatorName }}</p>
      <p>{{ address.street }}</p>
      <p>{{ address.cityLine }}</p>
      <p>{{ address.country }}</p>
    </section>

    <section class="space-y-2">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium">{{ t('legalNoticePage.contactTitle') }}</h2>
      <p>
        {{ t('legalNoticePage.emailLabel') }}:
        <a :href="`mailto:${LEGAL.email}`" class="text-emerald-400 hover:text-emerald-300">
          {{ LEGAL.email }}
        </a>
      </p>
      <p v-if="LEGAL.phone">{{ t('legalNoticePage.phoneLabel') }}: {{ LEGAL.phone }}</p>
    </section>

    <section v-if="LEGAL.vatId || LEGAL.commercialRegister" class="space-y-2">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium">{{ t('legalNoticePage.additionalTitle') }}</h2>
      <p v-if="LEGAL.vatId">{{ t('legalNoticePage.vatLabel') }}: {{ LEGAL.vatId }}</p>
      <p v-if="LEGAL.commercialRegister">{{ t('legalNoticePage.registerLabel') }}: {{ LEGAL.commercialRegister }}</p>
    </section>

    <section class="space-y-2">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium">{{ t('legalNoticePage.responsibleTitle') }}</h2>
      <p>{{ LEGAL.responsibleForContent }}</p>
      <p>{{ address.street }}</p>
      <p>{{ address.cityLine }}</p>
    </section>

    <section class="space-y-3">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium">{{ t('legalNoticePage.disputeTitle') }}</h2>
      <p>{{ t('legalNoticePage.disputeBody') }}</p>
      <p class="text-gray-400">{{ t('legalNoticePage.odrNote') }}</p>
    </section>

    <p class="text-xs text-gray-600 pt-4 border-t border-gray-800">
      {{ t('legalMeta.lastUpdated', { date: lastUpdated }) }}
    </p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { LEGAL, getLegalAddress, getMissingLegalFields } from '../legal.js'

const { t, locale } = useI18n()
const address = computed(() => getLegalAddress(locale.value))
const missingFields = computed(() => getMissingLegalFields(locale.value))
const lastUpdated = computed(() => (locale.value === 'de' ? LEGAL.lastUpdatedDe : LEGAL.lastUpdatedEn))
</script>
