<template>
  <div class="section-container">
    <n-tabs v-model:value="eventListTab" type="line" animated>
      <n-tab-pane name="events" tab="События" />
      <n-tab-pane name="pending" :tab="`Ожидают модерации (${pendingCount})`" />
    </n-tabs>
    <div class="event-filters">
      <n-input class="event-search" v-model:value="searchQuery" placeholder="Поиск по названию..." clearable />
      <n-select v-if="eventListTab === 'events'" class="event-status-filter" v-model:value="moderationFilter" :options="moderationOptions.filter(option => option.value !== 'pending')" clearable placeholder="Все статусы" />
    </div>

    <n-data-table
      :loading="loading"
      :columns="columns"
      :data="excursions"
      :row-key="row => row.excursion_id"
      :row-props="rowProps"
      :scroll-x="tableWidth"
      :pagination="{ pageSize: 10 }"
    />

    <n-modal
      v-model:show="showModal"
      preset="card"
      style="width: 900px"
      :title="isEdit ? 'Редактирование события' : 'Новое событие'"
    >
      <n-space vertical style="margin-bottom: 16px">
        <p v-if="isEdit">Автор: {{ selectedItem.created_by || 'Не указан' }}</p>
        <n-button @click="showPreview = true">Предпросмотр события</n-button>
        <n-tag v-if="isEdit" :type="eventModeration(selectedItem.moderation_status).type">{{ eventModeration(selectedItem.moderation_status).label }}</n-tag>
        <p v-if="selectedItem.moderation_comment">Комментарий: {{ selectedItem.moderation_comment }}</p>
        <template v-if="canModerateSelected && ['pending', 'approved'].includes(selectedItem.moderation_status)">
          <n-input v-model:value="returnComment" type="textarea" placeholder="Обязательный комментарий для возврата на доработку" />
          <n-button :loading="loading" :disabled="loading || !returnComment.trim()" type="warning" @click="handleReturn">Вернуть на доработку</n-button>
        </template>
      </n-space>
      <n-alert v-if="!selectedItem.sessions?.length" class="session-warning" type="error" title="У события нет сессий">
        <n-button v-if="activeTab !== 'sessions'" text type="error" @click="activeTab = 'sessions'">
          Перейти к сессиям
        </n-button>
        <span v-else>Добавьте дату и время проведения.</span>
      </n-alert>
      <n-tabs v-model:value="activeTab" type="line" animated>
        <n-tab-pane name="main" tab="Основная информация" display-directive="show">
          <n-form ref="formRef" :model="selectedItem" label-placement="top">
            <n-grid :cols="2" :x-gap="20">
              <n-form-item-gi span="2" label="Название события" required v-bind="fieldProps(selectedItem, 'event', 'title', isEdit)">
                <n-input v-model:value="selectedItem.title" placeholder="Введите название" />
              </n-form-item-gi>
              <n-form-item-gi span="2" label="Краткое описание" v-bind="fieldProps(selectedItem, 'event', 'short_description', isEdit)">
                <n-input v-model:value="selectedItem.short_description" type="textarea" :autosize="{ minRows: 2 }" />
              </n-form-item-gi>
              <n-form-item-gi span="2" label="Полное описание (с оформлением)" required v-bind="fieldProps(selectedItem, 'event', 'description', isEdit)">
                <Editor v-model="selectedItem.description" />
              </n-form-item-gi>
              <n-form-item-gi label="Категория" required v-bind="fieldProps(selectedItem, 'event', 'category_id', isEdit)">
                <n-select v-model:value="selectedItem.category_id" :options="categoryOptions" label-field="category_name" value-field="category_id" />
              </n-form-item-gi>
              <n-form-item-gi label="Формат" required v-bind="fieldProps(selectedItem, 'event', 'format_type_id', isEdit)">
                <n-select v-model:value="selectedItem.format_type_id" :options="formatOptions" label-field="format_type_name" value-field="format_type_id" />
              </n-form-item-gi>
              <n-form-item-gi label="Возраст" required v-bind="fieldProps(selectedItem, 'event', 'age_category_id', isEdit)">
                <n-select v-model:value="selectedItem.age_category_id" :options="ageOptions" label-field="age_category_name" value-field="age_category_id" />
              </n-form-item-gi>
              <n-form-item-gi label="Активна" v-bind="fieldProps(selectedItem, 'event', 'is_active', isEdit)">
                <n-radio-group v-model:value="selectedItem.is_active" name="is_active_group">
                  <n-space>
                    <n-radio :value="true">Да</n-radio>
                    <n-radio :value="false">Нет</n-radio>
                  </n-space>
                </n-radio-group>
              </n-form-item-gi>
            </n-grid>
          </n-form>
        </n-tab-pane>
        <n-tab-pane name="details" tab="Локация и Контакты" display-directive="show">
          <n-grid :cols="2" :x-gap="20">
            <n-form-item-gi label="Продолжительность (мин)" required v-bind="fieldProps(selectedItem, 'event', 'duration', isEdit)">
              <n-input-number v-model:value="selectedItem.duration" :precision="0" :min="0" style="width: 100%" />
            </n-form-item-gi>

            <n-form-item-gi label="Место" required v-bind="fieldProps(selectedItem, 'event', 'place', isEdit)">
              <n-input v-model:value="selectedItem.place" />
            </n-form-item-gi>

            <n-form-item-gi label="Проводит" v-bind="fieldProps(selectedItem, 'event', 'conducted_by', isEdit)">
              <n-input v-model:value="selectedItem.conducted_by" />
            </n-form-item-gi>

            <n-form-item-gi label="Часы работы" v-bind="fieldProps(selectedItem, 'event', 'working_hours', isEdit)">
              <n-input v-model:value="selectedItem.working_hours" placeholder="С 10:00 до 20:00" />
            </n-form-item-gi>

            <n-form-item-gi label="Email" v-bind="fieldProps(selectedItem, 'event', 'contact_email', isEdit)">
              <n-input v-model:value="selectedItem.contact_email" />
            </n-form-item-gi>

            <n-form-item-gi label="Telegram" v-bind="fieldProps(selectedItem, 'event', 'telegram', isEdit)">
              <n-input v-model:value="selectedItem.telegram" placeholder="@username" />
            </n-form-item-gi>

            <n-form-item-gi label="VK" v-bind="fieldProps(selectedItem, 'event', 'vk', isEdit)">
              <n-input v-model:value="selectedItem.vk" placeholder="vk.com/..." />
            </n-form-item-gi>

            <n-form-item-gi label="До центра (метры)" v-bind="fieldProps(selectedItem, 'event', 'distance_to_center', isEdit)">
              <n-input-number v-model:value="selectedItem.distance_to_center" :precision="1" style="width: 100%" :min="0" />
            </n-form-item-gi>

            <n-form-item-gi label="До остановки (мин)" v-bind="fieldProps(selectedItem, 'event', 'time_to_nearest_stop', isEdit)">
              <n-input-number v-model:value="selectedItem.time_to_nearest_stop" style="width: 100%" :min="0" />
            </n-form-item-gi>

            <n-form-item-gi span="2" label="Местоположение на карте">
              <MapPicker
                v-if="showModal && activeTab === 'details'"
                :key="selectedItem.excursion_id || 'new-event'"
                map-id="admin-event-map"
                style="width: 100%"
                :initial-coords="mapCoords"
                @update:coords="onCoordsUpdate"
              />
            </n-form-item-gi>
            <n-form-item-gi v-if="selectedItem.iframe_url && !mapCoords" span="2" label="Старая ссылка на карту" v-bind="fieldProps(selectedItem, 'event', 'iframe_url', isEdit)">
              <n-input v-model:value="selectedItem.iframe_url" type="textarea" />
            </n-form-item-gi>
          </n-grid>
        </n-tab-pane>

        <n-tab-pane name="sessions" tab="Сессии" display-directive="show">
          <n-space vertical :size="20">
            <n-button type="primary" dashed block @click="addEmptySession">
              + Добавить новую дату/сессию
            </n-button>

            <n-card v-for="(session, index) in selectedItem.sessions" :key="rowKey(session)" size="small" bordered>
              <n-grid :cols="4" :x-gap="12">
                <n-form-item-gi span="2" label="Дата и время начала" required v-bind="fieldProps(session, 'session', 'start_datetime', false, selectedItem, 'sessions.' + index + '.start_datetime')">
                  <n-date-picker
                    v-model:formatted-value="session.start_datetime"
                    value-format="yyyy-MM-dd HH:mm:00"
                    format="yyyy-MM-dd HH:mm"
                    type="datetime"
                    :actions="['now', 'confirm']"
                    @update:formatted-value="(val) => session.start_datetime = val"
                    style="width: 100%"
                  />
                </n-form-item-gi>

                <n-form-item-gi label="Макс. чел." required v-bind="fieldProps(session, 'session', 'max_participants', false, selectedItem, 'sessions.' + index + '.max_participants')">
                  <n-input-number v-model:value="session.max_participants" :precision="0" :min="1" />
                </n-form-item-gi>

                <n-form-item-gi label="Стоимость" required v-bind="fieldProps(session, 'session', 'cost', false, selectedItem, 'sessions.' + index + '.cost')">
                  <n-input-number v-model:value="session.cost" :min="0" :step="50" placeholder="100">
                    <template #suffix>₽</template>
                  </n-input-number>
                </n-form-item-gi>
              </n-grid>

              <template #footer>
                <n-space justify="end">
                  <n-button
                    v-if="isEdit"
                    size="small"
                    type="primary"
                    @click="handleSaveSession(session)"
                    :loading="loading"
                  >
                    {{ session.session_id ? 'Обновить сессию' : 'Сохранить в базу' }}
                  </n-button>

                  <n-button
                    size="small"
                    type="error"
                    ghost
                    @click="handleDeleteSession(session)"
                  >
                    Удалить
                  </n-button>
                </n-space>
              </template>
            </n-card>
          </n-space>
        </n-tab-pane>

        <n-tab-pane name="photos" tab="Фотографии" display-directive="show">
          <n-form-item :show-label="false" v-bind="fieldProps(selectedItem, 'event', 'photos', isEdit && !approving)">
            <div class="photo-grid">
              <div v-for="photo in selectedItem.photos" :key="photo.photo_id" class="photo-item">
                <img
                  :src="photo.isLocal ? photo.photo_url : `${baseUrl}${photo.photo_url}`"
                  alt="event"
                >
                <n-button
                  class="delete-btn"
                  type="error"
                  size="tiny"
                  circle
                  @click="handleDeletePhoto(photo.photo_id)"
                >
                  ✕
                </n-button>
              </div>
              <n-upload
                multiple
                accept="image/*"
                ref="uploadRef"
                :show-file-list="false"
                :custom-request="handleUploadPhoto"
              >
                <n-upload-dragger>Добавить фото</n-upload-dragger>
              </n-upload>
            </div>
          </n-form-item>
        </n-tab-pane>
      </n-tabs>

      <template #footer>
        <n-space justify="end">
          <n-button v-if="isEdit" type="error" ghost @click="handleDeleteExcursion">Удалить событие</n-button>
          <n-button @click="showModal = false">Отмена</n-button>
          <BaseButton :text="isEdit ? 'Сохранить' : 'Создать'" @click="handleSave" :loading="loading" />
          <BaseButton v-if="canModerateSelected && isAwaitingModeration(selectedItem)" text="Сохранить и одобрить" :loading="loading" @click="handleSave(true)" />
        </n-space>
      </template>
    </n-modal>
    <EventPreviewModal v-model:show="showPreview" :event="previewEvent" />
  </div>
</template>

<script setup>
import { useAdminValidation } from '@/composables/useAdminValidation'
import { getAdminFieldError } from '@/utils/adminValidation'
import { getApiErrorMessage } from '@/utils/apiError'
import { normalizeEventPayload, sessionPayload } from '@/utils/eventForm'
import EventPreviewModal from '@/components/shared/EventPreviewModal.vue'
import MapPicker from '@/components/shared/MapPicker.vue'
import { moderationOptions, eventModeration } from '@/utils/eventModeration'
import { ref, computed, onMounted, inject, watch, h } from 'vue';
import { useDataStore, baseUrl } from '@/stores/counter';
import {
  NAlert, NDataTable, NModal, NForm, NFormItem, NFormItemGi, NGrid, NInput, NDatePicker, NCard,
  NSelect, NButton, NSpace, NTag, NTabs, NTabPane, NUpload, NUploadDragger, useMessage, useDialog, NRadioGroup, NRadio, NInputNumber
} from 'naive-ui';
import BaseButton from '@/components/ui/button/BaseButton.vue';
import Editor from '@/components/ui/Editor.vue';

const { fieldProps, submitValidation, resetValidation, applyApiErrors, rowKey } = useAdminValidation();

const store = useDataStore();
const message = useMessage();
const dialog = useDialog();
const loading = ref(false);
const showModal = ref(false);
const showPreview = ref(false);
const savedSessions = new Map();
const isEdit = ref(false);
const searchQuery = ref('');
const moderationFilter = ref(null);
const eventListTab = ref('events');
const pendingCount = computed(() => (store.adminExcursions.excursions || []).filter(isAwaitingModeration).length);
const returnComment = ref('');
const uploadRef = ref(null);
const activeTab = ref('main');
const approving = ref(false);

const eventFieldAliases = {
  category: 'category_id',
  format_type: 'format_type_id',
  age_category: 'age_category_id',
};
const mainFields = ['title', 'short_description', 'description', 'category_id', 'format_type_id', 'age_category_id', 'is_active'];

function openErrorTab(paths) {
  const tabs = paths.map(path => {
    if (mainFields.includes(path)) return 'main';
    if (path === 'photos') return 'photos';
    if (path === 'sessions' || path.startsWith('sessions.')) return 'sessions';
    return 'details';
  });
  if (!tabs.includes(activeTab.value)) {
    activeTab.value = ['main', 'details', 'sessions', 'photos'].find(tab => tabs.includes(tab)) || activeTab.value;
  }
}

const emptyEvent = () => ({
  title: '', description: '', short_description: '', duration: null,
  category_id: null, format_type_id: null, age_category_id: null,
  place: '', conducted_by: '', is_active: true, working_hours: '',
  contact_email: '', iframe_url: '', latitude: null, longitude: null, telegram: '', vk: '',
  distance_to_center: null, time_to_nearest_stop: null,
  photos: [], sessions: [],
});
const selectedItem = ref(emptyEvent());
const authorRoles = ref(new Map());
const normalizeEmail = email => email?.trim().toLowerCase();
const canModerateSelected = computed(() => isEdit.value && eventRequiresModeration(selectedItem.value));

function eventRequiresModeration(event) {
  const role = authorRoles.value.get(normalizeEmail(event.created_by));
  return Boolean(role && role !== 'admin');
}

function isAwaitingModeration(event) {
  return eventRequiresModeration(event) && event.moderation_status === 'pending';
}

const mapCoords = computed(() =>
  Number.isFinite(selectedItem.value.latitude) && Number.isFinite(selectedItem.value.longitude)
    ? [selectedItem.value.latitude, selectedItem.value.longitude]
    : null
);
function onCoordsUpdate({ latitude, longitude }) {
  selectedItem.value.latitude = latitude;
  selectedItem.value.longitude = longitude;
}

const excursions = computed(() => {
  const allExcursions = (store.adminExcursions.excursions || []).filter(item =>
    eventListTab.value === 'pending'
      ? isAwaitingModeration(item)
      : !isAwaitingModeration(item) && (!moderationFilter.value || item.moderation_status === moderationFilter.value)
  );

  if (!searchQuery.value) return allExcursions;

  const query = searchQuery.value.toLowerCase();
  return allExcursions.filter(item =>
    item.title.toLowerCase().includes(query) ||
    item.excursion_id.toString().includes(query)
  );
});
const categoryOptions = computed(() => store.getCategories || []);
const formatOptions = computed(() => store.getFormat);
const ageOptions = computed(() => store.getAge);
const previewEvent = computed(() => ({
  ...selectedItem.value,
  category: categoryOptions.value.find(item => item.category_id === selectedItem.value.category_id),
  format_type: (formatOptions.value || []).find(item => item.format_type_id === selectedItem.value.format_type_id),
  age_category: (ageOptions.value || []).find(item => item.age_category_id === selectedItem.value.age_category_id),
}));

function displaySession(row) {
  const sessions = row.sessions || [];
  const now = Date.now();
  // The API returns sessions in chronological order.
  return sessions.find(session => new Date(session.start_datetime).getTime() >= now) || sessions.at(-1);
}

const columns = [
  { title: 'Автор', key: 'created_by', width: 176, ellipsis: { tooltip: true } },
  {
    title: 'Модерация', key: 'moderation_status', width: 134,
    render: row => h(NTag, { type: eventModeration(row.moderation_status).type }, { default: () => eventModeration(row.moderation_status).label }),
  },
  {
    title: 'ID',
    key: 'excursion_id',
    width: 64,
    sorter: (row1, row2) => row1.excursion_id - row2.excursion_id
  },
  {
    title: 'Название',
    key: 'title',
    width: 228,
    ellipsis: { tooltip: true },
    sorter: 'default'
  },
  {
    title: 'Краткое описание',
    key: 'short_description',
    width: 248,
    ellipsis: { tooltip: true }
  },
  {
    title: 'Сессии',
    key: 'sessions',
    width: 132,
    sorter: (row1, row2) => Number(Boolean(row1.sessions?.length)) - Number(Boolean(row2.sessions?.length)),
    render: row => {
      const hasSessions = Boolean(row.sessions?.length);
      return h(NTag, { type: hasSessions ? 'success' : 'error', size: 'small', bordered: false },
        () => hasSessions ? 'Есть сессии' : 'Нет сессий');
    }
  },
  {
    title: 'Мест',
    key: 'max_participants',
    width: 66,
    align: 'center',
    render: row => displaySession(row)?.max_participants ?? '—',
  },
  {
    title: 'Записано',
    key: 'booked',
    width: 88,
    align: 'center',
    render: (row) => {
      const session = displaySession(row);
      if (!session) return '—';
      const { booked, max_participants: max } = session;

      const type = booked >= max ? 'error' : booked > 0 ? 'warning' : 'default';

      return h(NTag, { type, size: 'medium', round: true }, { default: () => booked });
    }
  },
  {
    title: 'Стоимость',
    key: 'price',
    width: 124,
    sorter: (row1, row2) => (displaySession(row1)?.cost ?? -1) - (displaySession(row2)?.cost ?? -1),
    render: (row) => {
      const price = displaySession(row)?.cost;
      return price == null ? '—' : `${Number(price).toLocaleString('ru-RU')} ₽`;
    }
  }
];
const tableWidth = columns.reduce((width, column) => width + column.width, 0);

const rowProps = (row) => ({
  style: 'cursor: pointer',
  onClick: () => {
    returnComment.value = '';
    activeTab.value = 'main';
    isEdit.value = true;
    uploadRef.value?.clear();

    const fixedSessions = row.sessions?.map(s => ({
      ...s,
      start_datetime: s.start_datetime
        ? s.start_datetime.replace('T', ' ').replace(/:\d{2}$/, ':00')
        : null,
      cost: Number(s.cost) || 0
    })) || [];

    selectedItem.value = {
      ...row,
      category_id: row.category?.category_id,
      format_type_id: row.format_type?.format_type_id,
      age_category_id: row.age_category?.age_category_id,
      sessions: fixedSessions
    };
    savedSessions.clear();
    fixedSessions.forEach(s => savedSessions.set(s.session_id, JSON.stringify(sessionPayload(s))));
    showModal.value = true;
  }
});

const addTrigger = inject('admin-add-event');
watch(addTrigger, () => {
  isEdit.value = false;
  selectedItem.value = emptyEvent();
  activeTab.value = 'main';
  showModal.value = true;
});

async function handleSave(approve = false) {
  approve = approve === true;
  if (loading.value) return;
  approving.value = approve;
  const event = selectedItem.value;
  const issues = submitValidation(event, 'event', isEdit.value);
  const paths = issues.map(issue => issue.path);
  if (approve && getAdminFieldError(event, 'event', 'photos')) paths.push('photos');
  if (paths.length) {
    openErrorTab(paths);
    return;
  }
  let savingSession;
  try {
    loading.value = true;
    const selectedCategory = categoryOptions.value.find(c => c.category_id === event.category_id);
    const selectedFormat = formatOptions.value.find(f => f.format_type_id === event.format_type_id);
    const selectedAge = ageOptions.value.find(a => a.age_category_id === event.age_category_id);

    const payload = normalizeEventPayload({
      title: event.title,
      short_description: event.short_description,
      description: event.description,
      duration: event.duration,
      place: event.place,
      conducted_by: event.conducted_by,
      is_active: event.is_active,
      working_hours: event.working_hours,
      contact_email: event.contact_email,
      iframe_url: event.iframe_url,
      latitude: event.latitude,
      longitude: event.longitude,
      telegram: event.telegram,
      vk: event.vk,
      distance_to_center: event.distance_to_center,
      time_to_nearest_stop: event.time_to_nearest_stop,
      category: selectedCategory ? selectedCategory.category_name : '',
      format_type: selectedFormat ? selectedFormat.format_type_name : '',
      age_category: selectedAge ? selectedAge.age_category_name : '',
      sessions: (event.sessions || []).map(session => ({
        start_datetime: session.start_datetime,
        max_participants: session.max_participants,
        cost: session.cost
      })),
    });
    if (isEdit.value) {
      delete payload.sessions;
      for (const session of event.sessions || []) {
        savingSession = session;
        if (submitValidation(session, 'session').length) {
          activeTab.value = 'sessions';
          return;
        }
        await persistSession(event.excursion_id, session);
      }
      savingSession = undefined;
      if (approve) await store.ApproveEvent(event.excursion_id, payload);
      else await store.PatchExcursion(event.excursion_id, payload);
      message.success(approve ? 'Событие одобрено и опубликовано' : 'Обновлено');
    } else {
      const formData = new FormData();

      formData.append('data', JSON.stringify(payload));

      event.photos.forEach(photo => {
        formData.append('photos', photo.file);
      });

      await store.PostNewExcursion(formData);
      message.success('Событие полностью создано');
    }

    showModal.value = false;
    await store.FetchAdminExcursion();
  } catch (e) {
    const { paths, message: feedback } = applyApiErrors(e, savingSession || event, 'Ошибка при сохранении', eventFieldAliases);
    if (showModal.value && savingSession) activeTab.value = 'sessions';
    else if (paths.length) openErrorTab(paths);
    if (feedback) message.error(feedback);
  } finally {
    loading.value = false;
  }
}

async function handleReturn() {
  if (!canModerateSelected.value || loading.value || !returnComment.value.trim()) return;
  loading.value = true;
  try {
    await store.ReturnEvent(selectedItem.value.excursion_id, returnComment.value.trim());
    showModal.value = false;
    message.success('Событие возвращено на доработку');
    await store.FetchAdminExcursion();
  } catch (error) {
    message.error(getApiErrorMessage(error, 'Не удалось вернуть событие'));
  } finally {
    loading.value = false;
  }
}

function addEmptySession() {
  if (!selectedItem.value.sessions) selectedItem.value.sessions = [];
  selectedItem.value.sessions.unshift({
    start_datetime: null,
    max_participants: 10,
    cost: 0,
  });
}

async function persistSession(eventId, session) {
  const payload = sessionPayload(session);
  const serialized = JSON.stringify(payload);
  if (session.session_id && savedSessions.get(session.session_id) === serialized) return;
  if (session.session_id) {
    await store.PatchExcursionSession(eventId, session.session_id, payload);
  } else {
    const response = await store.PostExcursionSession(eventId, payload);
    session.session_id = response.data.session_id;
  }
  savedSessions.set(session.session_id, serialized);
}

async function handleSaveSession(session) {
  if (loading.value) return;
  if (submitValidation(session, 'session').length) return;

  try {
    loading.value = true;
    await persistSession(selectedItem.value.excursion_id, session);
    message.success('Сессия сохранена');
    await store.FetchAdminExcursion();
  } catch (e) {
    const { message: feedback } = applyApiErrors(e, session, 'Ошибка при работе с сессией');
    if (feedback) message.error(feedback);
  } finally {
    loading.value = false;
  }
}

function handleDeleteSession(session) {
  const event = selectedItem.value;
  const removeSession = () => {
    event.sessions = event.sessions.filter(item => item !== session);
  };
  if (!isEdit.value || !session.session_id) {
    removeSession();
    return;
  }

  dialog.warning({
    title: 'Удаление сессии',
    content: 'Удалить эту дату проведения из базы данных?',
    positiveText: 'Удалить',
    onPositiveClick: async () => {
      try {
        await store.DeleteExcursionSession(event.excursion_id, session.session_id);
        removeSession();
        savedSessions.delete(session.session_id);
        message.success('Сессия удалена из базы');
      } catch (e) {
        message.error(getApiErrorMessage(e, 'Ошибка при удалении'));
        return false;
      }
      await store.FetchAdminExcursion().catch(e => message.error(getApiErrorMessage(e, 'Не удалось обновить список событий')));
    }
  });
}

async function handleUploadPhoto({ file, onFinish, onError }) {
  try {
    if (isEdit.value) {
      loading.value = true;
      await store.PostExcursionPhoto(selectedItem.value.excursion_id, file.file);

      await store.FetchAdminExcursion();
      const updated = store.adminExcursions.excursions.find(
        e => e.excursion_id === selectedItem.value.excursion_id
      );
      if (updated) selectedItem.value.photos = updated.photos;

      message.success('Фото сохранено в базу');
    } else {
      const photos = selectedItem.value.photos;
      const isDuplicate = photos.some(
        photo => photo.file.name === file.file.name && photo.file.size === file.file.size
      );

      if (!isDuplicate) {
        const photoUrl = URL.createObjectURL(file.file);
        selectedItem.value.photos = [...photos, {
          photo_id: photoUrl,
          photo_url: photoUrl,
          isLocal: true,
          file: file.file,
        }];
      }
    }

    onFinish();

    uploadRef.value?.clear();

  } catch (e) {
    console.error(e);
    message.error(getApiErrorMessage(e, 'Ошибка при загрузке файла'));
    onError();
  } finally {
    loading.value = false;
  }
}

async function handleDeletePhoto(photoId) {
  const photo = selectedItem.value.photos.find(p => p.photo_id === photoId);
  if (!photo) return;

  if (photo.isLocal) {
    URL.revokeObjectURL(photo.photo_url);
    selectedItem.value.photos = selectedItem.value.photos.filter(p => p !== photo);
    message.info('Фото удалено из очереди');
    return;
  }
  if (selectedItem.value.photos.length <= 1) return message.error('У события должна остаться хотя бы одна фотография. Сначала добавьте замену.');

  dialog.warning({
    title: 'Удаление',
    content: 'Удалить фото из базы данных?',
    positiveText: 'Удалить',
    onPositiveClick: async () => {
      try {
        await store.DeleteExcursionPhoto(selectedItem.value.excursion_id, photoId);
        selectedItem.value.photos = selectedItem.value.photos.filter(p => p.photo_id !== photoId);
        message.success('Удалено');
      } catch (e) {
        message.error(getApiErrorMessage(e, 'Ошибка удаления'));
      }
    }
  });
}

function handleDeleteExcursion() {
  dialog.warning({
    title: 'Удаление',
    content: 'Вы уверены?',
    positiveText: 'Удалить',
    onPositiveClick: async () => {
      await store.deleteAdminExcursion(selectedItem.value.excursion_id);
      showModal.value = false;
      await store.FetchAdminExcursion();
    }
  });
}

onMounted(() => {
  store.FetchAdminExcursion().catch(e => message.error(getApiErrorMessage(e, 'Ошибка загрузки событий')));
  store.FetchUsers().then(() => {
    authorRoles.value = new Map(store.getUsers.map(user => [normalizeEmail(user.email), user.role]));
  }).catch(e => message.error(getApiErrorMessage(e, 'Не удалось загрузить роли авторов')));
  Promise.all([store.FetchCategories(), store.FetchFormat(), store.FetchAge()]).catch(e => message.error(getApiErrorMessage(e, 'Ошибка загрузки справочников')));
});

watch(showModal, (open) => {
  if (!open) {
    for (const photo of selectedItem.value.photos || []) {
      if (photo.isLocal) URL.revokeObjectURL(photo.photo_url);
    }
  }
  approving.value = false;
  resetValidation();
});
</script>

<style scoped>
.event-filters {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 12px;
  margin: 12px 0;
}

.event-search {
  width: min(300px, 100%);
}

.event-status-filter {
  width: min(260px, 100%);
}

.session-warning {
  margin-bottom: 12px;
}

.photo-grid {
  width: 100%;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 15px;
  margin-top: 10px;
}

.photo-item {
  position: relative;
  height: 120px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e0e0e0;
}

.photo-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-item .delete-btn {
  position: absolute;
  top: 5px;
  right: 5px;
  background: rgba(255, 255, 255, 0.8);
  color: #d03050;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.photo-item .delete-btn:hover {
  background: rgba(255, 255, 255, 1);
}

.upload-dragger-compact {
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  border-radius: 8px;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: rgba(0, 0, 0, 0.45);
}

.photo-item .delete-btn {
  position: absolute;
  top: 5px;
  right: 5px;
  z-index: 10;
  background: rgba(255, 255, 255, 0.8);
  color: #d03050;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}
</style>
