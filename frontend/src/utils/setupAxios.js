import axios from 'axios'
import { useDataStore } from '@/stores/counter'
import router from '@/router'
import { notification } from '@/utils/notification'
import { getApiErrorMessage } from '@/utils/apiError'

let isHandling401 = false

export function setupAxiosInterceptors() {
  axios.interceptors.response.use(
    (response) => response,
    (error) => {
      if (axios.isCancel(error)) return Promise.reject(error)
      const originalMessage = error.response?.data?.message || error.response?.data?.msg
      const errorMessage = getApiErrorMessage(error)
      if (error.response && error.response.data && typeof error.response.data === 'object') {
        error.response.data.message = errorMessage
      }
      if (error.response && error.response.status === 401) {
        const isLoginRequest = error.config?.url?.includes('/login')
        const isSessionError = !originalMessage || /token|authorization|bearer|сессия/i.test(originalMessage)

        if (!isLoginRequest && isSessionError) {
          const store = useDataStore()

          if (store.auth_key) {
            store.clearTokenRole()

            if (!isHandling401) {
              isHandling401 = true
              notification('Сессия истекла. Пожалуйста, войдите снова.', 'negative')

              if (router.currentRoute.value.path !== '/login') {
                router.push('/login')
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
