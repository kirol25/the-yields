import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { i18n } from '../i18n.js'
import { useToastStore } from './toastStore.js'
import { useSettingsStore } from './settingsStore.js'
import { API_BASE } from '../config.js'

const REGION = import.meta.env.VITE_COGNITO_REGION
const CLIENT_ID = import.meta.env.VITE_COGNITO_CLIENT_ID

function parseIdToken(token) {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return {
      name: payload.preferred_username || payload.email || '',
      email: payload.email || '',
      sub: payload.sub || '',
    }
  } catch {
    return null
  }
}

async function cognitoRequest(action, body) {
  const res = await fetch(`https://cognito-idp.${REGION}.amazonaws.com/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-amz-json-1.1',
      'X-Amz-Target': `AWSCognitoIdentityProviderService.${action}`,
    },
    body: JSON.stringify(body),
  })

  // Some Cognito operations (e.g. DeleteUser) return an empty body on success.
  // res.json() on an empty body throws SyntaxError in WebKit — treat that as {}
  // if the status is OK, otherwise surface a generic failure.
  let data = {}
  try {
    data = await res.json()
  } catch {
    if (!res.ok) throw new Error('Cognito request failed')
    return {}
  }

  if (!res.ok) {
    const err = new Error(data.message ?? 'Cognito request failed')
    err.type = data.__type ?? 'UnknownError'
    throw err
  }
  return data
}

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem('access_token'))
  const idToken = ref(localStorage.getItem('id_token'))
  const refreshToken = ref(localStorage.getItem('refresh_token'))
  const pendingEmail = ref(sessionStorage.getItem('pending_email') ?? '')

  const isAuthenticated = computed(() => !!accessToken.value)
  const user = computed(() => (idToken.value ? parseIdToken(idToken.value) : null))

  function setTokens({ AccessToken, IdToken, RefreshToken }) {
    accessToken.value = AccessToken
    idToken.value = IdToken
    if (RefreshToken) refreshToken.value = RefreshToken
    localStorage.setItem('access_token', AccessToken)
    localStorage.setItem('id_token', IdToken)
    if (RefreshToken) localStorage.setItem('refresh_token', RefreshToken)
  }

  async function signUp(email, password, name) {
    await cognitoRequest('SignUp', {
      ClientId: CLIENT_ID,
      Username: email,
      Password: password,
      UserAttributes: [
        { Name: 'email', Value: email },
        { Name: 'preferred_username', Value: name },
      ],
    })
    pendingEmail.value = email
    sessionStorage.setItem('pending_email', email)
  }

  async function confirmSignUp(email, code) {
    await cognitoRequest('ConfirmSignUp', {
      ClientId: CLIENT_ID,
      Username: email,
      ConfirmationCode: code,
    })
    sessionStorage.removeItem('pending_email')
    pendingEmail.value = ''
  }

  async function resendCode(email) {
    await cognitoRequest('ResendConfirmationCode', {
      ClientId: CLIENT_ID,
      Username: email,
    })
  }

  async function signIn(email, password) {
    const data = await cognitoRequest('InitiateAuth', {
      AuthFlow: 'USER_PASSWORD_AUTH',
      ClientId: CLIENT_ID,
      AuthParameters: {
        USERNAME: email,
        PASSWORD: password,
      },
    })
    setTokens(data.AuthenticationResult)
  }

  function isExpiredTokenError(err) {
    return (
      err.type === 'NotAuthorizedException' &&
      err.message?.toLowerCase().includes('expired')
    )
  }

  function isTokenExpired() {
    if (!accessToken.value) return true
    try {
      const { exp } = JSON.parse(atob(accessToken.value.split('.')[1]))
      return Date.now() / 1000 >= exp - 30 // 30s buffer
    } catch {
      return true
    }
  }

  async function refreshSession() {
    if (!refreshToken.value) throw new Error('No refresh token')
    const data = await cognitoRequest('InitiateAuth', {
      AuthFlow: 'REFRESH_TOKEN_AUTH',
      ClientId: CLIENT_ID,
      AuthParameters: { REFRESH_TOKEN: refreshToken.value },
    })
    setTokens(data.AuthenticationResult)
  }

  // Returns true if the token is (now) valid, false if the session was terminated.
  async function ensureValidToken() {
    if (!isTokenExpired()) return true
    try {
      await refreshSession()
      return true
    } catch {
      await logout()
      useToastStore().add(i18n.global.t('common.sessionExpired'), 'error')
      return false
    }
  }

  // Returns true if refreshed, false if session was terminated.
  async function handleExpiredSession() {
    try {
      await refreshSession()
      return true
    } catch {
      await logout()
      useToastStore().add(i18n.global.t('common.sessionExpired'), 'error')
      return false
    }
  }

  async function changePassword(oldPassword, newPassword) {
    const doChange = () =>
      cognitoRequest('ChangePassword', {
        AccessToken: accessToken.value,
        PreviousPassword: oldPassword,
        ProposedPassword: newPassword,
      })
    try {
      await doChange()
    } catch (err) {
      if (!isExpiredTokenError(err)) throw err
      const refreshed = await handleExpiredSession()
      if (refreshed) await doChange()
    }
  }

  async function forgotPassword(email) {
    await cognitoRequest('ForgotPassword', { ClientId: CLIENT_ID, Username: email })
  }

  async function resetPassword(email, code, newPassword) {
    await cognitoRequest('ConfirmForgotPassword', {
      ClientId: CLIENT_ID,
      Username: email,
      ConfirmationCode: code,
      Password: newPassword,
    })
  }

  function clearTokens() {
    accessToken.value = null
    idToken.value = null
    refreshToken.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('id_token')
    localStorage.removeItem('refresh_token')
    // Clear user-specific profile so the next account starts fresh
    const settings = useSettingsStore()
    settings.profile.name = ''
    settings.profile.email = ''
    settings.save()
  }

  async function deleteAccount() {
    // Best-effort: wipe backend data. Never block account deletion on this.
    try {
      await fetch(`${API_BASE}/api/data`, {
        method: 'DELETE',
        headers: { 'X-User-Email': user.value?.email ?? '' },
      })
    } catch {
      // network error or backend unreachable — proceed anyway
    }

    // Delete the Cognito account
    const doDelete = () => cognitoRequest('DeleteUser', { AccessToken: accessToken.value })
    try {
      await doDelete()
    } catch (err) {
      if (!isExpiredTokenError(err)) throw err
      const refreshed = await handleExpiredSession()
      if (!refreshed) return
      await doDelete()
    }

    // Account is gone — clear tokens directly without GlobalSignOut
    clearTokens()
  }

  async function logout() {
    try {
      if (accessToken.value) {
        await cognitoRequest('GlobalSignOut', { AccessToken: accessToken.value })
      }
    } catch {
      // best-effort — clear local state regardless
    }
    clearTokens()
  }

  return {
    isAuthenticated,
    user,
    pendingEmail,
    signUp,
    confirmSignUp,
    resendCode,
    signIn,
    logout,
    changePassword,
    forgotPassword,
    resetPassword,
    deleteAccount,
    refreshSession,
    ensureValidToken,
  }
})
