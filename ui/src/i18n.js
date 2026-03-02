import { createI18n } from 'vue-i18n'
import en from './locales/en.json'
import de from './locales/de.json'

const saved = JSON.parse(localStorage.getItem('yield-settings') || '{}')
const defaultLocale = saved.locale || 'de'

export const i18n = createI18n({
  legacy: false,
  locale: defaultLocale,
  fallbackLocale: 'en',
  messages: { en, de },
})
