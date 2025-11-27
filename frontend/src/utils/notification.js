import { useNotification } from '@/composables/useNotification'

let notificationInstance = null

const getNotificationInstance = () => {
  if (!notificationInstance) {
    notificationInstance = useNotification()
  }
  return notificationInstance
}

export const notification = (message, type = 'positive') => {
  const instance = getNotificationInstance()
  return instance.notify(message, type) // Возвращаем Promise
}
