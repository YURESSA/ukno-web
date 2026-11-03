<template>
  <main class="resident-editor">
    <header class="editor-header">
      <div><p class="eyebrow">Кабинет резидента / События</p><h1>Редактор события</h1></div>
      <button type="button" class="quiet-button" :disabled="saving" @click="close">Закрыть редактор</button>
    </header>
    <p v-if="loading" role="status">Загружаем событие…</p>
    <div v-else-if="loadError" role="alert" class="notice error-notice">{{ loadError }} <button type="button" @click="load">Повторить</button></div>
    <template v-else>
      <section class="moderation-notice" :class="{ returned: status === 'returned' }">
        <strong>{{ eventModeration(status).label }}</strong>
        <p v-if="comment" class="moderator-comment">Комментарий администратора: {{ comment }}</p>
        <p v-if="status === 'returned'">Внесите исправления и отправьте событие на проверку прямо из редактора.</p>
        <p v-else-if="status === 'approved'">Новые даты можно добавлять без повторной проверки. Изменение описания, фотографий или существующих сеансов скроет событие до одобрения.</p>
        <p v-else>Событие появится на сайте после одобрения администратором.</p>
      </section>
      <div class="preview-action">
        <button type="button" class="quiet-button" @click="showPreview = true">Предпросмотр события</button>
      </div>
      <form novalidate @submit.prevent="save(false)">
        <nav class="editor-tabs" role="tablist" aria-label="Разделы события">
          <button v-for="tab in tabs" :id="`tab-${tab.key}`" :key="tab.key" type="button" role="tab" :aria-selected="activeTab === tab.key" :aria-controls="`panel-${tab.key}`" :tabindex="activeTab === tab.key ? 0 : -1" :class="{ active: activeTab === tab.key }" @click="activeTab = tab.key" @keydown.right.prevent="switchTab(1)" @keydown.left.prevent="switchTab(-1)">{{ tab.label }}</button>
        </nav>
        <div class="editor-fields" :inert="saving">
          <section v-show="activeTab === 'about'" id="panel-about" role="tabpanel" aria-labelledby="tab-about">
            <h2>О событии</h2><p class="section-hint">Расскажите, что ждёт посетителей. Поля со звёздочкой обязательны.</p>
            <label>Название*<input v-model="form.title" name="title" :aria-invalid="!!errors.title" placeholder="Например, прогулка по Хлебозаводу" /></label><p v-if="errors.title" class="field-error" role="alert">{{ errors.title }}</p>
            <label>Краткое описание<textarea v-model="form.short_description" rows="2" placeholder="Пара предложений для карточки события" /></label>
            <div><label id="description-label">Полное описание*</label><Editor v-model="form.description" aria-labelledby="description-label" /><p v-if="errors.description" class="field-error" role="alert">{{ errors.description }}</p></div>
            <div class="field-grid">
              <label>Категория*<select v-model="form.category" :aria-invalid="!!errors.category"><option value="" disabled>Выберите категорию</option><option v-for="item in stats.categories || []" :key="item.category_id" :value="item.category_name">{{ item.category_name }}</option></select><span v-if="errors.category" class="field-error">{{ errors.category }}</span></label>
              <label>Формат*<select v-model="form.format_type" :aria-invalid="!!errors.format_type"><option value="" disabled>Выберите формат</option><option v-for="item in stats.format_types || []" :key="item.format_type_id" :value="item.format_type_name">{{ item.format_type_name }}</option></select><span v-if="errors.format_type" class="field-error">{{ errors.format_type }}</span></label>
              <label>Возраст*<select v-model="form.age_category" :aria-invalid="!!errors.age_category"><option value="" disabled>Выберите возраст</option><option v-for="item in stats.age_categories || []" :key="item.age_category_id" :value="item.age_category_name">{{ item.age_category_name }}</option></select><span v-if="errors.age_category" class="field-error">{{ errors.age_category }}</span></label>
              <label>Продолжительность, мин.*<input v-model.number="form.duration" type="number" min="0" step="1" :aria-invalid="!!errors.duration" /><span v-if="errors.duration" class="field-error">{{ errors.duration }}</span></label>
            </div>
          </section>
          <section v-show="activeTab === 'location'" id="panel-location" role="tabpanel" aria-labelledby="tab-location">
            <h2>Место и контакты</h2>
            <label>Место сбора*<input v-model="form.place" :aria-invalid="!!errors.place" placeholder="Адрес и ориентир для посетителей" /></label><p v-if="errors.place" class="field-error">{{ errors.place }}</p>
            <div><label>Точка на карте</label><MapPicker v-if="activeTab === 'location' && !showPreview" map-id="resident-editor-map" :initial-coords="mapCoords" @update:coords="({ latitude, longitude }) => Object.assign(form, { latitude, longitude })" /></div>
            <div class="field-grid">
              <label>Организатор<input v-model="form.conducted_by" /></label>
              <label>Часы работы<input v-model="form.working_hours" placeholder="Ежедневно с 10:00 до 21:00" /></label>
              <label>Почта для связи<input v-model="form.contact_email" type="email" :aria-invalid="!!errors.contact_email" /><span v-if="errors.contact_email" class="field-error">{{ errors.contact_email }}</span></label>
              <label>Telegram<input v-model="form.telegram" placeholder="@username" /></label>
              <label>VK<input v-model="form.vk" placeholder="Ссылка на страницу" /></label>
              <label>Расстояние до центра, м<input v-model.number="form.distance_to_center" type="number" min="0" /><span v-if="errors.distance_to_center" class="field-error">{{ errors.distance_to_center }}</span></label>
              <label>До ближайшей остановки, мин.<input v-model.number="form.time_to_nearest_stop" type="number" min="0" /><span v-if="errors.time_to_nearest_stop" class="field-error">{{ errors.time_to_nearest_stop }}</span></label>
            </div>
          </section>
          <section v-show="activeTab === 'sessions'" id="panel-sessions" role="tabpanel" aria-labelledby="tab-sessions">
            <div class="section-heading"><div><h2>Даты и стоимость</h2><p class="section-hint">Все даты сохранятся вместе с событием.</p></div><button type="button" class="quiet-button" @click="addSession()">+ Добавить дату</button></div>
            <p v-if="errors.sessions" class="field-error" role="alert">{{ errors.sessions }}</p>
            <p v-if="!sessions.length" class="empty-state">Добавьте первую дату проведения события.</p>
            <article v-for="(session, index) in sessions" :key="session.key" class="session-card">
              <div class="section-heading"><strong>Сеанс {{ index + 1 }}</strong><div class="row-actions"><button type="button" class="text-button" @click="addSession(session)">Дублировать</button><button type="button" class="text-button danger" :aria-label="`Удалить сеанс ${index + 1}`" @click="pendingRemoval = { kind: 'session', item: session }">Удалить</button></div></div>
              <p v-if="session.booked" class="section-hint">Уже записано: {{ session.booked }}. При удалении сеанса бронирования будут отменены.</p>
              <div class="session-grid">
                <label>Дата и время*<input v-model="session.start_datetime" type="datetime-local" :aria-invalid="!!errors[`${session.key}.start_datetime`]" /><span v-if="errors[`${session.key}.start_datetime`]" class="field-error">{{ errors[`${session.key}.start_datetime`] }}</span></label>
                <label>Количество мест*<input v-model.number="session.max_participants" type="number" :min="Math.max(1, session.booked)" step="1" /><span v-if="errors[`${session.key}.max_participants`]" class="field-error">{{ errors[`${session.key}.max_participants`] }}</span></label>
                <label>Стоимость, ₽*<input v-model.number="session.cost" type="number" min="0" step="0.01" /><span v-if="errors[`${session.key}.cost`]" class="field-error">{{ errors[`${session.key}.cost`] }}</span></label>
              </div>
            </article>
          </section>
          <section v-show="activeTab === 'photos'" id="panel-photos" role="tabpanel" aria-labelledby="tab-photos">
            <h2>Фотографии</h2><p class="section-hint">Добавьте хотя бы одну фотографию. Первое изображение — обложка события. Загрузка, удаление и порядок применятся после сохранения.</p>
            <label class="upload-area">Добавить фотографии<input type="file" accept="image/*" multiple @change="onFiles" /></label>
            <p v-if="errors.photos" class="field-error" role="alert">{{ errors.photos }}</p>
            <div class="photo-grid">
              <article v-for="(photo, index) in photos" :key="photo.key" class="photo-card">
                <img :src="photo.url" :alt="`Фотография ${index + 1}`" /><span v-if="index === 0" class="cover-label">Обложка</span><span v-else-if="photo.file" class="cover-label">Новое фото</span>
                <div class="photo-actions"><button v-if="index > 0" type="button" class="text-button" @click="movePhoto(index, 0)">На обложку</button><button type="button" :disabled="index === 0" :aria-label="`Переместить фото ${index + 1} выше`" @click="movePhoto(index, index - 1)">←</button><button type="button" :disabled="index === photos.length - 1" :aria-label="`Переместить фото ${index + 1} ниже`" @click="movePhoto(index, index + 1)">→</button><button type="button" class="text-button danger" :aria-label="`Удалить фото ${index + 1}`" @click="pendingRemoval = { kind: 'photo', item: photo }">Удалить</button></div>
              </article>
            </div>
          </section>
        </div>
      </form>
      <EventPreviewModal v-model:show="showPreview" :event="preview" />
      <footer class="save-bar">
        <div aria-live="polite"><p v-if="error" class="field-error" role="alert">{{ error }}</p><p v-else-if="success && !dirty" class="save-success" role="status">{{ success }}</p><p v-else>{{ saving ? phase : dirty ? 'Есть несохранённые изменения' : 'Все изменения сохранены' }}</p></div>
        <div class="save-actions"><button v-if="status === 'returned'" type="button" class="quiet-button" :disabled="saving || !dirty" @click="save(false)">{{ saving ? 'Сохранение…' : 'Сохранить изменения' }}</button><BaseButton v-else text="Сохранить изменения" :loading="saving" :disabled="!dirty" @click="save(false)" /><BaseButton v-if="status === 'returned'" text="Сохранить и отправить на проверку" :loading="saving" @click="save(true)" /></div>
      </footer>
    </template>
    <n-modal :show="!!pendingRemoval" preset="dialog" :title="pendingRemoval?.kind === 'session' ? 'Убрать сеанс?' : 'Убрать фотографию?'" content="Изменение применится только после нажатия «Сохранить изменения»." positive-text="Убрать" negative-text="Отмена" @positive-click="confirmRemoval" @negative-click="pendingRemoval = null" @update:show="value => { if (!value) pendingRemoval = null }" />
    <n-modal :show="leaving" preset="dialog" title="Есть несохранённые изменения" content="Если выйти сейчас, несохранённые правки будут потеряны." positive-text="Выйти без сохранения" negative-text="Продолжить редактирование" @positive-click="resolveLeave(true)" @negative-click="resolveLeave(false)" @update:show="value => { if (!value) resolveLeave(false) }" />
  </main>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted, nextTick, defineAsyncComponent } from 'vue'
import { useRoute, useRouter, onBeforeRouteLeave, onBeforeRouteUpdate } from 'vue-router'
import { NModal } from 'naive-ui'
import { useDataStore } from '@/stores/counter'
import { useResidentEventEditor } from '@/composables/useResidentEventEditor'
import { eventModeration } from '@/utils/eventModeration'
import BaseButton from '@/components/ui/button/BaseButton.vue'
import MapPicker from '@/components/shared/MapPicker.vue'
import EventPreviewModal from '@/components/shared/EventPreviewModal.vue'

const Editor = defineAsyncComponent(() => import('@/components/ui/Editor.vue'))

const store = useDataStore(), route = useRoute(), router = useRouter()
const state = useResidentEventEditor(store, route.params.id)
const { loading, saving, loadError, error, success, activeTab, phase, form, sessions, photos, status, comment, errors, dirty, mapCoords, preview, load, addSession, removeSession, addPhotos, removePhoto, movePhoto, save } = state
const showPreview = ref(false)
const stats = computed(() => store.getExcursionsStats || {})
const tabs = [{ key: 'about', label: 'О событии' }, { key: 'location', label: 'Место и контакты' }, { key: 'sessions', label: 'Даты и стоимость' }, { key: 'photos', label: 'Фотографии' }]
const pendingRemoval = ref(null), leaving = ref(false)
let leaveResolver
function onFiles(event) { addPhotos(event.target.files); event.target.value = '' }
function confirmRemoval() {
  const action = pendingRemoval.value
  if (action?.kind === 'session') removeSession(action.item)
  else if (action) removePhoto(action.item)
  pendingRemoval.value = null
}
async function switchTab(direction) {
  activeTab.value = tabs[(tabs.findIndex(t => t.key === activeTab.value) + direction + tabs.length) % tabs.length].key
  await nextTick(); document.getElementById(`tab-${activeTab.value}`)?.focus()
}
function canLeave() {
  if (saving.value || leaving.value) return false
  if (!dirty.value) return true
  leaving.value = true
  return new Promise(resolve => { leaveResolver = resolve })
}
function resolveLeave(allowed) { leaving.value = false; leaveResolver?.(allowed); leaveResolver = null }
function beforeUnload(event) { if (dirty.value || saving.value) { event.preventDefault(); event.returnValue = '' } }
function close() { router.push('/resident-profile') }
onBeforeRouteLeave(canLeave)
onBeforeRouteUpdate(canLeave)
onMounted(() => { document.body.style.overflowY = 'auto'; window.addEventListener('beforeunload', beforeUnload); load() })
onUnmounted(() => { window.removeEventListener('beforeunload', beforeUnload); resolveLeave(false); state.dispose() })
</script>

<style scoped>
.resident-editor { max-width: 1120px; margin: 0 auto; padding: 36px 24px 0; color: #333; font-family: 'Manrope', sans-serif; }
.editor-header, .section-heading { display: flex; justify-content: space-between; align-items: center; gap: 16px; }
.editor-header { margin-bottom: 24px; }
.editor-header h1 { font-size: clamp(24px, 3vw, 36px); line-height: 1.25; margin: 6px 0; }
.eyebrow, .section-hint { color: #777; font-size: 14px; line-height: 1.6; }
.moderation-notice { background: #f7f7f7; border: 1px solid #e8e8e8; padding: 18px 22px; border-radius: 16px; line-height: 1.6; font-size: 14px; }
.moderation-notice.returned { background: #fff6ed; border-color: #ffd8ba; }
.moderator-comment { white-space: pre-wrap; overflow-wrap: anywhere; margin: 6px 0; }
.preview-action { display: flex; justify-content: flex-end; margin: 20px 0 8px; }
button { font: inherit; cursor: pointer; }
button:disabled { cursor: default; opacity: .5; }
button:focus-visible, input:focus-visible, textarea:focus-visible, select:focus-visible { outline: 2px solid #f25c03; outline-offset: 3px; }
.editor-tabs { display: flex; gap: 24px; border-bottom: 1px solid #e6e6e6; overflow-x: auto; }
.editor-tabs button { padding: 16px 0; white-space: nowrap; background: none; border: 0; border-bottom: 2px solid transparent; color: #777; font-size: 15px; }
.editor-tabs button.active { color: #e85a07; border-color: #f25c03; }
.editor-fields { padding: 28px 0 36px; min-height: 420px; }
section[role='tabpanel'] { display: flex; flex-direction: column; gap: 18px; }
section h2 { font-size: 23px; line-height: 1.4; margin: 0; }
label { display: flex; flex-direction: column; gap: 8px; font-size: 14px; font-weight: 600; }
input, textarea, select { box-sizing: border-box; width: 100%; border: 1px solid #ddd; border-radius: 10px; padding: 12px 14px; font: inherit; font-weight: 400; background: #fff; color: #333; }
textarea { resize: vertical; }
input[aria-invalid='true'], select[aria-invalid='true'] { border-color: #c93437; }
.field-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 20px; }
.session-grid { display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 16px; }
.session-card { border: 1px solid #e4e4e4; border-radius: 14px; padding: 20px; display: grid; gap: 18px; }
.row-actions, .save-actions, .photo-actions { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.quiet-button { border: 1px solid #d8d8d8; border-radius: 12px; background: white; color: #333; padding: 11px 18px; font-size: 14px; }
.quiet-button:hover:not(:disabled) { background: #fff6ef; border-color: #f25c03; }
.text-button { border: 0; background: none; color: #555; font-size: 13px; padding: 4px 0; }
.danger, .field-error { color: #bb3030; }
.field-error { font-size: 13px; line-height: 1.5; }
.save-success { color: #277947; }
.upload-area { border: 1px dashed #f2ab7c; background: #fff9f5; padding: 24px; border-radius: 14px; }
.upload-area input { background: transparent; border: 0; padding: 0; font-size: 13px; }
.upload-area input::file-selector-button {
  margin-right: 14px;
  padding: 12px 20px;
  border: 0;
  border-radius: 12px;
  background: #f25c03;
  color: #fff;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
  transition: background .15s;
}
.upload-area input::file-selector-button:hover { background: #cf5006; }
.photo-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; }
.photo-card { position: relative; border: 1px solid #e4e4e4; border-radius: 14px; overflow: hidden; }
.photo-card img { width: 100%; height: 180px; object-fit: cover; display: block; }
.cover-label { position: absolute; top: 10px; left: 10px; border-radius: 7px; background: #fff; padding: 5px 9px; font-size: 12px; }
.photo-actions { padding: 12px; gap: 10px; justify-content: space-between; }
.photo-actions > button:not(.text-button) { background: #f5f5f5; border: 0; border-radius: 5px; padding: 4px 8px; }
.save-bar { position: sticky; bottom: 0; z-index: 20; padding: 18px 0; background: #ffffffed; backdrop-filter: blur(12px); border-top: 1px solid #e4e4e4; display: flex; justify-content: space-between; gap: 18px; align-items: center; font-size: 13px; }
.save-actions :deep(button) { font-family: inherit; font-size: 14px; padding: 12px 18px; height: auto; }
.empty-state { padding: 24px; background: #fafafa; border-radius: 12px; color: #777; }
.notice { padding: 20px; border-radius: 12px; }.error-notice { background: #fff0ed; }
@media (max-width: 720px) {
  .resident-editor { padding: 24px 16px 0; }
  .editor-header, .section-heading { align-items: flex-start; flex-wrap: wrap; }
  .field-grid, .session-grid { grid-template-columns: 1fr; }
  .photo-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .editor-tabs { gap: 20px; }.save-bar { flex-direction: column; align-items: stretch; padding-bottom: max(16px, env(safe-area-inset-bottom)); }.save-actions { flex-direction: column; align-items: stretch; }.photo-card img { height: 140px; }
}
</style>
