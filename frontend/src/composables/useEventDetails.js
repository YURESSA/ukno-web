import { ref, watch } from 'vue'
import { useDataStore } from '@/stores/counter'
import { getApiErrorMessage } from '@/utils/apiError'

export function parseEventRouteId(value) {
  if (typeof value !== 'string' || !/^\d+$/.test(value)) return null
  const id = Number(value)
  return Number.isSafeInteger(id) && id > 0 ? id : null
}

export function useEventDetails(getId, shouldLoad = () => true) {
  const store = useDataStore()
  const event = ref(null)
  const notFound = ref(false)
  const error = ref('')
  const attempt = ref(0)

  watch([getId, shouldLoad, attempt], async ([routeId, enabled], _, onCleanup) => {
    event.value = null
    notFound.value = false
    error.value = ''
    if (!enabled) return

    const id = parseEventRouteId(routeId)
    if (id === null) {
      notFound.value = true
      return
    }

    const controller = new AbortController()
    onCleanup(() => controller.abort())

    try {
      const data = await store.FetchExcursionDetail(id, controller.signal)
      if (controller.signal.aborted) return

      if (data) {
        event.value = data
      } else {
        error.value = 'Не удалось загрузить событие.'
      }
    } catch (requestError) {
      if (controller.signal.aborted) return

      if (requestError.response?.status === 404) {
        notFound.value = true
      } else {
        error.value = getApiErrorMessage(requestError, 'Не удалось загрузить событие.')
      }
    }
  }, { immediate: true })

  function retry() {
    attempt.value++
  }

  return { event, notFound, error, retry }
}
