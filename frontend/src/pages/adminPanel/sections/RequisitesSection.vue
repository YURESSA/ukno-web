<template>
  <div class="requisites-section">
    <n-space vertical size="large">
      <n-h2 style="margin: 0">Реквизиты</n-h2>
      <n-data-table
        :columns="columns"
        :data="requisites"
        :loading="loading"
        :row-props="rowProps"
      />
    </n-space>

    <n-modal v-model:show="showModal" preset="card" style="width: 500px"
             :title="isEditMode ? 'Редактировать реквизит' : 'Добавить реквизит'">
      <n-form>
        <n-form-item label="Название реквизита">
          <n-input v-model:value="model.title" placeholder="Например: Свидетельство о регистрации" />
        </n-form-item>

        <n-form-item label="Документ (файл)">
          <n-upload
            v-model:file-list="fileList"
            @change="handleUploadChange"
            @remove="handleRemove"
            :max="1"
          >
            <n-button>Выбрать файл</n-button>
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
  NModal, NForm, NFormItem, NInput, NUpload, useDialog, NText
} from 'naive-ui'

const store = useDataStore()
const message = useMessage()
const dialog = useDialog()
const addEvent = inject('admin-add-event')

const requisites = computed(() => store.getRequisites)

const showModal = ref(false)
const isEditMode = ref(false)
const loading = ref(false)
const submitLoading = ref(false)

const fileList = ref([])
const model = ref({
  id: null,
  title: '',
  file: null,
  file_url: ''
})

watch(addEvent, () => {
  openCreateModal()
})

const columns = [
  { title: 'ID', key: 'id', width: 70 },
  { title: 'Название реквизита', key: 'title' },
  {
    title: 'Файл',
    key: 'file',
    render(row) {
      if (!row.file) return h(NText, { depth: 3 }, 'Нет файла')
      const fileName = row.file.split('/').pop()
      return h('a', {
        href: `${baseUrl}/${row.file}`,
        target: '_blank',
        style: 'color: #FF6C36; text-decoration: underline;'
      }, fileName)
    }
  }
]

const rowProps = (row) => ({
  style: 'cursor: pointer',
  onClick: () => openEditModal(row)
})

const openCreateModal = () => {
  isEditMode.value = false
  model.value = { id: null, title: '', file: null, file_url: '' }
  fileList.value = []
  showModal.value = true
}

const openEditModal = (row) => {
  isEditMode.value = true
  model.value = {
    id: row.id,
    title: row.title,
    file: null,
    file_url: row.file
  }

  fileList.value = row.file ? [{
    id: 'server-file',
    name: row.file.split('/').pop(),
    status: 'finished',
    url: `${baseUrl}/${row.file}`
  }] : []

  showModal.value = true
}

const handleUploadChange = (data) => {
  const lastFile = data.fileList.slice(-1)
  fileList.value = lastFile
  model.value.file = lastFile.length > 0 && lastFile[0].file ? lastFile[0].file : null
}

const handleRemove = (options) => {
  const { file } = options
  if (file.id !== 'server-file') {
    model.value.file = null
    return true
  }

  return new Promise((resolve) => {
    dialog.warning({
      title: 'Удаление файла',
      content: 'Вы уверены, что хотите удалить файл реквизита с сервера?',
      positiveText: 'Удалить',
      onPositiveClick: async () => {
        try {
          await store.DeleteRequisiteFile(model.value.id)
          message.success('Файл удален')
          await store.FetchRequisites()
          resolve(true)
        } catch (e) {
          message.error('Ошибка при удалении', e)
          resolve(false)
        }
      },
      onNegativeClick: () => resolve(false)
    })
  })
}

const handleSave = async () => {
  if (!model.value.title) return message.error('Введите название')

  try {
    submitLoading.value = true

    if (isEditMode.value) {
      const formData = new FormData()
      formData.append('title', model.value.title)
      await store.UpdateRequisite(model.value.id, formData)

      if (model.value.file) {
        const fileData = new FormData()
        fileData.append('file', model.value.file)
        await store.UpdateRequisiteFile(model.value.id, fileData)
      }
      message.success('Реквизит обновлен')
    } else {
      const formData = new FormData()
      formData.append('title', model.value.title)
      if (model.value.file) {
        formData.append('file', model.value.file)
      }

      await store.AddRequisite(formData)
      message.success('Реквизит создан')
    }

    showModal.value = false
    await store.FetchRequisites()
  } catch (e) {
    message.error('Ошибка при сохранении', e)
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = async () => {
  if (confirm(`Удалить реквизит "${model.value.title}"?`)) {
    try {
      await store.DeleteRequisite(model.value.id)
      message.success('Удалено')
      showModal.value = false
      await store.FetchRequisites()
    } catch (e) {
      message.error('Ошибка при удалении', e)
    }
  }
}

onMounted(() => {
  loading.value = true
  store.FetchRequisites().finally(() => loading.value = false)
})
</script>
