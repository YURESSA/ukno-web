import axios from 'axios'
import { useDataStore } from '@/stores/counter'
import router from '@/router'
import { notification } from '@/utils/notification'

let isHandling401 = false

export function setupAxiosInterceptors() {
  axios.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response && error.response.status === 401) {
        const isLoginRequest = error.config?.url?.includes('/login')

        if (!isLoginRequest) {
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
