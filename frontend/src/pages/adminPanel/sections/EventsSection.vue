<template>
  <div class="section-container">
    <div class="filter-panel">
      <n-space justify="space-between">
        <n-input v-model:value="searchQuery" placeholder="Поиск по названию..." clearable style="width: 300px" />
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
      <n-tabs type="line" animated>
        <n-tab-pane name="main" tab="Основная информация">
          <n-form ref="formRef" :model="selectedItem" label-placement="top">
            <n-grid :cols="2" :x-gap="20">
              <n-form-item-gi span="2" label="Название события">
                <n-input v-model:value="selectedItem.title" placeholder="Введите название" />
              </n-form-item-gi>
              <n-form-item-gi span="2" label="Краткое описание">
                <n-input v-model:value="selectedItem.short_description" type="textarea" :autosize="{ minRows: 2 }" />
              </n-form-item-gi>
              <n-form-item-gi span="2" label="Полное описание (с оформлением)">
                <Editor v-model="selectedItem.description" />
              </n-form-item-gi>
              <n-form-item-gi label="Категория">
                <n-select v-model:value="selectedItem.category_id" :options="categoryOptions" label-field="category_name" value-field="category_id" />
              </n-form-item-gi>
              <n-form-item-gi label="Формат">
                <n-select v-model:value="selectedItem.format_type_id" :options="formatOptions" label-field="format_type_name" value-field="format_type_id" />
              </n-form-item-gi>
              <n-form-item-gi label="Возраст">
                <n-select v-model:value="selectedItem.age_category_id" :options="ageOptions" label-field="age_category_name" value-field="age_category_id" />
              </n-form-item-gi>
              <n-form-item-gi label="Активна">
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
            <n-form-item-gi label="Продолжительность (мин)">
              <n-input-number v-model:value="selectedItem.duration" :min="0" style="width: 100%" />
            </n-form-item-gi>

            <n-form-item-gi label="Место">
              <n-input v-model:value="selectedItem.place" />
            </n-form-item-gi>

            <n-form-item-gi label="Проводит">
              <n-input v-model:value="selectedItem.conducted_by" />
            </n-form-item-gi>

            <n-form-item-gi label="Часы работы">
              <n-input v-model:value="selectedItem.working_hours" placeholder="С 10:00 до 20:00" />
            </n-form-item-gi>

            <n-form-item-gi label="Email">
              <n-input v-model:value="selectedItem.contact_email" />
            </n-form-item-gi>

            <n-form-item-gi label="Telegram">
              <n-input v-model:value="selectedItem.telegram" placeholder="@username" />
            </n-form-item-gi>

            <n-form-item-gi label="VK">
              <n-input v-model:value="selectedItem.vk" placeholder="vk.com/..." />
            </n-form-item-gi>

            <n-form-item-gi label="До центра (км)">
              <n-input-number v-model:value="selectedItem.distance_to_center" :precision="1" style="width: 100%" />
            </n-form-item-gi>

            <n-form-item-gi label="До остановки (мин)">
              <n-input-number v-model:value="selectedItem.time_to_nearest_stop" style="width: 100%" />
            </n-form-item-gi>

            <n-form-item-gi span="2" label="Ссылка на iframe (карта)">
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
                <n-form-item-gi span="2" label="Дата и время начала">
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

                <n-form-item-gi label="Макс. чел.">
                  <n-input-number v-model:value="session.max_participants" :min="1" />
                </n-form-item-gi>

                <n-form-item-gi label="Стоимость">
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
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, inject, watch, h } from 'vue';
import { useDataStore, baseUrl } from '@/stores/counter';
import {
  NDataTable, NModal, NForm, NFormItemGi, NGrid, NInput, NDatePicker, NCard,
  NSelect, NButton, NSpace, NTag, NTabs, NTabPane, NUpload, NUploadDragger, useMessage, useDialog, NRadioGroup, NRadio, NInputNumber
} from 'naive-ui';
import BaseButton from '@/components/ui/button/BaseButton.vue';
import Editor from '@/components/ui/Editor.vue';

const store = useDataStore();
const message = useMessage();
const dialog = useDialog();
const loading = ref(false);
const showModal = ref(false);
const isEdit = ref(false);
const searchQuery = ref('');
// В script setup
const uploadRef = ref(null);

const selectedItem = ref({
  title: '',
  category_id: null,
  short_description: '',
  description: '',
  conducted_by: '',
  place: '',
  contact_email: '',
  photos: []
});

// Данные из стора
const excursions = computed(() => {
  const allExcursions = store.adminExcursions.excursions || [];

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

// Таблица
const columns = [
  {
    title: 'ID',
    key: 'excursion_id',
    width: 60,
    sorter: (row1, row2) => row1.excursion_id - row2.excursion_id // Сортировка чисел
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
      // Убираем секунды для красоты в таблице
      return row.sessions[0].start_datetime.replace(/:\d{2}$/, '');
    }
  },
  {
    title: 'Макс. чел.',
    key: 'max_participants',
    width: 120,
    align: 'center',
    render: (row) => {
      // Берем данные из первой сессии
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

      // Динамический цвет тега в зависимости от заполненности
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
    isEdit.value = true;
    newExcursionPhotos.value = []; // Чистим очередь для создания
    uploadRef.value?.clear();

    // Глубокое копирование сессий с исправлением формата дат
    const fixedSessions = row.sessions?.map(s => ({
      ...s,
      // Заменяем "T" на пробел, чтобы получилось "2026-05-23 19:04:00"
      start_datetime: s.start_datetime
        ? s.start_datetime.replace('T', ' ').replace(/:\d{2}$/, ':00')
        : null,
      cost: s.cost ? parseInt(s.cost) : 0
    })) || [];

    selectedItem.value = {
      ...row,
      category_id: row.category?.category_id,
      format_type_id: row.format_type?.format_type_id,
      age_category_id: row.age_category?.age_category_id,
      sessions: fixedSessions // Используем исправленные сессии
    };
    showModal.value = true;
  }
});

// Кнопка добавить в хедере
const addTrigger = inject('admin-add-event');
watch(addTrigger, () => {
  isEdit.value = false;
  newExcursionPhotos.value = [];
  selectedItem.value = {
    title: '',
    category_id: null,
    photos: [],
    sessions: []
  };
  showModal.value = true;
});

// --- ЛОГИКА СОХРАНЕНИЯ ---
async function handleSave() {
  try {
    loading.value = true;
      // 1. Обновляем текстовые данные
      const selectedCategory = categoryOptions.value.find(c => c.category_id === selectedItem.value.category_id);
      const selectedFormat = formatOptions.value.find(f => f.format_type_id === selectedItem.value.format_type_id);
      const selectedAge = ageOptions.value.find(a => a.age_category_id === selectedItem.value.age_category_id);

      const payload = {
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
        telegram: selectedItem.value.telegram,
        vk: selectedItem.value.vk,
        distance_to_center: selectedItem.value.distance_to_center,
        time_to_nearest_stop: selectedItem.value.time_to_nearest_stop,
        // Если бэкенд принимает ID категории/формата в этом же запросе:
        category: selectedCategory ? selectedCategory.category_name : '',
        format_type: selectedFormat ? selectedFormat.format_type_name : '',
        age_category: selectedAge ? selectedAge.age_category_name : '',
        sessions: (selectedItem.value.sessions || []).map(s => ({
        start_datetime: s.start_datetime,
        max_participants: s.max_participants || 10,
        cost: s.cost || 0
      }))
      };
    if (isEdit.value) {
      await store.PatchExcursion(selectedItem.value.excursion_id, payload);
      message.success('Обновлено');
    } else {
      // 2. Создаем новое (через простой JSON или FormData, если нужно сразу с фото)
      const formData = new FormData();

      // Поле 'data' с JSON строкой
      formData.append('data', JSON.stringify(payload));

      // Поле 'photos' со списком файлов
      newExcursionPhotos.value.forEach(file => {
        formData.append('photos', file);
      });

      await store.PostNewExcursion(formData);
      message.success('Событие полностью создано');
      newExcursionPhotos.value = []; // Чистим временные фото
    }

    showModal.value = false;
    await store.FetchAdminExcursion();
  } catch (e) {
    console.error(e);
    message.error('Ошибка при сохранении');
  } finally {
    loading.value = false;
  }
}

// 1. Добавить пустую форму сессии в список (локально)
function addEmptySession() {
  if (!selectedItem.value.sessions) selectedItem.value.sessions = [];
  selectedItem.value.sessions.unshift({
    start_datetime: null,
    max_participants: 10,
    cost: 0,
  });
}

// 2. Сохранение или обновление сессии
async function handleSaveSession(session) {
  if (!session.start_datetime) {
    message.error('Выберите дату и время');
    return;
  }

  const payload = {
    start_datetime: session.start_datetime,
    max_participants: session.max_participants,
    cost: session.cost
  };

  try {
    loading.value = true;
    if (session.session_id) {
      // Редактирование существующей
      await store.PatchExcursionSession(selectedItem.value.excursion_id, session.session_id, payload);
      message.success('Сессия обновлена');
    } else {
      // Создание новой
      await store.PostExcursionSession(selectedItem.value.excursion_id, payload);
      message.success('Сессия создана');
    }
    await store.FetchAdminExcursion(); // Перезагружаем данные
  } catch (e) {
    message.error('Ошибка при работе с сессией', e);
  } finally {
    loading.value = false;
  }
}

// 3. Удаление сессии
async function handleDeleteSession(session, index) {
  // Если мы в режиме создания ИЛИ у сессии еще нет ID (она только что добавлена локально)
  if (!isEdit.value || !session.session_id) {
    selectedItem.value.sessions.splice(index, 1);
    return;
  }

  // Если это реальная сессия из базы при редактировании
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
        message.error('Ошибка при удалении', e);
      }
    }
  });
}

// --- РАБОТА С ФОТО ---
const newExcursionPhotos = ref([]);

async function handleUploadPhoto({ file, onFinish, onError }) {
  try {
    if (isEdit.value) {
      // РЕДАКТИРОВАНИЕ
      loading.value = true;
      await store.PostExcursionPhoto(selectedItem.value.excursion_id, file.file);

      await store.FetchAdminExcursion();
      const updated = store.adminExcursions.excursions.find(
        e => e.excursion_id === selectedItem.value.excursion_id
      );
      if (updated) selectedItem.value.photos = updated.photos;

      message.success('Фото сохранено в базу');
    } else {
      // СОЗДАНИЕ
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

    // Сообщаем компоненту, что загрузка конкретно этого файла успешна
    onFinish();

    // ОЧИЩАЕМ внутренний список n-upload, чтобы он не копил файлы
    // и не пытался отправить их повторно при следующем клике
    uploadRef.value?.clear();

  } catch (e) {
    console.error(e);
    message.error('Ошибка при загрузке файла');
    onError();
  } finally {
    loading.value = false;
  }
}

async function handleDeletePhoto(photoId) {
  const photoIndex = selectedItem.value.photos.findIndex(p => p.photo_id === photoId);
  if (photoIndex === -1) return;

  const photo = selectedItem.value.photos[photoIndex];

  if (photo.isLocal) {
    // 1. Удаляем из массива файлов для FormData (по имени файла)
    newExcursionPhotos.value = newExcursionPhotos.value.filter(
      file => file.name !== photo.fileName
    );
    // 2. Удаляем из превью
    selectedItem.value.photos.splice(photoIndex, 1);
    message.info('Фото удалено из очереди');
    return;
  }

  // Удаление из базы (остается без изменений)
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
        message.error('Ошибка удаления', e);
      }
    }
  });
}

// --- УДАЛЕНИЕ СОБЫТИЯ ---
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
  store.FetchAdminExcursion();
  store.FetchCategories();
});
</script>

<style scoped>
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

/* Стили для компактного загрузчика */
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
  z-index: 10; /* Чтобы кнопка была над картинкой */
  background: rgba(255, 255, 255, 0.8);
  color: #d03050;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}
</style>
