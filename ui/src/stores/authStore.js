import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { i18n } from '../i18n.js'
import { useToastStore } from './toastStore.js'

const REGION = import.meta.env.VITE_COGNITO_REGION
const CLIENT_ID = import.meta.env.VITE_COGNITO_CLIENT_ID

function parseIdToken(token) {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return {
      name: payload.name ?? payload['cognito:username'] ?? payload.email ?? '',
      email: payload.email ?? '',
      sub: payload.sub ?? '',
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

  const data = await res.json()
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

  async function signUp(email, password) {
    await cognitoRequest('SignUp', {
      ClientId: CLIENT_ID,
      Username: email,
      Password: password,
      UserAttributes: [{ Name: 'email', Value: email }],
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

  async function handleExpiredSession() {
    await logout()
    useToastStore().add(i18n.global.t('common.sessionExpired'), 'error')
  }

  async function changePassword(oldPassword, newPassword) {
    try {
      await cognitoRequest('ChangePassword', {
        AccessToken: accessToken.value,
        PreviousPassword: oldPassword,
        ProposedPassword: newPassword,
      })
    } catch (err) {
      if (isExpiredTokenError(err)) {
        await handleExpiredSession()
        return
      }
      throw err
    }
  }

  async function deleteAccount() {
    try {
      await cognitoRequest('DeleteUser', { AccessToken: accessToken.value })
    } catch (err) {
      if (isExpiredTokenError(err)) {
        await handleExpiredSession()
        return
      }
      throw err
    }
    await logout()
  }

  async function logout() {
    try {
      if (accessToken.value) {
        await cognitoRequest('GlobalSignOut', { AccessToken: accessToken.value })
      }
    } catch {
      // best-effort — clear local state regardless
    }
    accessToken.value = null
    idToken.value = null
    refreshToken.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('id_token')
    localStorage.removeItem('refresh_token')

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
    deleteAccount,
  }
})
