<template>
  <div class="max-w-4xl mx-auto py-4 space-y-8 text-sm text-gray-300 leading-relaxed">
    <section
      v-if="missingFields.length"
      class="rounded-2xl border border-amber-500/30 bg-amber-500/10 px-4 py-4 text-amber-100"
    >
      <p class="font-semibold">{{ t('legalMeta.completeBeforeLaunch') }}</p>
      <p class="mt-2 text-sm text-amber-50/90">{{ missingFields.join(', ') }}</p>
      <p class="mt-2 text-xs text-amber-50/70">{{ t('legalMeta.updateIn') }}</p>
    </section>

    <h1 class="text-2xl font-bold text-gray-100">{{ t('privacyPage.title') }}</h1>

    <section class="space-y-2">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium">{{ t('privacyPage.controllerTitle') }}</h2>
      <p class="font-medium text-gray-100">{{ LEGAL.operatorName }}</p>
      <p>{{ address.street }}</p>
      <p>{{ address.cityLine }}</p>
      <p>{{ address.country }}</p>
      <p>
        {{ t('legalNoticePage.emailLabel') }}:
        <a :href="`mailto:${LEGAL.email}`" class="text-emerald-400 hover:text-emerald-300">
          {{ LEGAL.email }}
        </a>
      </p>
    </section>

    <section class="space-y-3">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium">{{ t('privacyPage.hostingTitle') }}</h2>
      <p>{{ t('privacyPage.hostingBody1') }}</p>
      <p>{{ t('privacyPage.hostingBody2') }}</p>
    </section>

    <section class="space-y-3">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium">{{ t('privacyPage.accountTitle') }}</h2>
      <p>{{ t('privacyPage.accountBody1') }}</p>
      <p>{{ t('privacyPage.accountBody2') }}</p>
      <p>{{ t('privacyPage.accountBody3') }}</p>
      <p>{{ t('privacyPage.accountBody4') }}</p>
    </section>

    <section class="space-y-3">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium">{{ t('privacyPage.feedbackTitle') }}</h2>
      <p>{{ t('privacyPage.feedbackBody1') }}</p>
      <p>{{ t('privacyPage.feedbackBody2') }}</p>
    </section>

    <section class="space-y-3">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium">{{ t('privacyPage.processorsTitle') }}</h2>
      <ul class="space-y-2">
        <li class="flex gap-2"><span class="text-emerald-400 shrink-0">→</span><span>{{ t('privacyPage.processorIonos') }}</span></li>
        <li class="flex gap-2"><span class="text-emerald-400 shrink-0">→</span><span>{{ t('privacyPage.processorAws') }}</span></li>
      </ul>
    </section>

    <section class="space-y-3">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium">{{ t('privacyPage.transfersTitle') }}</h2>
      <p>{{ t('privacyPage.transfersBody') }}</p>
    </section>

    <section class="space-y-3">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium">{{ t('privacyPage.retentionTitle') }}</h2>
      <ul class="space-y-2 pl-5 list-disc text-gray-400">
        <li><span class="text-gray-300">{{ t('privacyPage.retention1') }}</span></li>
        <li><span class="text-gray-300">{{ t('privacyPage.retention2') }}</span></li>
        <li><span class="text-gray-300">{{ t('privacyPage.retention3') }}</span></li>
        <li><span class="text-gray-300">{{ t('privacyPage.retention5') }}</span></li>
      </ul>
    </section>

    <section class="space-y-3">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium">{{ t('privacyPage.storageTitle') }}</h2>
      <p>{{ t('privacyPage.storageBody1') }}</p>
      <ul class="space-y-2 pl-5 list-disc text-gray-400">
        <li><span class="text-gray-300">{{ t('privacyPage.storageItem1') }}</span></li>
        <li><span class="text-gray-300">{{ t('privacyPage.storageItem2') }}</span></li>
      </ul>
      <p>{{ t('privacyPage.storageBody2') }}</p>
    </section>

    <section class="space-y-3">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium">{{ t('privacyPage.rightsTitle') }}</h2>
      <ul class="space-y-2">
        <li class="flex gap-2"><span class="text-emerald-400 shrink-0">→</span><span>{{ t('privacyPage.rights1') }}</span></li>
        <li class="flex gap-2"><span class="text-emerald-400 shrink-0">→</span><span>{{ t('privacyPage.rights2') }}</span></li>
        <li class="flex gap-2"><span class="text-emerald-400 shrink-0">→</span><span>{{ t('privacyPage.rights3') }}</span></li>
        <li class="flex gap-2"><span class="text-emerald-400 shrink-0">→</span><span>{{ t('privacyPage.rights4') }}</span></li>
        <li class="flex gap-2"><span class="text-emerald-400 shrink-0">→</span><span>{{ t('privacyPage.rights5') }}</span></li>
        <li class="flex gap-2"><span class="text-emerald-400 shrink-0">→</span><span>{{ t('privacyPage.rights6') }}</span></li>
        <li class="flex gap-2"><span class="text-emerald-400 shrink-0">→</span><span>{{ t('privacyPage.rights7') }}</span></li>
      </ul>
      <p>
        {{ t('privacyPage.rightsBody') }}
        <a :href="`mailto:${LEGAL.email}`" class="text-emerald-400 hover:text-emerald-300">
          {{ LEGAL.email }}
        </a>.
      </p>
    </section>

    <section class="space-y-3">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium">{{ t('privacyPage.objectionTitle') }}</h2>
      <p>{{ t('privacyPage.objectionBody') }}</p>
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
  street: '[Street]',
  postalCode: '[Postal Code]',
  city: '[City]',
  country: 'Deutschland',
  email: '[your-email@example.com]',
  lastUpdatedDe: '[Datum]',
  lastUpdatedEn: '[Date]',
}

function getLegalAddress(locale) {
  const de = locale === 'de'
  return {
    street: LEGAL.street || (de ? '[Strasse und Hausnummer]' : '[Street and house number]'),
    cityLine: LEGAL.postalCode && LEGAL.city ? `${LEGAL.postalCode} ${LEGAL.city}` : (de ? '[PLZ] [Ort]' : '[Postal code] [City]'),
    country: LEGAL.country || (de ? 'Deutschland' : 'Germany'),
  }
}

function getMissingLegalFields(locale) {
  const de = locale === 'de'
  const fields = [
    { key: 'street', labelDe: 'Strasse und Hausnummer', labelEn: 'Street and house number' },
    { key: 'postalCode', labelDe: 'Postleitzahl', labelEn: 'Postal code' },
    { key: 'city', labelDe: 'Ort', labelEn: 'City' },
  ]
  return fields
    .filter(({ key }) => !String(LEGAL[key] || '').trim() || LEGAL[key].startsWith('['))
    .map(({ labelDe, labelEn }) => (de ? labelDe : labelEn))
}

const { t, locale } = useI18n()
const address = computed(() => getLegalAddress(locale.value))
const missingFields = computed(() => getMissingLegalFields(locale.value))
const lastUpdated = computed(() => (locale.value === 'de' ? LEGAL.lastUpdatedDe : LEGAL.lastUpdatedEn))
</script>
