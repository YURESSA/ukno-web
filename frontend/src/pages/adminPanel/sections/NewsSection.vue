<template>
  <div class="section-container">
    <div class="filter-panel" style="margin-bottom: 20px;">
      <n-space justify="space-between">
        <n-input
          v-model:value="searchQuery"
          placeholder="Поиск по заголовку, тексту или автору..."
          clearable
          style="width: 400px"
        />
      </n-space>
    </div>

    <n-data-table
      :loading="loading"
      :columns="columns"
      :data="filteredNews"
      :row-props="rowProps"
      :pagination="{ pageSize: 10 }"
    />

    <n-modal
      v-model:show="showModal"
      preset="card"
      style="width: 900px"
      :title="isEdit ? 'Редактирование новости' : 'Создать новую новость'"
    >
      <n-form ref="formRef" :model="selectedItem" label-placement="top">
        <n-grid :cols="2" :x-gap="20">
          <n-form-item-gi span="2" label="Заголовок">
            <n-input v-model:value="selectedItem.title" placeholder="Введите заголовок" />
          </n-form-item-gi>

          <n-form-item-gi span="2" label="Краткое описание">
            <n-input
              v-model:value="selectedItem.short_description"
              type="textarea"
              :autosize="{ minRows: 2 }"
              placeholder="Короткое превью..."
            />
          </n-form-item-gi>

          <n-form-item-gi span="2" label="Содержимое">
            <Editor v-model="selectedItem.content" />
          </n-form-item-gi>
          <n-form-item-gi span="2" label="Изображения новости">
            <n-upload
              multiple
              directory-dnd
              :default-file-list="fileList"
              :max="1"
              list-type="image-card"
              @change="handleUploadChange"
              @remove="handleRemove"
            >
              <n-upload-dragger>
                <div>
                  <n-icon size="32">
                    +
                  </n-icon>
                </div>
              </n-upload-dragger>
            </n-upload>
          </n-form-item-gi>

          <n-form-item-gi label="Автор фото">
            <n-input v-model:value="selectedItem.photo_author" placeholder="Кто сделал фото?" />
          </n-form-item-gi>

          <n-form-item-gi label="Дата публикации">
            <n-date-picker
              v-model:formatted-value="selectedItem.created_at"
              value-format="yyyy-MM-dd HH:mm:00"
              type="datetime"
              style="width: 100%"
              clearable
            />
          </n-form-item-gi>
        </n-grid>
      </n-form>

      <template #footer>
        <n-space justify="end">
          <n-button v-if="isEdit" type="error" ghost @click="confirmDelete">Удалить</n-button>
          <n-button @click="showModal = false">Отмена</n-button>
          <BaseButton
            :text="isEdit ? 'Сохранить изменения' : 'Опубликовать'"
            @click="handleSave"
            :loading="loading"
          />
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, computed, inject, watch, onMounted, h } from 'vue';
import { useDataStore, baseUrl } from '@/stores/counter'; // baseUrl для картинок
import {
  NDataTable, NModal, NForm, NFormItemGi, NGrid, NInput,
  NDatePicker, NButton, NSpace, NAvatar, NUpload, NUploadDragger,
  NIcon, useMessage, useDialog
} from 'naive-ui';
import BaseButton from '@/components/UI/button/BaseButton.vue';
import Editor from '@/components/ui/Editor.vue';

const store = useDataStore();
const message = useMessage();
const dialog = useDialog();
const loading = ref(false);

const showModal = ref(false);
const isEdit = ref(false);
const searchQuery = ref('');

const selectedItem = ref({
  news_id: null,
  title: '',
  short_description: '',
  content: '',
  photo_author: '',
  created_at: null
});

// --- КОЛОНКИ ТАБЛИЦЫ ---
const columns = [
  { title: 'ID', key: 'news_id', width: 60 },
  {
    title: 'Превью',
    key: 'images',
    width: 150,
    render: (row) => {
      if (row.images?.length) {
        return h(NAvatar, {
          size: 96,
          src: `${baseUrl}${row.images[0]}`,
          objectFit: 'cover'
        });
      }
      return '—';
    }
  },
  { title: 'Заголовок', key: 'title', sorter: 'default', ellipsis: { tooltip: true }, width: 450  },
  { title: 'Краткое описание', key: 'short_description', render: (row) => row.short_description || 'Отсутствует' },
  {
    title: 'Автор',
    key: 'author',
    render: (row) => row.author?.full_name || 'Не указан',
    width: 150
  },
  {
    title: 'Дата',
    key: 'created_at',
    width: 150,
    render: (row) => row.created_at?.split('T')[0]
  }
];

// --- ФИЛЬТРАЦИЯ ---
const filteredNews = computed(() => {
  const data = store.getNews?.news || []; // Обращаемся к store.getNews.news
  if (!searchQuery.value) return data;

  const s = searchQuery.value.toLowerCase();
  return data.filter(n =>
    n.title?.toLowerCase().includes(s) ||
    n.author?.full_name?.toLowerCase().includes(s) ||
    n.content?.toLowerCase().includes(s)
  );
});

// Список для отображения в компоненте n-upload
const fileList = ref([]);
// Массив самих файлов для отправки
const newFiles = ref([]);

// Следим за изменениями в загрузчике
const handleUploadChange = (data) => {
  fileList.value = data.fileList;
  // Фильтруем только те файлы, у которых есть объект file (новые загруженные)
  newFiles.value = data.fileList
    .filter(item => item.file)
    .map(item => item.file);
};

// При удалении файла
const handleRemove = (data) => {
  const { file } = data;

  // 1. Если это НОВОЕ фото (которого еще нет на сервере)
  // Мы помечаем новые файлы отсутствием префикса 'old-' в id
  if (!file.id.startsWith('old-')) {
    newFiles.value = newFiles.value.filter(f => f.name !== file.name);
    message.info('Файл удален из очереди на загрузку');
    return true; // Разрешаем компоненту убрать карточку
  }

  // 2. Если это СТАРОЕ фото (нужно удалить на бэкенде по индексу)
  return new Promise((resolve) => {
    dialog.warning({
      title: 'Удаление фото',
      content: 'Вы уверены, что хотите удалить это фото с сервера?',
      positiveText: 'Удалить',
      negativeText: 'Отмена',
      onPositiveClick: async () => {
        try {
          const photoIndex = parseInt(file.id.replace('old-', '')) + 1;

          loading.value = true;
          await store.DeleteAdminNewsPhoto(selectedItem.value.news_id, photoIndex);

          selectedItem.value.images.splice(photoIndex, 1);

          message.success('Фото успешно удалено');
          await store.FetchAdminNews();

          resolve(true);
        } catch (e) {
          console.error(e);
          message.error('Ошибка сервера при удалении фото');
          resolve(false);
        } finally {
          loading.value = false;
        }
      },
      onNegativeClick: () => resolve(false)
    });
  });
};

const rowProps = (row) => ({
  style: 'cursor: pointer',
  onClick: () => {
    isEdit.value = true;
    const item = { ...row };

    // Внутри rowProps
    if (item.images && item.images.length > 0) {
      fileList.value = item.images.map((img, index) => ({
        // Используем уникальный маркер 'old-', чтобы отличить серверные фото от новых
        id: `old-${index}`,
        name: `Снимок ${index + 1}`,
        status: 'finished',
        url: `${baseUrl}${img.photo_url || img}`, // поддержка и объекта, и строки
        // Сохраняем оригинальные данные внутри объекта файла для доступа в handleRemove
        fullData: img
      }));
    }

    newFiles.value = []; // Сбрасываем новые файлы
    if (item.created_at) {
      // Приводим к формату "2026-04-01 01:42:18"
      item.created_at = item.created_at.replace('T', ' ').substring(0, 19);
    }
    selectedItem.value = item;
    showModal.value = true;
  }
});

const addTrigger = inject('admin-add-event');
watch(addTrigger, () => {
  isEdit.value = false;
  fileList.value = [];
  newFiles.value = [];
  selectedItem.value = {
    news_id: null,
    title: '',
    short_description: '',
    content: '',
    photo_author: '',
    created_at: null // Теперь здесь "2026-04-01 13:00:00"
  };

  showModal.value = true;
});

async function handleSave() {
  if (!selectedItem.value.title.trim()) return message.warning('Заголовок обязателен');

  try {
    loading.value = true;

    // 1. Подготавливаем только текстовые данные
    const dataToSerialize = {
      title: selectedItem.value.title,
      content: selectedItem.value.content,
      photo_author: selectedItem.value.photo_author,
      short_description: selectedItem.value.short_description || "",
      created_at: selectedItem.value.created_at
    };

    const formData = new FormData();
    formData.append('data', JSON.stringify(dataToSerialize));

    let newsId = selectedItem.value.news_id;

    // 2. Основное сохранение (текст)
    if (isEdit.value) {
      await store.PutAdminNews(newsId, formData);
    } else {
      const res = await store.PostAdminNews(formData);
      // Если это создание, берем ID из ответа сервера (проверь структуру ответа!)
      newsId = res.data.news_id || res.data.id;
    }

    // 3. ЗАГРУЗКА ФОТО (Отдельно для каждого файла)
    if (newFiles.value && newFiles.value.length > 0) {
      console.log('Файлы к отправке:', newFiles.value);

      const uploadPromises = newFiles.value.map(file => {
        // Если это объект события или обертка, берем сам файл
        const rawFile = file.file || file;
        return store.PostAdminNewsPhoto(newsId, rawFile);
      });

      console.log('Массив промисов:', uploadPromises);
      await Promise.all(uploadPromises);
      console.log('Все фото загружены');
    }

    message.success(isEdit.value ? 'Новость обновлена' : 'Новость создана');
    showModal.value = false;
    await store.FetchAdminNews();

  } catch (e) {
    console.error(e);
    message.error(e.response?.data?.message || 'Ошибка при сохранении');
  } finally {
    loading.value = false;
  }
}

function confirmDelete() {
  dialog.warning({
    title: 'Удаление новости',
    content: `Вы уверены, что хотите полностью удалить новость "${selectedItem.value.title}"? Это действие необратимо.`,
    positiveText: 'Удалить',
    negativeText: 'Отмена',
    onPositiveClick: async () => {
      try {
        loading.value = true;
        await store.DeleteAdminNews(selectedItem.value.news_id);
        message.success('Новость успешно удалена');
        showModal.value = false;
        await store.FetchAdminNews(); // Обновляем таблицу
      } catch (e) {
        message.error('Не удалось удалить новость', e);
      } finally {
        loading.value = false;
      }
    }
  });
}

onMounted(() => store.FetchAdminNews());
</script>
