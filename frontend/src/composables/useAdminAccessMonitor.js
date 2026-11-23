import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDataStore } from '@/stores/counter'
import {
  ADMIN_ACCESS_CHECK_INTERVAL,
  adminAccessUnavailable,
  checkAdminAccess,
  closeAdminSession,
  isAdminAccessDenied,
} from '@/utils/adminAccess'

export function useAdminAccessMonitor() {
  const route = useRoute()
  const router = useRouter()
  const store = useDataStore()
  const onAdminRoute = computed(() => route.meta.requiredRole === 'admin')
  const hasAdminSession = computed(() => !!store.auth_key && store.role === 'admin')
  const accessUnavailable = computed(() => (
    onAdminRoute.value && hasAdminSession.value && adminAccessUnavailable(store.auth_key)
  ))
  const canRenderRoute = computed(() => (
    !onAdminRoute.value || (hasAdminSession.value && !accessUnavailable.value)
  ))
  const pendingToken = ref(null)
  const isChecking = computed(() => hasAdminSession.value && pendingToken.value === store.auth_key)

  function hideAdminContent(hidden) {
    document.documentElement.classList.toggle('admin-access-pending', hidden)
  }

  async function refreshAdminAccess() {
    if (!onAdminRoute.value || !hasAdminSession.value || document.hidden) return
    const token = store.auth_key
    if (pendingToken.value === token) return
    pendingToken.value = token

    try {
      await checkAdminAccess(token)
      if (onAdminRoute.value && store.auth_key === token && !document.hidden) hideAdminContent(false)
    } catch (error) {
      if (onAdminRoute.value && store.auth_key === token && isAdminAccessDenied(error)) {
        closeAdminSession(store, error.response.status)
        router.replace({ name: 'LoginPage' })
      }
    } finally {
      if (pendingToken.value === token) pendingToken.value = null
    }
  }

  function onPageHide() {
    if (onAdminRoute.value) hideAdminContent(true)
  }

  function onVisibilityChange() {
    if (document.hidden) onPageHide()
    else refreshAdminAccess()
  }

  watch(onAdminRoute, (isAdmin) => {
    hideAdminContent(isAdmin && document.hidden)
  })

  watch(accessUnavailable, (unavailable) => {
    document.documentElement.classList.toggle('admin-access-unavailable', unavailable)
  }, { immediate: true, flush: 'sync' })

  let timer
  onMounted(() => {
    timer = window.setInterval(refreshAdminAccess, ADMIN_ACCESS_CHECK_INTERVAL)
    document.addEventListener('visibilitychange', onVisibilityChange)
    window.addEventListener('focus', refreshAdminAccess)
    window.addEventListener('pagehide', onPageHide)
    window.addEventListener('pageshow', refreshAdminAccess)
  })

  onUnmounted(() => {
    window.clearInterval(timer)
    document.removeEventListener('visibilitychange', onVisibilityChange)
    window.removeEventListener('focus', refreshAdminAccess)
    window.removeEventListener('pagehide', onPageHide)
    window.removeEventListener('pageshow', refreshAdminAccess)
    hideAdminContent(false)
    document.documentElement.classList.remove('admin-access-unavailable')
  })

  return { canRenderRoute, accessUnavailable, isChecking, refreshAdminAccess }
}
