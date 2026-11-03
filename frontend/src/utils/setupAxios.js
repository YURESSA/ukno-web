import axios from 'axios'
import { useDataStore } from '@/stores/counter'
import router from '@/router'
import { notification } from '@/utils/notification'
import { getApiErrorMessage } from '@/utils/apiError'

let isHandling401 = false

export function setupAxiosInterceptors() {
  axios.interceptors.response.use(
    (response) => {
      const authorization = response.config?.headers?.Authorization
      // A request from the previous session must not refill cleared stores.
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
      const authenticated = Boolean(error.config?.headers?.Authorization)
      const invalidJwt = status === 422 && /token|signature|segments|jwt|header|padding|subject|claim|\balg\b|алгоритм|токен/i.test(originalMessage || '')
      if ((status === 401 && authenticated) || (invalidJwt && authenticated)) {
        const isLoginRequest = error.config?.url?.includes('/login')
        if (!isLoginRequest) {
          const store = useDataStore()
          // Ignore failures from a token replaced by a subsequent login.
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
