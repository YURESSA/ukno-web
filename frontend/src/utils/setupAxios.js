import axios from 'axios'
import { useDataStore } from '@/stores/counter'
import router from '@/router'
import { notification } from '@/utils/notification'
import { getApiErrorMessage } from '@/utils/apiError'
import { checkAdminAccess, closeAdminSession } from '@/utils/adminAccess'

let isHandling401 = false

export function setupAxiosInterceptors() {
  axios.interceptors.response.use(
    (response) => {
      const authorization = response.config?.headers?.Authorization
      if (authorization && authorization !== `Bearer ${useDataStore().auth_key}`) {
        return Promise.reject(new axios.CanceledError('Session changed'))
      }
      return response
    },
    (error) => {
      if (axios.isCancel(error)) return Promise.reject(error)
      const originalMessage = error.response?.data?.message || error.response?.data?.msg
      const errorMessage = getApiErrorMessage(error)
      if (error.response && error.response.data && typeof error.response.data === 'object') {
        error.response.data.message = errorMessage
      }
      const status = error.response?.status
      const authorization = error.config?.headers?.Authorization
      const store = authorization ? useDataStore() : null
      if (status === 403 && store?.role === 'admin' && authorization === `Bearer ${store.auth_key}`) {
        if (error.config.adminAccessCheck) {
          closeAdminSession(store, status)
          if (router.currentRoute.value.path !== '/login') router.replace('/login')
        } else if (router.currentRoute.value.meta.requiredRole === 'admin') {
          checkAdminAccess(store.auth_key).catch(() => {})
        }
      }

      const authenticated = Boolean(authorization)
      const invalidJwt = status === 422 && /token|signature|segments|jwt|header|padding|subject|claim|\balg\b|алгоритм|токен/i.test(originalMessage || '')
      const wrongCurrentPassword = error.config?.passwordChange && originalMessage === 'Неверный текущий пароль'
      if (authenticated && ((status === 401 && !wrongCurrentPassword) || invalidJwt)) {
        const isLoginRequest = error.config?.url?.includes('/login')
        if (!isLoginRequest) {
          const store = useDataStore()
          if (error.config.headers.Authorization === `Bearer ${store.auth_key}`) {
            store.clearTokenRole()

            if (!isHandling401) {
              isHandling401 = true
              notification('Сессия истекла. Пожалуйста, войдите снова.', 'negative')

              if (router.currentRoute.value.path !== '/login') {
                router.replace('/login')
              }

              setTimeout(() => {
                isHandling401 = false
              }, 1500)
            }
          }
        }
      }

      return Promise.reject(error)
    }
  )
}
