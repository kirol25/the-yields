import { defineStore } from 'pinia'
import { ref } from 'vue'
import { i18n } from '../i18n.js'

const STORAGE_KEY = 'yield-settings'

export const useSettingsStore = defineStore('settings', () => {
  const CURRENCIES = [
    { code: 'USD', label: 'US Dollar' },
    { code: 'EUR', label: 'Euro' },
    { code: 'GBP', label: 'British Pound' },
  ]

  const LANGUAGES = [
    { code: 'de', label: 'Deutsch' },
    { code: 'en', label: 'English' },
  ]

  const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}')

  const profile = ref({ name: saved.name || '', email: saved.email || '' })
  const currency = ref(saved.currency || 'USD')
  const locale = ref(saved.locale || 'de')

  function setLocale(code) {
    locale.value = code
    i18n.global.locale.value = code
    save()
  }

  function save() {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        name: profile.value.name,
        email: profile.value.email,
        currency: currency.value,
        locale: locale.value,
      }),
    )
  }

  function fmt(amount) {
    const isJpy = currency.value === 'JPY'
    return new Intl.NumberFormat(locale.value, {
      style: 'currency',
      currency: currency.value,
      minimumFractionDigits: isJpy ? 0 : 2,
      maximumFractionDigits: isJpy ? 0 : 2,
    }).format(amount)
  }

  return { profile, currency, locale, CURRENCIES, LANGUAGES, save, setLocale, fmt }
})
