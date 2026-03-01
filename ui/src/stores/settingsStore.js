import { defineStore } from 'pinia'
import { ref } from 'vue'

const STORAGE_KEY = 'yield-settings'

export const useSettingsStore = defineStore('settings', () => {
  const CURRENCIES = [
    { code: 'USD', label: 'US Dollar' },
    { code: 'EUR', label: 'Euro' },
    { code: 'GBP', label: 'British Pound' },
  ]

  const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}')

  const profile = ref({ name: saved.name || '', email: saved.email || '' })
  const currency = ref(saved.currency || 'USD')

  function save() {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        name: profile.value.name,
        email: profile.value.email,
        currency: currency.value,
      }),
    )
  }

  function fmt(amount) {
    const isJpy = currency.value === 'JPY'
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency.value,
      minimumFractionDigits: isJpy ? 0 : 2,
      maximumFractionDigits: isJpy ? 0 : 2,
    }).format(amount)
  }

  return { profile, currency, CURRENCIES, save, fmt }
})
