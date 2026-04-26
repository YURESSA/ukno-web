<template>
  <div class="partners-section">
    <n-space vertical size="large">
      <n-h2 style="margin: 0">Партнёры</n-h2>
      <n-data-table
        :columns="columns"
        :data="partners"
        :loading="loading"
        :row-props="rowProps"
      />
    </n-space>

    <n-modal v-model:show="showModal" preset="card" style="width: 550px"
             :title="isEditMode ? 'Редактировать партнёра' : 'Добавить партнёра'">
      <n-form>
        <n-form-item label="Название организации">
          <n-input v-model:value="model.name" placeholder="Введите название..." />
        </n-form-item>

        <n-form-item label="Ссылка на сайт">
          <n-input v-model:value="model.link" placeholder="https://partner-site.com" />
        </n-form-item>

        <n-form-item label="Порядок отображения">
          <n-input-number v-model:value="model.order_index" :min="0" style="width: 100%" />
        </n-form-item>

        <n-form-item label="Логотип">
          <n-upload
            v-model:file-list="fileList"
            list-type="image-card"
            :max="1"
            @change="handleUploadChange"
            @remove="handleRemove"
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
  NModal, NForm, NFormItem, NInput, NUpload, NImage, useDialog, NInputNumber
} from 'naive-ui'

const store = useDataStore()
const message = useMessage()
const dialog = useDialog()
const addEvent = inject('admin-add-event')

const partners = computed(() => store.getPartners)

const showModal = ref(false)
const isEditMode = ref(false)
const loading = ref(false)
const submitLoading = ref(false)

const fileList = ref([])
const model = ref({
  id: null,
  name: '',
  link: '',
  order_index: 0,
  photo: null,
  photo_url: ''
})

const getImageUrl = (path) => {
  if (!path) return ''
  return path.startsWith('http') ? path : `${baseUrl}/${path}`
}

watch(addEvent, () => {
  openCreateModal()
})

const columns = [
  { title: 'Порядок', key: 'order_index', width: 100 },
  {
    title: 'Логотип',
    key: 'photo',
    render(row) {
      return h(NImage, {
        width: 100,
        height: 50,
        src: getImageUrl(row.photo),
        style: 'border-radius: 4px; object-fit: contain; background: #f5f5f5',
        onClick: (e) => e.stopPropagation()
      })
    }
  },
  { title: 'Название партнера', key: 'name' },
  {
    title: 'Ссылка',
    key: 'link',
    render: (row) => h('a', { href: row.link, target: '_blank', style: 'color: #FF6C36' }, row.link)
  }
]

const rowProps = (row) => ({
  style: 'cursor: pointer',
  onClick: () => openEditModal(row)
})

const openCreateModal = () => {
  isEditMode.value = false
  model.value = { id: null, name: '', link: '', order_index: 0, photo: null, photo_url: '' }
  fileList.value = []
  showModal.value = true
}

const openEditModal = (row) => {
  isEditMode.value = true
  const fullPhotoUrl = getImageUrl(row.photo)
  model.value = {
    id: row.id,
    name: row.name,
    link: row.link,
    order_index: Number(row.order_index) || 0,
    photo: null,
    photo_url: fullPhotoUrl
  }

  fileList.value = row.photo ? [{
    id: 'server-file',
    name: 'logo.png',
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

const handleRemove = (options) => {
  const { file } = options
  if (file.id !== 'server-file') {
    model.value.photo = null
    return true
  }

  return new Promise((resolve) => {
    dialog.warning({
      title: 'Удаление логотипа',
      content: 'Удалить логотип партнера с сервера?',
      positiveText: 'Удалить',
      onPositiveClick: async () => {
        try {
          await store.DeletePartnerPhoto(model.value.id)
          message.success('Логотип удален')
          await store.FetchPartners()
          resolve(true)
        } catch (e) {
          message.error('Ошибка при удалении')
          resolve(false)
        }
      },
      onNegativeClick: () => resolve(false)
    })
  })
}

const handleSave = async () => {
  if (!model.value.name) return message.error('Введите название партнера')

  try {
    submitLoading.value = true
    const orderValue = Number(model.value.order_index) || 0

    if (isEditMode.value) {
      // Обновление данных (текст + ссылка + порядок) через PUT
      const formData = new FormData()
      formData.append('name', model.value.name)
      formData.append('link', model.value.link)
      formData.append('order_index', orderValue)

      await store.UpdatePartner(model.value.id, formData)

      // Если выбрано новое фото
      if (model.value.photo) {
        const photoData = new FormData()
        photoData.append('photo', model.value.photo)
        await store.UpdatePartnerPhoto(model.value.id, photoData)
      }
      message.success('Данные партнера обновлены')
    } else {
      // Создание (POST)
      const formData = new FormData()
      formData.append('name', model.value.name)
      formData.append('link', model.value.link)
      formData.append('order_index', orderValue)
      if (model.value.photo) formData.append('photo', model.value.photo)

      await store.AddPartner(formData)
      message.success('Партнер добавлен')
    }

    showModal.value = false
    await store.FetchPartners()
  } catch (e) {
    message.error('Ошибка при сохранении')
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = async () => {
  if (confirm(`Удалить партнера "${model.value.name}"?`)) {
    try {
      await store.DeletePartner(model.value.id)
      message.success('Удалено')
      showModal.value = false
      await store.FetchPartners()
    } catch (e) {
      message.error('Ошибка при удалении')
    }
  }
}

onMounted(() => {
  loading.value = true
  store.FetchPartners().finally(() => loading.value = false)
})
</script>
