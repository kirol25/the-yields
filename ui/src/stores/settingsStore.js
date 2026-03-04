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
  const theme = ref(saved.theme || 'dark')
  const dividendGoal      = ref(typeof saved.dividendGoal      === 'object' && saved.dividendGoal      !== null ? saved.dividendGoal      : {})
  const steuerfreibetrag  = ref(typeof saved.steuerfreibetrag  === 'object' && saved.steuerfreibetrag  !== null ? saved.steuerfreibetrag  : {})

  function setLocale(code) {
    locale.value = code
    i18n.global.locale.value = code
    save()
  }

  const _mq = window.matchMedia('(prefers-color-scheme: light)')
  let _mqListener = null

  function _applyTheme(t) {
    const isLight = t === 'light' || (t === 'system' && _mq.matches)
    document.documentElement.classList.toggle('light', isLight)
  }

  function setTheme(t) {
    theme.value = t
    // Remove previous system listener if any
    if (_mqListener) {
      _mq.removeEventListener('change', _mqListener)
      _mqListener = null
    }
    if (t === 'system') {
      _mqListener = (e) => document.documentElement.classList.toggle('light', e.matches)
      _mq.addEventListener('change', _mqListener)
    }
    _applyTheme(t)
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
        theme: theme.value,
        dividendGoal:     dividendGoal.value,
        steuerfreibetrag: steuerfreibetrag.value,
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

  function setDividendGoal(year, amount) {
    dividendGoal.value = { ...dividendGoal.value, [year]: amount }
    save()
  }

  function setSteuerfreibetrag(year, amount) {
    steuerfreibetrag.value = { ...steuerfreibetrag.value, [year]: Math.min(amount, 2000) }
    save()
  }

  return { profile, currency, locale, theme, dividendGoal, steuerfreibetrag, CURRENCIES, LANGUAGES, save, setLocale, setTheme, setDividendGoal, setSteuerfreibetrag, fmt }
})
