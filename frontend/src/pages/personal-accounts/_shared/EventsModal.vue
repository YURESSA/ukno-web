<template>
  <n-modal :show="true" preset="card" class="resident-events-modal"
    style="width: min(1000px, calc(100vw - 32px)); height: min(760px, calc(100dvh - 32px)); border-radius: 20px"
    :content-style="{ display: 'flex', flexDirection: 'column', minHeight: '0', overflow: 'hidden', gap: '16px' }"
    :mask-closable="!deleting && !pendingDelete" :closable="!deleting"
    @update:show="value => { if (!value) emit('close') }">
    <template #header><div class="list-heading"><h2>Мои события</h2><span>{{ allEvents.length }} всего</span></div></template>
    <div class="list-toolbar">
      <label class="search-field"><span class="sr-only">Найти событие по названию</span><input v-model="search" type="search" placeholder="Найти по названию…" /></label>
      <button type="button" class="create-button" @click="navigate('/newEvent')">+ Новое событие</button>
    </div>
    <div class="status-filters" role="group" aria-label="Фильтр по статусу">
      <button v-for="option in filters" :key="option.value" type="button" :aria-pressed="statusFilter === option.value" :class="{ selected: statusFilter === option.value }" @click="statusFilter = option.value">{{ option.label }} <span>{{ countStatus(option.value) }}</span></button>
    </div>
    <div class="events-list" :aria-busy="loading">
      <p v-if="loading" class="empty-state" role="status">Загружаем события…</p>
      <div v-else-if="loadError" class="empty-state" role="alert"><p>{{ loadError }}</p><button type="button" class="edit-button" @click="loadEvents">Повторить загрузку</button></div>
      <template v-else-if="filteredEvents.length">
        <article v-for="event in filteredEvents" :key="event.excursion_id" class="event-card">
          <img v-if="event.photos?.[0]?.photo_url" class="event-photo" :src="resolveMediaUrl(event.photos[0].photo_url)" alt="" loading="lazy" />
          <div v-else class="event-photo photo-placeholder">{{ event.category?.category_name || 'Событие' }}</div>
          <div class="event-info">
            <div class="event-top"><span class="status-badge" :class="event.moderation_status">{{ eventModeration(event.moderation_status).label }}</span><button type="button" class="delete-button" :disabled="deleting" :aria-label="`Удалить событие ${event.title}`" title="Удалить событие" @click="pendingDelete = event"><img src="/icon/basket.svg" alt="" /></button></div>
            <button type="button" class="event-title" @click="navigate(`/change-event/${event.excursion_id}`)">{{ event.title }}</button>
            <p class="event-meta">{{ sessionSummary(event) }}<span v-if="event.category?.category_name"> · {{ event.category.category_name }}</span></p>
            <p class="description-text">{{ plainDescription(event.short_description || event.description) }}</p>
            <p v-if="event.moderation_comment" class="moderation-comment"><strong>Комментарий администратора</strong>{{ event.moderation_comment }}</p>
            <div class="event-actions">
              <button type="button" class="edit-button" :aria-label="`Редактировать событие ${event.title}`" @click="navigate(`/change-event/${event.excursion_id}`)">Редактировать</button>
              <button v-if="event.moderation_status === 'returned'" type="button" class="review-button" :disabled="submitting !== null" @click="submitForReview(event)">{{ submitting === event.excursion_id ? 'Отправляем…' : 'Отправить на проверку' }}</button>
            </div>
          </div>
        </article>
      </template>
      <div v-else class="empty-state"><h3>{{ allEvents.length ? 'Ничего не найдено' : 'Пока нет событий' }}</h3><p>{{ allEvents.length ? 'Попробуйте изменить поиск или статус.' : 'Создайте первое событие — оно появится в этом списке.' }}</p><button v-if="allEvents.length" type="button" class="edit-button" @click="search = ''; statusFilter = 'all'">Сбросить фильтры</button></div>
    </div>
    <p v-if="!loading && !loadError" class="list-count">Показано {{ filteredEvents.length }} из {{ allEvents.length }}</p>
  </n-modal>
  <n-modal :show="!!pendingDelete" preset="dialog" title="Удалить событие?"
    :content="`Событие «${pendingDelete?.title || ''}» и его сеансы будут удалены. Это действие нельзя отменить.`"
    positive-text="Удалить" negative-text="Отмена" :loading="deleting"
    :mask-closable="!deleting" :closable="!deleting"
    :positive-button-props="{ type: 'error', disabled: deleting }"
    :negative-button-props="{ disabled: deleting }"
    :on-positive-click="confirmDelete" @negative-click="pendingDelete = null"
    @update:show="value => { if (!value && !deleting) pendingDelete = null }"
  />
</template>

<script setup>
import router from '@/router';
import { useDataStore, resolveMediaUrl } from '@/stores/counter';
import DOMPurify from 'dompurify';
import { computed, onMounted, ref } from 'vue';
import { notification } from '@/utils/notification'
import { eventModeration } from '@/utils/eventModeration'
import { getApiErrorMessage } from '@/utils/apiError'
import { NModal } from 'naive-ui'

const store = useDataStore();
const events = computed(() => store.getResidentEvents);
const emit = defineEmits(['close']);
const loading = ref(true);
const submitting = ref(null);
const pendingDelete = ref(null);
const deleting = ref(false);

async function submitForReview(event) {
  if (submitting.value !== null) return;
  if (!event.photos?.length) return notification('Добавьте фотографию события в редакторе перед отправкой на проверку', 'negative');
  const id = event.excursion_id;
  submitting.value = id;
  try {
    await store.SubmitEvent(id);
    await store.FetchResidentEvents();
    notification('Событие отправлено на проверку', 'positive');
  } catch (error) {
    notification(getApiErrorMessage(error, 'Не удалось отправить событие'), 'negative');
  } finally {
    submitting.value = null;
  }
}

const search = ref('');
const statusFilter = ref('all');
const loadError = ref('');
const allEvents = computed(() => events.value?.excursions || []);
const filters = [
  { value: 'all', label: 'Все' }, { value: 'returned', label: 'На доработке' },
  { value: 'pending', label: 'На проверке' }, { value: 'approved', label: 'Одобрены' },
];
const countStatus = status => status === 'all' ? allEvents.value.length : allEvents.value.filter(event => event.moderation_status === status).length;
const filteredEvents = computed(() => allEvents.value.filter(event =>
  (statusFilter.value === 'all' || event.moderation_status === statusFilter.value) &&
  (event.title || '').toLocaleLowerCase('ru').includes(search.value.trim().toLocaleLowerCase('ru'))
));
function navigate(path) { emit('close'); router.push(path); }
function plainDescription(value) {
  const safe = DOMPurify.sanitize(value || '', { ALLOWED_TAGS: [], ALLOWED_ATTR: [] });
  return new DOMParser().parseFromString(safe, 'text/html').body.textContent || '';
}
function sessionSummary(event) {
  const sessions = [...(event.sessions || [])].filter(s => Number.isFinite(new Date(s.start_datetime).getTime())).sort((a, b) => new Date(a.start_datetime) - new Date(b.start_datetime));
  if (!sessions.length) return 'Даты не добавлены';
  const next = sessions.find(s => new Date(s.start_datetime) >= new Date()) || sessions[0];
  const date = new Date(next.start_datetime).toLocaleString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' });
  return date + (sessions.length > 1 ? ` · Всего дат: ${sessions.length}` : '');
}
async function loadEvents() {
  loading.value = true; loadError.value = '';
  try { await store.FetchResidentEvents(); }
  catch (error) { loadError.value = getApiErrorMessage(error, 'Не удалось загрузить события'); }
  finally { loading.value = false; }
}
onMounted(loadEvents);

async function confirmDelete(){
  if (deleting.value || !pendingDelete.value) return false;
  deleting.value = true;
  try {
    await store.DeletEvent(pendingDelete.value.excursion_id);
    pendingDelete.value = null;
    await store.FetchResidentEvents();
    await notification('Событие успешно удалено', 'positive');
  } catch (error) {
    notification(getApiErrorMessage(error, 'Не удалось удалить событие'), 'negative');
    return false;
  } finally {
    deleting.value = false;
  }
}
</script>

<style scoped>
.list-heading { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; padding-right: 28px; }
.list-heading h2 { margin: 0; font-size: 27px; line-height: 1.3; }
.list-heading > span, .list-count { color: #888; font-size: 13px; font-weight: 400; }
.list-toolbar { display: flex; gap: 12px; }
.search-field { flex: 1; min-width: 0; }
.search-field input { width: 100%; box-sizing: border-box; height: 42px; padding: 10px 14px; border: 1px solid #dedede; border-radius: 10px; font: inherit; font-size: 14px; }
button { font: inherit; cursor: pointer; }
button:disabled { opacity: .5; cursor: default; }
button:focus-visible, input:focus-visible { outline: 2px solid #f25c03; outline-offset: 3px; }
.create-button { padding: 10px 18px; border: 0; border-radius: 10px; background: #f25c03; color: #fff; font-size: 14px; white-space: nowrap; }
.create-button:hover { background: #cf5006; }
.status-filters { display: flex; gap: 8px; overflow-x: auto; flex-shrink: 0; padding: 3px; }
.status-filters button { border: 1px solid #e6e6e6; border-radius: 9px; background: #fff; padding: 8px 12px; color: #666; font-size: 13px; white-space: nowrap; }
.status-filters button.selected { color: #b94b08; background: #fff4eb; border-color: #f6c6a5; }
.status-filters span { margin-left: 6px; opacity: .7; }
.events-list { flex: 1; min-height: 0; overflow-y: auto; overscroll-behavior: contain; display: flex; flex-direction: column; gap: 12px; padding: 2px 8px 2px 2px; }
.event-card { display: flex; align-items: flex-start; gap: 18px; padding: 18px; border: 1px solid #e6e6e6; border-radius: 14px; }
.event-photo { width: 132px; height: 108px; object-fit: cover; border-radius: 10px; flex-shrink: 0; margin-top: 3px; }
.photo-placeholder { display: grid; place-items: center; background: #fff4eb; color: #b88667; font-size: 13px; text-align: center; }
.event-info { flex: 1; min-width: 0; }
.event-top { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
.status-badge { padding: 3px 9px; border-radius: 6px; font-size: 12px; background: #f3f3f3; color: #666; }
.status-badge.pending { background: #fff5df; color: #936714; }.status-badge.returned { background: #fff0eb; color: #ac4a2d; }.status-badge.approved { background: #edf7ee; color: #3c7945; }
.delete-button { border: 0; background: transparent; border-radius: 6px; padding: 4px; display: flex; }.delete-button img { width: 18px; height: 18px; opacity: .65; }.delete-button:hover { background: #fff0eb; }
.event-title { display: block; text-align: left; font-weight: 650; font-size: 18px; line-height: 1.4; background: none; border: 0; padding: 6px 0 0; color: #333; overflow-wrap: anywhere; }.event-title:hover { color: #d95508; }
.event-meta { color: #888; font-size: 12px; margin-top: 5px; line-height: 1.5; }
.description-text { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; color: #666; font-size: 13px; line-height: 1.5; margin-top: 8px; }
.event-actions { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 12px; }
.edit-button, .review-button { border: 1px solid #dedede; background: #fff; border-radius: 8px; padding: 7px 12px; font-size: 13px; color: #444; }.edit-button:hover, .review-button:hover:not(:disabled) { border-color: #edab7e; background: #fff7f1; }.review-button { color: #bd510f; border-color: #f2ccb0; }
.moderation-comment { margin-top: 10px; background: #fff7ef; border-radius: 8px; padding: 10px 12px; font-size: 13px; line-height: 1.5; white-space: pre-wrap; overflow-wrap: anywhere; }.moderation-comment strong { display: block; margin-bottom: 4px; font-size: 12px; color: #956646; }
.empty-state { margin: auto; padding: 40px 16px; text-align: center; color: #888; font-size: 14px; }.empty-state h3 { font-size: 20px; color: #555; }.empty-state p { margin: 10px 0 16px; }
.list-count { margin: 0; flex-shrink: 0; }.sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip-path: inset(50%); white-space: nowrap; }
@media(max-width: 600px) { .list-heading h2 { font-size: 23px; }.list-toolbar { flex-wrap: wrap; }.search-field { flex-basis: 100%; }.event-card { gap: 12px; padding: 12px; }.event-photo { width: 64px; height: 64px; }.event-title { font-size: 16px; }.event-meta { font-size: 12px; }.event-actions { gap: 8px; }.status-filters button { padding: 7px 10px; }.description-text { -webkit-line-clamp: 2; } }
</style>
