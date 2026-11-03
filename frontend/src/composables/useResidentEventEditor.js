import { ref, computed } from 'vue'
import { normalizeEventPayload, sessionPayload } from '@/utils/eventForm'
import { getAdminFieldError } from '@/utils/adminValidation'
import { getApiErrorMessage } from '@/utils/apiError'
import { resolveMediaUrl } from '@/stores/counter'

export function useResidentEventEditor(store, eventId) {
  const loading = ref(true), saving = ref(false), loadError = ref(''), error = ref(''), success = ref('')
  const activeTab = ref('about'), phase = ref('')
  const form = ref({}), sessions = ref([]), photos = ref([]), status = ref(''), comment = ref('')
  const errors = ref({}), baseline = ref('')
  const removedSessions = new Set(), removedPhotos = new Set(), savedSessions = new Map(), savedPhotoIds = new Set()
  const blobUrls = new Set()
  let persistedForm = '', persistedOrder = '', nextKey = 0
  const key = () => `draft-${++nextKey}`
  const snapshot = () => JSON.stringify({ form: form.value, sessions: sessions.value, photos: photos.value.map(p => ({ key: p.key, photo_id: p.photo_id })) })
  const dirty = computed(() => !loading.value && baseline.value !== snapshot())
  const mapCoords = computed(() => Number.isFinite(form.value.latitude) && Number.isFinite(form.value.longitude) ? [form.value.latitude, form.value.longitude] : null)

  async function load() {
    loading.value = true; loadError.value = ''
    try {
      await Promise.all([store.FetchExcursionDetailResident(eventId), store.FetchExcursionsStats()])
      const event = store.getExcursionDetail.excursion
      const textFields = ['title', 'short_description', 'description', 'place', 'conducted_by', 'working_hours', 'contact_email', 'telegram', 'vk']
      form.value = Object.fromEntries(textFields.map(field => [field, event[field] ?? '']))
      Object.assign(form.value, {
        duration: event.duration, category: event.category?.category_name || '',
        format_type: event.format_type?.format_type_name || '', age_category: event.age_category?.age_category_name || '',
        latitude: event.latitude ?? null, longitude: event.longitude ?? null,
        distance_to_center: event.distance_to_center ?? null, time_to_nearest_stop: event.time_to_nearest_stop ?? null,
      })
      sessions.value = (event.sessions || []).map(s => ({ ...sessionPayload(s), session_id: s.session_id, booked: Number(s.booked) || 0, key: key() }))
      photos.value = [...(event.photos || [])].sort((a, b) => (a.order_index || 0) - (b.order_index || 0)).map(p => ({ ...p, key: key(), url: resolveMediaUrl(p.photo_url) }))
      status.value = event.moderation_status; comment.value = event.moderation_comment || ''
      removedSessions.clear(); removedPhotos.clear(); savedSessions.clear(); savedPhotoIds.clear()
      sessions.value.forEach(s => savedSessions.set(s.session_id, JSON.stringify(sessionPayload(s))))
      photos.value.forEach(p => savedPhotoIds.add(p.photo_id))
      persistedForm = JSON.stringify(normalizeEventPayload(form.value))
      persistedOrder = photos.value.map(p => p.photo_id).join(',')
      baseline.value = snapshot()
    } catch (cause) { loadError.value = getApiErrorMessage(cause, 'Не удалось загрузить событие') }
    finally { loading.value = false }
  }

  function addSession(source) {
    sessions.value.push({ key: key(), session_id: null, booked: 0,
      start_datetime: source?.start_datetime || '', max_participants: source?.max_participants || 1, cost: source?.cost || 0 })
  }
  function removeSession(session) {
    if (session.session_id) removedSessions.add(session.session_id)
    sessions.value = sessions.value.filter(s => s.key !== session.key)
  }
  function addPhotos(files) {
    for (const file of files) {
      if (!file.type.startsWith('image/')) { errors.value.photos = 'Выберите файлы изображений'; continue }
      const url = URL.createObjectURL(file); blobUrls.add(url)
      photos.value.push({ key: key(), file, url, photo_id: null, name: file.name })
    }
    if (photos.value.length) delete errors.value.photos
  }
  function removePhoto(photo) {
    if (photo.photo_id) removedPhotos.add(photo.photo_id)
    photos.value = photos.value.filter(p => p.key !== photo.key)
  }
  function movePhoto(index, target) {
    if (target < 0 || target >= photos.value.length) return
    const [photo] = photos.value.splice(index, 1)
    photos.value.splice(target, 0, photo)
  }
  function validate() {
    errors.value = {}; error.value = ''; success.value = ''
    const normalized = normalizeEventPayload(form.value)
    for (const field of ['title', 'description', 'category', 'format_type', 'age_category', 'duration', 'place', 'contact_email', 'distance_to_center', 'time_to_nearest_stop']) {
      const message = getAdminFieldError(normalized, 'residentEvent', field)
      if (message) errors.value[field] = message
    }
    for (const session of sessions.value) for (const field of ['start_datetime', 'max_participants', 'cost']) {
      const message = getAdminFieldError(session, 'session', field)
      if (message) errors.value[`${session.key}.${field}`] = message
    }
    if (!sessions.value.length) errors.value.sessions = 'Добавьте хотя бы один сеанс'
    if (!photos.value.length) errors.value.photos = 'Добавьте хотя бы одну фотографию события'
    const first = Object.keys(errors.value)[0]
    if (!first) return true
    activeTab.value = ['title', 'description', 'category', 'format_type', 'age_category', 'duration'].includes(first) ? 'about'
      : ['place', 'contact_email', 'distance_to_center', 'time_to_nearest_stop'].includes(first) ? 'location'
        : first === 'photos' ? 'photos' : 'sessions'
    error.value = 'Проверьте выделенные поля'
    return false
  }

  async function save(submit = false) {
    if (saving.value || !validate()) return false
    saving.value = true
    let detailsSaved = false
    try {
      phase.value = 'Сохраняем фотографии…'
      for (const photo of photos.value.filter(p => p.file)) {
        const data = new FormData(); data.append('photo', photo.file)
        const response = await store.PostNewPhoto(eventId, data)
        const saved = response.data.photos.find(p => !savedPhotoIds.has(p.photo_id))
        if (!saved) throw new Error('Фото загружено, но сервер не вернул его идентификатор')
        photo.photo_id = saved.photo_id; photo.file = null; savedPhotoIds.add(saved.photo_id)
      }
      for (const id of [...removedPhotos]) { await store.DeletePhoto(eventId, id); removedPhotos.delete(id); savedPhotoIds.delete(id) }
      const ids = photos.value.map(p => p.photo_id)
      if (ids.join(',') !== persistedOrder) {
        await store.ReorderResidentPhotos(eventId, ids)
        persistedOrder = ids.join(',')
      }
      phase.value = 'Сохраняем даты и стоимость…'
      for (const session of sessions.value) {
        const payload = sessionPayload(session), serialized = JSON.stringify(payload)
        if (session.session_id) {
          if (savedSessions.get(session.session_id) === serialized) continue
          await store.PatchResidentSession(eventId, session.session_id, payload)
        } else {
          const response = await store.PostNewSession(eventId, payload)
          session.session_id = response.data.session_id
        }
        savedSessions.set(session.session_id, serialized)
      }
      for (const id of [...removedSessions]) { await store.DeleteSession(eventId, id); removedSessions.delete(id); savedSessions.delete(id) }
      phase.value = 'Сохраняем описание…'
      const payload = normalizeEventPayload(form.value), serialized = JSON.stringify(payload)
      if (serialized !== persistedForm) { await store.PatchSessionData(eventId, payload); persistedForm = serialized }
      await store.FetchExcursionDetailResident(eventId)
      status.value = store.getExcursionDetail.excursion.moderation_status
      comment.value = store.getExcursionDetail.excursion.moderation_comment || ''
      baseline.value = snapshot(); detailsSaved = true
      if (submit && status.value === 'returned') {
        phase.value = 'Отправляем на проверку…'
        await store.SubmitEvent(eventId)
        status.value = 'pending'; comment.value = ''
      }
      success.value = submit ? 'Изменения сохранены. Событие отправлено на проверку.' : 'Все изменения сохранены.'
      return true
    } catch (cause) {
      error.value = getApiErrorMessage(cause, detailsSaved ? 'Изменения сохранены, но отправка на проверку не удалась. Повторите отправку.' : 'Не удалось сохранить все изменения. Правки остались в форме — повторите попытку.')
      return false
    } finally { saving.value = false; phase.value = '' }
  }
  function dispose() { blobUrls.forEach(url => URL.revokeObjectURL(url)); blobUrls.clear() }
  const preview = computed(() => ({
    ...form.value,
    category: { category_name: form.value.category }, format_type: { format_type_name: form.value.format_type }, age_category: { age_category_name: form.value.age_category },
    photos: photos.value.map(p => ({ photo_id: p.key, photo_url: p.url, isLocal: true })),
    sessions: sessions.value.map(s => ({ ...s, session_id: s.key, available: Math.max(0, s.max_participants - s.booked) })),
  }))
  return { loading, saving, loadError, error, success, activeTab, phase, form, sessions, photos, status, comment, errors, dirty, mapCoords, preview,
    load, addSession, removeSession, addPhotos, removePhoto, movePhoto, save, dispose }
}
