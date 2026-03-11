import { defineStore } from 'pinia'
import { ref } from 'vue'
import { i18n } from '../i18n.js'
import client from '../api/client.js'

const STORAGE_KEY = 'yield-settings'
const SAVE_DEBOUNCE_MS = 800

function debounce(fn, delay) {
  let timer
  return (...args) => {
    clearTimeout(timer)
    timer = setTimeout(() => fn(...args), delay)
  }
}

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
  const dividendGoal     = ref(typeof saved.dividendGoal     === 'object' && saved.dividendGoal     !== null ? saved.dividendGoal     : {})
  const yieldGoal        = ref(typeof saved.yieldGoal        === 'object' && saved.yieldGoal        !== null ? saved.yieldGoal        : {})
  const steuerfreibetrag = ref(typeof saved.steuerfreibetrag === 'object' && saved.steuerfreibetrag !== null ? saved.steuerfreibetrag : {})

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
        yieldGoal:        yieldGoal.value,
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

  async function _saveToServer() {
    try {
      await client.put('/api/settings', {
        dividendGoal: dividendGoal.value,
        yieldGoal: yieldGoal.value,
        steuerfreibetrag: steuerfreibetrag.value,
      })
    } catch (e) {
      console.error('[settings] server sync failed — local values kept:', e)
    }
  }

  const _debouncedSaveToServer = debounce(_saveToServer, SAVE_DEBOUNCE_MS)

  async function loadFromServer() {
    try {
      const { data } = await client.get('/api/settings')
      if (data.dividendGoal     && typeof data.dividendGoal     === 'object') dividendGoal.value     = data.dividendGoal
      if (data.yieldGoal        && typeof data.yieldGoal        === 'object') yieldGoal.value        = data.yieldGoal
      if (data.steuerfreibetrag && typeof data.steuerfreibetrag === 'object') steuerfreibetrag.value = data.steuerfreibetrag
      save()
    } catch (e) {
      console.error('[settings] failed to load from server — using local values:', e)
    }
  }

  function setDividendGoal(year, amount) {
    dividendGoal.value = { ...dividendGoal.value, [year]: Math.max(amount, 0) }
    save()
    _debouncedSaveToServer()
  }

  function setYieldGoal(year, amount) {
    yieldGoal.value = { ...yieldGoal.value, [year]: Math.max(amount, 0) }
    save()
    _debouncedSaveToServer()
  }

  function setSteuerfreibetrag(year, amount) {
    steuerfreibetrag.value = { ...steuerfreibetrag.value, [year]: Math.min(Math.max(amount, 0), 2000) }
    save()
    _debouncedSaveToServer()
  }

  return { profile, currency, locale, theme, dividendGoal, yieldGoal, steuerfreibetrag, CURRENCIES, LANGUAGES, save, setLocale, setTheme, setDividendGoal, setYieldGoal, setSteuerfreibetrag, fmt, loadFromServer }
})
