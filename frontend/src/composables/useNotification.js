import { ref } from 'vue'

const showNotification = ref(false)
const notificationMessage = ref('')
const notificationType = ref('negative')
let resolvePromise = null

// Выносим функции наружу
const blockClicks = (event) => {
  if (event.target.closest('.notification-wrapper')) {
    return
  }
  event.preventDefault()
  event.stopPropagation()
}

const blockKeys = (event) => {
  if (event.key === 'Escape') {
    closeNotification()
    return
  }
  event.preventDefault()
}

const closeNotification = () => {
  showNotification.value = false
  document.body.style.overflow = ''
  document.removeEventListener('click', blockClicks, true)
  document.removeEventListener('keydown', blockKeys, true)

  if (resolvePromise) {
    resolvePromise()
    resolvePromise = null
  }
}

export function useNotification() {
  const notify = (message, type = 'positive') => {
    return new Promise((resolve) => {
      notificationMessage.value = message
      notificationType.value = type
      resolvePromise = resolve
      showNotification.value = true

      document.body.style.overflow = 'hidden'
      document.addEventListener('click', blockClicks, true)
      document.addEventListener('keydown', blockKeys, true)
    })
  }

  return {
    showNotification,
    notificationMessage,
    notificationType,
    notify,
    closeNotification
  }
}
