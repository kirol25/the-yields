export const SUPPORTED_LOCALES = ['de', 'en']

export function getLocaleFromPath(path = '') {
  const match = path.match(/^\/(de|en)(?:\/|$)/)
  return match?.[1] ?? null
}

export function stripLocalePrefix(path = '') {
  const stripped = path.replace(/^\/(de|en)(?=\/|$)/, '')
  return stripped || '/'
}

export function localizePath(path = '/', locale = 'de') {
  const normalizedLocale = SUPPORTED_LOCALES.includes(locale) ? locale : 'de'
  const normalizedPath = stripLocalePrefix(path)
  return normalizedPath === '/' ? `/${normalizedLocale}` : `/${normalizedLocale}${normalizedPath}`
}
