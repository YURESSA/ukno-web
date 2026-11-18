<template>
  <div class="requisites-section">
    <n-space vertical size="large">
      <n-h2 style="margin: 0">Реквизиты</n-h2>
      <n-data-table
        :columns="columns"
        :data="requisites"
        :row-key="row => row.requiredDocument ? row.title : row.id"
        :loading="loading"
        :row-props="rowProps"
      />
    </n-space>

    <n-modal v-model:show="showModal" preset="card" style="width: min(500px, calc(100vw - 32px))"
             :title="model.requiredDocument ? model.title : (isEditMode ? 'Редактировать реквизит' : 'Добавить реквизит')"
             :closable="!submitLoading" :mask-closable="!submitLoading" :close-on-esc="!submitLoading">
      <n-form>
        <n-form-item v-if="!model.requiredDocument" label="Название реквизита" v-bind="fieldProps(model, 'requisites', 'title')">
          <n-input v-model:value="model.title" placeholder="Например: Свидетельство о регистрации" />
        </n-form-item>

        <n-form-item v-if="model.requiredDocument && model.file_url" label="Текущий файл">
          <a :href="resolveMediaUrl(model.file_url)" target="_blank" rel="noopener noreferrer">{{ fileName(model.file_url) }}</a>
        </n-form-item>

        <n-form-item label="Документ (файл)" :required="requiresFile" v-bind="fieldProps(model, 'requisites', 'file', !requiresFile)">
          <n-upload
            :disabled="submitLoading"
            :default-upload="false"
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
          <n-button v-if="isEditMode && !model.requiredDocument" type="error" ghost :disabled="submitLoading" @click="handleDelete">Удалить</n-button>
          <div v-else></div>
          <n-space>
            <n-button :disabled="submitLoading" @click="showModal = false">Отмена</n-button>
            <n-button type="primary" :loading="submitLoading" @click="handleSave">Сохранить</n-button>
          </n-space>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { useAdminValidation } from '@/composables/useAdminValidation'
import { getApiErrorMessage } from '@/utils/apiError'
import { findRequiredRequisite, getRequiredRequisiteTitle, REQUIRED_REQUISITES } from '@/utils/requiredRequisites'
import { ref, onMounted, h, inject, watch, computed } from 'vue'
import { useDataStore, resolveMediaUrl } from '@/stores/counter'
import {
  NButton, useMessage, NSpace, NH2, NDataTable,
  NModal, NForm, NFormItem, NInput, NUpload, useDialog, NText, NTag
} from 'naive-ui'

const { fieldProps, submitValidation, resetValidation, applyApiErrors } = useAdminValidation();

const store = useDataStore()
const message = useMessage()
const dialog = useDialog()
const addEvent = inject('admin-add-event')

const requisites = computed(() => {
  const records = Array.isArray(store.getRequisites) ? store.getRequisites : []
  const required = REQUIRED_REQUISITES.map(title => ({
    ...findRequiredRequisite(records, title),
    title,
    requiredDocument: true
  }))
  return [...required, ...records.filter(row => !getRequiredRequisiteTitle(row.title))]
})

const showModal = ref(false)
const isEditMode = ref(false)
const loading = ref(false)
const submitLoading = ref(false)

const fileList = ref([])
const model = ref({
  id: null,
  title: '',
  file: null,
  file_url: '',
  requiredDocument: false
})
const requiresFile = computed(() => model.value.requiredDocument || !isEditMode.value)
const fileName = path => path.split(/[?#]/)[0].split('/').pop()

watch(addEvent, () => {
  openCreateModal()
})

const columns = [
  { title: 'ID', key: 'id', width: 70 },
  {
    title: 'Название реквизита',
    key: 'title',
    render: row => row.requiredDocument
      ? h(NSpace, { size: 'small', align: 'center' }, () => [
          row.title,
          h(NTag, { size: 'small', bordered: false }, () => 'Обязательный')
        ])
      : row.title
  },
  {
    title: 'Файл',
    key: 'file',
    render(row) {
      const file = row.file ? h('a', {
        href: resolveMediaUrl(row.file),
        target: '_blank',
        rel: 'noopener noreferrer',
        style: 'color: #FF6C36; text-decoration: underline;',
        onClick: event => event.stopPropagation()
      }, fileName(row.file)) : h(NText, { depth: 3 }, () => 'Нет файла')
      if (!row.requiredDocument) return file
      return h(NSpace, { size: 'small', align: 'center' }, () => [
        file,
        h(NButton, {
          size: 'small',
          onClick: event => {
            event.stopPropagation()
            openEditModal(row)
          }
        }, () => row.file ? 'Заменить файл' : 'Загрузить файл')
      ])
    }
  }
]

const rowProps = (row) => ({
  style: 'cursor: pointer',
  onClick: () => openEditModal(row)
})

const openCreateModal = () => {
  isEditMode.value = false
  model.value = { id: null, title: '', file: null, file_url: '', requiredDocument: false }
  fileList.value = []
  showModal.value = true
}

const openEditModal = (row) => {
  isEditMode.value = row.id != null
  model.value = {
    id: row.id ?? null,
    title: row.title,
    file: null,
    file_url: row.file,
    requiredDocument: Boolean(row.requiredDocument)
  }

  fileList.value = row.file && !row.requiredDocument ? [{
    id: 'server-file',
    name: fileName(row.file),
    status: 'finished',
    url: resolveMediaUrl(row.file)
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
  if (model.value.requiredDocument) return false

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
          message.error(getApiErrorMessage(e, 'Ошибка при удалении'))
          resolve(false)
        }
      },
      onNegativeClick: () => resolve(false)
    })
  })
}

const handleSave = async () => {
  if (loading.value || submitLoading.value) return;
  if (submitValidation(model.value, 'requisites', !requiresFile.value).length) return;

  try {
    submitLoading.value = true

    if (model.value.requiredDocument) {
      const { title, file } = model.value
      let id = model.value.id
      if (id == null) {
        await store.FetchRequisites()
        id = findRequiredRequisite(store.getRequisites, title)?.id
      }
      const formData = new FormData()
      formData.append('file', file)
      if (id == null) {
        formData.append('title', title)
        await store.AddRequisite(formData)
      } else {
        await store.UpdateRequisiteFile(id, formData)
      }
      message.success('Файл сохранён')
      showModal.value = false
      return
    }

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
    const { message: feedback } = applyApiErrors(e, model.value, 'Ошибка при сохранении');
    if (feedback) message.error(feedback);
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = async () => {
  if (model.value.requiredDocument || submitLoading.value) return
  if (confirm(`Удалить реквизит "${model.value.title}"?`)) {
    try {
      await store.DeleteRequisite(model.value.id)
      message.success('Удалено')
      showModal.value = false
      await store.FetchRequisites()
    } catch (e) {
      message.error(getApiErrorMessage(e, 'Ошибка при удалении'))
    }
  }
}

onMounted(() => {
  loading.value = true
  store.FetchRequisites().catch(e => message.error(getApiErrorMessage(e, 'Ошибка загрузки данных'))).finally(() => loading.value = false)
})

watch(showModal, resetValidation);
</script>
