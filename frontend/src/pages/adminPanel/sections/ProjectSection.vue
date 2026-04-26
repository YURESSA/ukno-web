<template>
  <div class="projects-section">
    <n-space vertical size="large">
      <n-h2 style="margin: 0">Проекты компании</n-h2>

      <n-data-table
        :columns="columns"
        :data="projects"
        :loading="loading"
        :row-props="rowProps"
      />
    </n-space>

    <n-modal
      v-model:show="showModal"
      preset="card"
      style="width: 500px"
      :title="isEditMode ? 'Редактировать проект' : 'Новый проект'"
    >
      <n-form>
        <n-form-item label="Название проекта">
          <n-input v-model:value="model.title" placeholder="Например: Молодёжное бюро" />
        </n-form-item>

        <n-form-item label="Ссылка">
          <n-input v-model:value="model.link" placeholder="https://example.com" />
        </n-form-item>

        <n-form-item label="Порядок вывода">
          <n-input-number v-model:value="model.order_index" :min="0" style="width: 100%" />
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
import { useDataStore } from '@/stores/counter'
import {
  NButton, useMessage, NSpace, NH2, NDataTable,
  NModal, NForm, NFormItem, NInput, NInputNumber
} from 'naive-ui'

const store = useDataStore()
const message = useMessage()
const addEvent = inject('admin-add-event')

// Получаем данные из стора
const projects = computed(() => store.getProject)

const showModal = ref(false)
const isEditMode = ref(false)
const loading = ref(false)
const submitLoading = ref(false)

const model = ref({
  id: null,
  title: '',
  link: '',
  order_index: 0
})

// Следим за кликом по кнопке "+ Создать запись" в Layout
watch(addEvent, () => {
  openCreateModal()
})

const columns = [
  { title: 'Порядок', key: 'order_index', width: 100 },
  { title: 'Название', key: 'title', width: 250 },
  {
    title: 'Ссылка',
    key: 'link',
    render(row) {
      return h('a', { href: row.link, target: '_blank', style: 'color: #FF6C36' }, row.link)
    }
  },
  { title: 'ID', key: 'id', width: 70 }
]

const rowProps = (row) => ({
  style: 'cursor: pointer',
  onClick: () => openEditModal(row)
})

const openCreateModal = () => {
  isEditMode.value = false
  model.value = { id: null, title: '', link: '', order_index: 0 }
  showModal.value = true
}

const openEditModal = (row) => {
  isEditMode.value = true
  model.value = {
    id: row.id,
    title: row.title,
    link: row.link,
    order_index: Number(row.order_index) || 0
  }
  showModal.value = true
}

const handleSave = async () => {
  if (!model.value.title || !model.value.link) {
    return message.error('Заполните название и ссылку')
  }

  // Подготавливаем чистый JSON объект
  const payload = {
    title: model.value.title,
    link: model.value.link,
    order_index: Number(model.value.order_index)
  }

  try {
    submitLoading.value = true
    if (isEditMode.value) {
      await store.UpdateProject(model.value.id, payload)
      message.success('Проект обновлен')
    } else {
      await store.AddProject(payload)
      message.success('Проект создан')
    }
    showModal.value = false
    await store.FetchProject()
  } catch (e) {
    console.error(e)
    message.error('Ошибка при сохранении')
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = async () => {
  if (confirm(`Удалить проект "${model.value.title}"?`)) {
    try {
      submitLoading.value = true
      await store.DeleteProject(model.value.id)
      message.success('Удалено')
      showModal.value = false
      await store.FetchProject()
    } catch (e) {
      message.error('Ошибка при удалении')
    } finally {
      submitLoading.value = false
    }
  }
}

onMounted(() => {
  loading.value = true
  store.FetchProject().finally(() => loading.value = false)
})
</script>
