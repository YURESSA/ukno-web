<template>
  <div class="section-container">
    <n-tabs v-model:value="eventListTab" type="line" animated>
      <n-tab-pane name="events" tab="События" />
      <n-tab-pane name="pending" :tab="`Ожидают модерации (${pendingCount})`" />
    </n-tabs>
    <div class="filter-panel">
      <n-space justify="space-between">
        <n-input v-model:value="searchQuery" placeholder="Поиск по названию..." clearable style="width: 300px" />
        <n-select v-if="eventListTab === 'events'" v-model:value="moderationFilter" :options="moderationOptions.filter(option => option.value !== 'pending')" clearable placeholder="Все статусы" style="width: 260px" />
      </n-space>
    </div>

    <n-data-table
      :loading="loading"
      :columns="columns"
      :data="excursions"
      :row-props="rowProps"
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
        <template v-if="['pending', 'approved'].includes(selectedItem.moderation_status)">
          <n-input v-model:value="returnComment" type="textarea" placeholder="Обязательный комментарий для возврата на доработку" />
          <n-button :loading="loading" :disabled="loading || !returnComment.trim()" type="warning" @click="handleReturn">Вернуть на доработку</n-button>
        </template>
      </n-space>
      <n-tabs v-model:value="activeTab" type="line" animated>
        <n-tab-pane name="main" tab="Основная информация">
          <n-form ref="formRef" :model="selectedItem" label-placement="top">
            <n-grid :cols="2" :x-gap="20">
              <n-form-item-gi span="2" label="Название события" required v-bind="fieldProps(selectedItem, 'event', 'title', 'selectedItem.title', isEdit)">
                <n-input v-model:value="selectedItem.title" placeholder="Введите название" />
              </n-form-item-gi>
              <n-form-item-gi span="2" label="Краткое описание" v-bind="fieldProps(selectedItem, 'event', 'short_description', 'selectedItem.short_description', isEdit)">
                <n-input v-model:value="selectedItem.short_description" type="textarea" :autosize="{ minRows: 2 }" />
              </n-form-item-gi>
              <n-form-item-gi span="2" label="Полное описание (с оформлением)" required v-bind="fieldProps(selectedItem, 'event', 'description', 'selectedItem.description', isEdit)">
                <Editor v-model="selectedItem.description" />
              </n-form-item-gi>
              <n-form-item-gi label="Категория" required v-bind="fieldProps(selectedItem, 'event', 'category_id', 'selectedItem.category_id', isEdit)">
                <n-select v-model:value="selectedItem.category_id" :options="categoryOptions" label-field="category_name" value-field="category_id" />
              </n-form-item-gi>
              <n-form-item-gi label="Формат" required v-bind="fieldProps(selectedItem, 'event', 'format_type_id', 'selectedItem.format_type_id', isEdit)">
                <n-select v-model:value="selectedItem.format_type_id" :options="formatOptions" label-field="format_type_name" value-field="format_type_id" />
              </n-form-item-gi>
              <n-form-item-gi label="Возраст" required v-bind="fieldProps(selectedItem, 'event', 'age_category_id', 'selectedItem.age_category_id', isEdit)">
                <n-select v-model:value="selectedItem.age_category_id" :options="ageOptions" label-field="age_category_name" value-field="age_category_id" />
              </n-form-item-gi>
              <n-form-item-gi label="Активна" v-bind="fieldProps(selectedItem, 'event', 'is_active', 'selectedItem.is_active', isEdit)">
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
        <n-tab-pane name="details" tab="Локация и Контакты">
          <n-grid :cols="2" :x-gap="20">
            <n-form-item-gi label="Продолжительность (мин)" required v-bind="fieldProps(selectedItem, 'event', 'duration', 'selectedItem.duration', isEdit)">
              <n-input-number v-model:value="selectedItem.duration" :precision="0" :min="0" style="width: 100%" />
            </n-form-item-gi>

            <n-form-item-gi label="Место" required v-bind="fieldProps(selectedItem, 'event', 'place', 'selectedItem.place', isEdit)">
              <n-input v-model:value="selectedItem.place" />
            </n-form-item-gi>

            <n-form-item-gi label="Проводит" v-bind="fieldProps(selectedItem, 'event', 'conducted_by', 'selectedItem.conducted_by', isEdit)">
              <n-input v-model:value="selectedItem.conducted_by" />
            </n-form-item-gi>

            <n-form-item-gi label="Часы работы" v-bind="fieldProps(selectedItem, 'event', 'working_hours', 'selectedItem.working_hours', isEdit)">
              <n-input v-model:value="selectedItem.working_hours" placeholder="С 10:00 до 20:00" />
            </n-form-item-gi>

            <n-form-item-gi label="Email" v-bind="fieldProps(selectedItem, 'event', 'contact_email', 'selectedItem.contact_email', isEdit)">
              <n-input v-model:value="selectedItem.contact_email" />
            </n-form-item-gi>

            <n-form-item-gi label="Telegram" v-bind="fieldProps(selectedItem, 'event', 'telegram', 'selectedItem.telegram', isEdit)">
              <n-input v-model:value="selectedItem.telegram" placeholder="@username" />
            </n-form-item-gi>

            <n-form-item-gi label="VK" v-bind="fieldProps(selectedItem, 'event', 'vk', 'selectedItem.vk', isEdit)">
              <n-input v-model:value="selectedItem.vk" placeholder="vk.com/..." />
            </n-form-item-gi>

            <n-form-item-gi label="До центра (метры)" v-bind="fieldProps(selectedItem, 'event', 'distance_to_center', 'selectedItem.distance_to_center', isEdit)">
              <n-input-number v-model:value="selectedItem.distance_to_center" :precision="1" style="width: 100%" :min="0" />
            </n-form-item-gi>

            <n-form-item-gi label="До остановки (мин)" v-bind="fieldProps(selectedItem, 'event', 'time_to_nearest_stop', 'selectedItem.time_to_nearest_stop', isEdit)">
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
            <n-form-item-gi v-if="selectedItem.iframe_url && !mapCoords" span="2" label="Старая ссылка на карту" v-bind="fieldProps(selectedItem, 'event', 'iframe_url', 'selectedItem.iframe_url', isEdit)">
              <n-input v-model:value="selectedItem.iframe_url" type="textarea" />
            </n-form-item-gi>
          </n-grid>
        </n-tab-pane>

        <n-tab-pane name="sessions" tab="Сессии (Даты)">
          <n-space vertical :size="20">
            <n-button type="primary" dashed block @click="addEmptySession">
              + Добавить новую дату/сессию
            </n-button>

            <n-card v-for="(session, index) in selectedItem.sessions" :key="session.session_id || index" size="small" bordered>
              <n-grid :cols="4" :x-gap="12">
                <n-form-item-gi span="2" label="Дата и время начала" required v-bind="fieldProps(session, 'session', 'start_datetime', 'sessions.' + index + '.start_datetime', false)">
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

                <n-form-item-gi label="Макс. чел." required v-bind="fieldProps(session, 'session', 'max_participants', 'sessions.' + index + '.max_participants', false)">
                  <n-input-number v-model:value="session.max_participants" :precision="0" :min="1" />
                </n-form-item-gi>

                <n-form-item-gi label="Стоимость" required v-bind="fieldProps(session, 'session', 'cost', 'sessions.' + index + '.cost', false)">
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
                    @click="handleDeleteSession(session, index)"
                  >
                    Удалить
                  </n-button>
                </n-space>
              </template>
            </n-card>
          </n-space>
        </n-tab-pane>

        <n-tab-pane name="photos" tab="Фотографии">
          <p>Добавьте хотя бы одну фотографию события.</p>
          <p v-if="submitted && !selectedItem.photos?.length" class="photo-error" role="alert">Добавьте хотя бы одну фотографию</p>
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
        </n-tab-pane>
      </n-tabs>

      <template #footer>
        <n-space justify="end">
          <n-button v-if="isEdit" type="error" ghost @click="handleDeleteExcursion">Удалить событие</n-button>
          <n-button @click="showModal = false">Отмена</n-button>
          <BaseButton :text="isEdit ? 'Сохранить' : 'Создать'" @click="handleSave" :loading="loading" />
          <BaseButton v-if="isEdit && selectedItem.moderation_status === 'pending'" text="Сохранить и одобрить" :loading="loading" @click="handleSave(true)" />
        </n-space>
      </template>
    </n-modal>
    <EventPreviewModal v-model:show="showPreview" :event="previewEvent" />
  </div>
</template>

<script setup>
import { useAdminValidation } from '@/composables/useAdminValidation'
import { validateAdmin, getAdminFieldError } from '@/utils/adminValidation'
import { getApiErrorMessage } from '@/utils/apiError'
import { normalizeEventPayload, sessionPayload } from '@/utils/eventForm'
import EventPreviewModal from '@/components/shared/EventPreviewModal.vue'
import MapPicker from '@/components/shared/MapPicker.vue'
import { moderationOptions, eventModeration } from '@/utils/eventModeration'
import { ref, computed, onMounted, inject, watch, h } from 'vue';
import { useDataStore, baseUrl } from '@/stores/counter';
import {
  NDataTable, NModal, NForm, NFormItemGi, NGrid, NInput, NDatePicker, NCard,
  NSelect, NButton, NSpace, NTag, NTabs, NTabPane, NUpload, NUploadDragger, useMessage, useDialog, NRadioGroup, NRadio, NInputNumber
} from 'naive-ui';
import BaseButton from '@/components/ui/button/BaseButton.vue';
import Editor from '@/components/ui/Editor.vue';

const { submitted, fieldProps, resetValidation, applyApiErrors } = useAdminValidation();

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
const pendingCount = computed(() => (store.adminExcursions.excursions || []).filter(item => item.moderation_status === 'pending').length);
const returnComment = ref('');
const uploadRef = ref(null);
const activeTab = ref('main');

const emptyEvent = () => ({
  title: '', description: '', short_description: '', duration: null,
  category_id: null, format_type_id: null, age_category_id: null,
  place: '', conducted_by: '', is_active: true, working_hours: '',
  contact_email: '', iframe_url: '', latitude: null, longitude: null, telegram: '', vk: '',
  distance_to_center: null, time_to_nearest_stop: null,
  photos: [], sessions: [],
});
const selectedItem = ref(emptyEvent());
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
      ? item.moderation_status === 'pending'
      : item.moderation_status !== 'pending' && (!moderationFilter.value || item.moderation_status === moderationFilter.value)
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

const columns = [
  { title: 'Автор', key: 'created_by', width: 220, ellipsis: { tooltip: true } },
  {
    title: 'Модерация', key: 'moderation_status', width: 150,
    render: row => h(NTag, { type: eventModeration(row.moderation_status).type }, { default: () => eventModeration(row.moderation_status).label }),
  },
  {
    title: 'ID',
    key: 'excursion_id',
    width: 60,
    sorter: (row1, row2) => row1.excursion_id - row2.excursion_id
  },
  {
    title: 'Название',
    key: 'title',
    width: 350,
    ellipsis: { tooltip: true },
    sorter: 'default'
  },
  {
    title: 'Краткое описание',
    key: 'short_description',
    width: 400,
    ellipsis: { tooltip: true }
  },
  {
    title: 'Ближайшая дата',
    key: 'next_date',
    width: 180,
    sorter: (row1, row2) => {
      const date1 = row1.sessions?.[0]?.start_datetime || '';
      const date2 = row2.sessions?.[0]?.start_datetime || '';
      return date1.localeCompare(date2);
    },
    render: (row) => {
      if (!row.sessions?.length) return '—';
      return row.sessions[0].start_datetime.replace(/:\d{2}$/, '');
    }
  },
  {
    title: 'Макс. чел.',
    key: 'max_participants',
    width: 120,
    align: 'center',
    render: (row) => {
      if (!row.sessions?.length) return '—';
      return row.sessions[0].max_participants;
    }
  },
  {
    title: 'Записано',
    key: 'booked',
    width: 120,
    align: 'center',
    render: (row) => {
      if (!row.sessions?.length) return '—';
      const booked = row.sessions[0].booked;
      const max = row.sessions[0].max_participants;

      const type = booked >= max ? 'error' : booked > 0 ? 'warning' : 'default';

      return h(NTag, { type, size: 'medium', round: true }, { default: () => booked });
    }
  },
  {
    title: 'Стоимость',
    key: 'price',
    width: 120,
    fixed: 'right',
    sorter: (row1, row2) => row1.sessions[0].cost - row2.sessions[0].cost,
    render: (row) => {
      if (!row.sessions?.length) return '—';
      const price = row.sessions[0].cost;
      return `${parseFloat(price).toLocaleString()} ₽`;
    }
  }
];

const rowProps = (row) => ({
  style: 'cursor: pointer',
  onClick: () => {
    returnComment.value = '';
    activeTab.value = 'main';
    isEdit.value = true;
    newExcursionPhotos.value = [];
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
  newExcursionPhotos.value = [];
  selectedItem.value = emptyEvent();
  activeTab.value = 'main';
  showModal.value = true;
});

async function handleSave(approve = false) {
  approve = approve === true;
  if (loading.value) return;
  submitted.value = true;
  const validationError = validateAdmin(selectedItem.value, 'event', isEdit.value);
  if (validationError) {
    const mainFields = ['title', 'description', 'category_id', 'format_type_id', 'age_category_id', 'is_active'];
    const detailFields = ['place', 'duration', 'contact_email', 'distance_to_center', 'time_to_nearest_stop'];
    activeTab.value = mainFields.some(key => getAdminFieldError(selectedItem.value, 'event', key))
      ? 'main' : detailFields.some(key => getAdminFieldError(selectedItem.value, 'event', key)) ? 'details' : 'sessions';
    return message.error(validationError);
  }
  if ((!isEdit.value && !newExcursionPhotos.value.length) || (approve && !selectedItem.value.photos?.length)) {
    activeTab.value = 'photos';
    return message.error('Добавьте хотя бы одну фотографию события');
  }
  try {
    loading.value = true;
      const selectedCategory = categoryOptions.value.find(c => c.category_id === selectedItem.value.category_id);
      const selectedFormat = formatOptions.value.find(f => f.format_type_id === selectedItem.value.format_type_id);
      const selectedAge = ageOptions.value.find(a => a.age_category_id === selectedItem.value.age_category_id);

      const payload = normalizeEventPayload({
        title: selectedItem.value.title,
        short_description: selectedItem.value.short_description,
        description: selectedItem.value.description,
        duration: selectedItem.value.duration,
        place: selectedItem.value.place,
        conducted_by: selectedItem.value.conducted_by,
        is_active: selectedItem.value.is_active,
        working_hours: selectedItem.value.working_hours,
        contact_email: selectedItem.value.contact_email,
        iframe_url: selectedItem.value.iframe_url,
        latitude: selectedItem.value.latitude,
        longitude: selectedItem.value.longitude,
        telegram: selectedItem.value.telegram,
        vk: selectedItem.value.vk,
        distance_to_center: selectedItem.value.distance_to_center,
        time_to_nearest_stop: selectedItem.value.time_to_nearest_stop,
        category: selectedCategory ? selectedCategory.category_name : '',
        format_type: selectedFormat ? selectedFormat.format_type_name : '',
        age_category: selectedAge ? selectedAge.age_category_name : '',
        sessions: (selectedItem.value.sessions || []).map(s => ({
        start_datetime: s.start_datetime,
        max_participants: s.max_participants,
        cost: s.cost
      }))
      });
    if (isEdit.value) {
      delete payload.sessions;
      for (const session of selectedItem.value.sessions || []) await persistSession(session);
      if (approve) await store.ApproveEvent(selectedItem.value.excursion_id, payload);
      else await store.PatchExcursion(selectedItem.value.excursion_id, payload);
      message.success(approve ? 'Событие одобрено и опубликовано' : 'Обновлено');
    } else {
      const formData = new FormData();

      formData.append('data', JSON.stringify(payload));

      newExcursionPhotos.value.forEach(file => {
        formData.append('photos', file);
      });

      await store.PostNewExcursion(formData);
      message.success('Событие полностью создано');
      newExcursionPhotos.value = [];
    }

    showModal.value = false;
    await store.FetchAdminExcursion();
  } catch (e) {
    console.error(e);
    applyApiErrors(e, selectedItem.value);
    const fields = Object.keys(e.response?.data?.errors || {});
    if (fields.some(key => ['title', 'short_description', 'description', 'category', 'format_type', 'age_category', 'is_active'].includes(key))) activeTab.value = 'main';
    else if (fields.length) activeTab.value = 'details';
    message.error(getApiErrorMessage(e, 'Ошибка при сохранении'));
  } finally {
    loading.value = false;
  }
}

async function handleReturn() {
  if (loading.value || !returnComment.value.trim()) return;
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

async function persistSession(session) {
  const payload = sessionPayload(session);
  const serialized = JSON.stringify(payload);
  if (session.session_id && savedSessions.get(session.session_id) === serialized) return;
  if (session.session_id) {
    await store.PatchExcursionSession(selectedItem.value.excursion_id, session.session_id, payload);
  } else {
    const response = await store.PostExcursionSession(selectedItem.value.excursion_id, payload);
    session.session_id = response.data.session_id;
  }
  savedSessions.set(session.session_id, serialized);
}

async function handleSaveSession(session) {
  if (loading.value) return;
  submitted.value = true;
  const validationError = validateAdmin(session, 'session', false);
  if (validationError) return message.error(validationError);
  if (!session.start_datetime) {
    message.error('Выберите дату и время');
    return;
  }

  try {
    loading.value = true;
    await persistSession(session);
    message.success('Сессия сохранена');
    await store.FetchAdminExcursion();
  } catch (e) {
    message.error(getApiErrorMessage(e, 'Ошибка при работе с сессией'));
  } finally {
    loading.value = false;
  }
}

async function handleDeleteSession(session, index) {
  if (!isEdit.value || !session.session_id) {
    selectedItem.value.sessions.splice(index, 1);
    return;
  }

  dialog.warning({
    title: 'Удаление сессии',
    content: 'Удалить эту дату проведения из базы данных?',
    positiveText: 'Удалить',
    onPositiveClick: async () => {
      try {
        await store.DeleteExcursionSession(selectedItem.value.excursion_id, session.session_id);
        message.success('Сессия удалена из базы');
        selectedItem.value.sessions.splice(index, 1);
      } catch (e) {
        message.error(getApiErrorMessage(e, 'Ошибка при удалении'));
      }
    }
  });
}

const newExcursionPhotos = ref([]);

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
      const isDuplicate = newExcursionPhotos.value.some(
        f => f.name === file.file.name && f.size === file.file.size
      );

      if (!isDuplicate) {
        newExcursionPhotos.value.push(file.file);
        selectedItem.value.photos.push({
          photo_id: Date.now() + Math.random(),
          photo_url: URL.createObjectURL(file.file),
          isLocal: true,
          fileName: file.file.name
        });
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
  if (selectedItem.value.photos.length <= 1) return message.error('У события должна остаться хотя бы одна фотография. Сначала добавьте замену.');
  const photoIndex = selectedItem.value.photos.findIndex(p => p.photo_id === photoId);
  if (photoIndex === -1) return;

  const photo = selectedItem.value.photos[photoIndex];

  if (photo.isLocal) {
    newExcursionPhotos.value = newExcursionPhotos.value.filter(
      file => file.name !== photo.fileName
    );
    selectedItem.value.photos.splice(photoIndex, 1);
    message.info('Фото удалено из очереди');
    return;
  }

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
  Promise.all([store.FetchCategories(), store.FetchFormat(), store.FetchAge()]).catch(e => message.error(getApiErrorMessage(e, 'Ошибка загрузки справочников')));
});

watch(showModal, resetValidation);
</script>

<style scoped>
.photo-error { color: #d03050; }
.photo-grid {
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
