import axios from 'axios'
import { ref } from 'vue'
import { baseUrl, useDataStore } from '@/stores/counter'
import { notification } from '@/utils/notification'

export const ADMIN_ACCESS_CHECK_INTERVAL = 600000

let pendingCheck
const unavailableToken = ref(null)

export function adminAccessUnavailable(token) {
  return unavailableToken.value === token
}

export function isAdminAccessDenied(error) {
  const status = error.response?.status
  return status === 401 || status === 403
}

export function checkAdminAccess(token) {
  if (pendingCheck?.token === token) return pendingCheck.request

  const request = axios.get(`${baseUrl}api/admin/profile`, {
    headers: { Authorization: `Bearer ${token}`, 'Cache-Control': 'no-cache' },
    timeout: 5000,
    adminAccessCheck: true,
  }).then(response => {
    if (unavailableToken.value === token) unavailableToken.value = null
    return response
  }).catch(error => {
    if (!isAdminAccessDenied(error) && useDataStore().auth_key === token) {
      unavailableToken.value = token
    }
    throw error
  }).finally(() => {
    if (pendingCheck?.request === request) pendingCheck = undefined
  })

  pendingCheck = { token, request }
  return request
}

export function closeAdminSession(store, status) {
  store.clearTokenRole()
  const message = status === 403
    ? 'Доступ к админке отозван. Войдите снова.'
    : 'Сессия истекла. Пожалуйста, войдите снова.'
  notification(message, 'negative')
}
