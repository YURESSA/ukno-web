<template>
  <div class="cultural-space-section">
    <n-space vertical size="large">
      <n-h2 style="margin: 0">Культурное пространство</n-h2>
      <n-data-table
        :columns="columns"
        :data="data"
        :loading="loading"
        :row-props="rowProps"
      />
    </n-space>

    <n-modal v-model:show="showModal" preset="card" style="width: 600px"
             :title="isEditMode ? 'Редактировать элемент' : 'Добавить элемент'">
      <n-form>
        <n-form-item label="Описание (текст)">
          <n-input
            v-model:value="model.text"
            type="textarea"
            placeholder="Введите описание культурного пространства..."
            :autosize="{ minRows: 3 }"
          />
        </n-form-item>

        <n-form-item label="Порядок вывода. Отсчёт начинается с 0">
          <n-input
            v-model:value="model.order_index"
            placeholder="Введите порядок отображения (0 выводится первым)"
            widht="100%"
          />
        </n-form-item>

        <n-form-item label="Фото">
          <n-upload
            v-model:file-list="fileList"
            list-type="image-card"
            :max="1"
            @change="handleUploadChange"
            accept="image/*"
          >
            Загрузить
          </n-upload>
        </n-form-item>
      </n-form>

      <template #footer>
        <n-space justify="space-between">
          <n-button v-if="isEditMode" type="error" ghost @click="handleDelete">Удалить</n-button>
          <div v-else></div>
          <n-space>
            <n-button @click="showModal = false">Отмена</n-button>
            <n-button type="primary" :loading="submitLoading" @click="handleSave">Сохранить</n-button>
          </n-space>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, onMounted, h, inject, watch, computed } from 'vue'
import { useDataStore, baseUrl } from '@/stores/counter'
import {
  NButton, useMessage, NSpace, NH2, NDataTable,
  NModal, NForm, NFormItem, NInput, NUpload, NImage
} from 'naive-ui'

const store = useDataStore()
const data = computed(() => store.getCulturalSpace)
const message = useMessage()
const addEvent = inject('admin-add-event')

const showModal = ref(false)
const isEditMode = ref(false)
const loading = ref(false)
const submitLoading = ref(false)

const fileList = ref([])
const model = ref({
  id: null,
  text: '',
  photo: null,
  photo_url: '',
  order_index: 0 // Инициализируем нулем по умолчанию
})

// Базовый URL для картинок
const getImageUrl = (path) => {
  if (!path) return ''
  return path.startsWith('http') ? path : `${baseUrl}/${path}`
}

// Следим за кнопкой из Layout
watch(addEvent, () => {
  openCreateModal()
})

const columns = [
  { title: 'ID', key: 'id' },
  {
    title: 'Фото',
    key: 'photo',
    render(row) {
      return h(NImage, {
        width: 150,
        height: 90,
        src: getImageUrl(row.photo),
        style: 'border-radius: 4px; object-fit: cover;',
        onClick: (e) => e.stopPropagation()
      })
    }
  },
  { title: 'Текст описания', key: 'text' },
  { title: 'Порядок', key: 'order_index' },
]

const rowProps = (row) => ({
  style: 'cursor: pointer',
  onClick: () => openEditModal(row)
})

const openCreateModal = () => {
  isEditMode.value = false
  model.value = {
    id: null,
    text: '',
    photo: null,
    photo_url: '',
    order_index: 0 // Сбрасываем в 0
  }
  fileList.value = []
  showModal.value = true
}

const openEditModal = (row) => {
  isEditMode.value = true
  const fullPhotoUrl = getImageUrl(row.photo)
  model.value = {
    id: row.id,
    text: row.text,
    photo: null,
    photo_url: fullPhotoUrl,
    // Важно: приводим к числу на случай, если с бэка пришла строка
    order_index: row.order_index !== undefined ? Number(row.order_index) : 0
  }

  fileList.value = row.photo ? [{
    id: 'curr',
    name: 'photo.png',
    status: 'finished',
    url: fullPhotoUrl
  }] : []

  showModal.value = true
}

const handleUploadChange = (data) => {
  const lastFile = data.fileList.slice(-1)
  fileList.value = lastFile
  model.value.photo = lastFile.length > 0 && lastFile[0].file ? lastFile[0].file : null
}

const handleSave = async () => {
  if (!model.value.text) return message.error('Введите текст')

  try {
    submitLoading.value = true
    // Приводим к числу перед отправкой
    const orderValue = Number(model.value.order_index) || 0

    if (isEditMode.value) {
      const textData = new FormData()
      textData.append('text', model.value.text)
      textData.append('order_index', orderValue) // Отправляем индекс при обновлении текста

      await store.UpdateCulturalSpaceText(model.value.id, textData)

      if (model.value.photo) {
        const photoData = new FormData()
        photoData.append('photo', model.value.photo)
        await store.UpdateCulturalSpacePhoto(model.value.id, photoData)
      }

      message.success('Данные успешно обновлены')
    } else {
      const formData = new FormData()
      formData.append('text', model.value.text)
      formData.append('order_index', orderValue) // Добавляем индекс при создании

      if (model.value.photo) {
        formData.append('photo', model.value.photo)
      }

      await store.AddCulturalSpace(formData)
      message.success('Элемент добавлен')
    }

    showModal.value = false
    await store.FetchCulturalSpace()
  } catch (e) {
    console.error(e)
    message.error('Ошибка при сохранении')
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = async () => {
  if (confirm('Удалить этот элемент?')) {
    try {
      await store.DeleteCulturalSpace(model.value.id)
      message.success('Удалено')
      showModal.value = false
      store.FetchCulturalSpace()
    } catch (e) {
      message.error('Ошибка при удалении')
    }
  }
}

onMounted(() => {
  loading.value = true
  store.FetchCulturalSpace().finally(() => loading.value = false)
})
</script>
