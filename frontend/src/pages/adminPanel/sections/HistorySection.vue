<template>
  <div class="history-section">
    <n-space vertical size="large">
      <n-h2 style="margin: 0">История компании (Таймлайн)</n-h2>

      <n-data-table
        :columns="columns"
        :data="historyData"
        :loading="loading"
        :row-props="rowProps"
      />
    </n-space>

    <n-modal
      v-model:show="showModal"
      preset="card"
      style="width: 600px"
      :title="isEditMode ? 'Редактировать событие' : 'Добавить событие'"
    >
      <n-form>
        <n-form-item label="Заголовок события">
          <n-input v-model:value="model.title" placeholder="Например: Основание компании" />
        </n-form-item>

        <n-form-item label="Дата события">
          <n-date-picker
            v-model:value="model.date"
            type="date"
            style="width: 100%"
            placeholder="Выберите дату"
          />
        </n-form-item>

        <n-form-item label="Описание">
          <n-input
            v-model:value="model.description"
            type="textarea"
            placeholder="Расскажите, что произошло..."
            :autosize="{ minRows: 3 }"
          />
        </n-form-item>

        <n-form-item label="Ссылка (опционально)">
          <n-input v-model:value="model.link" placeholder="https://..." />
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
  NModal, NForm, NFormItem, NInput, NDatePicker
} from 'naive-ui'
import { format, parseISO } from 'date-fns'

const store = useDataStore()
const message = useMessage()
const addEvent = inject('admin-add-event')

const historyData = computed(() => store.getHistory)

const showModal = ref(false)
const isEditMode = ref(false)
const loading = ref(false)
const submitLoading = ref(false)

const model = ref({
  id: null,
  title: '',
  link: '',
  date: null, // Здесь будет timestamp для n-date-picker
  description: ''
})

// Следим за кнопкой из Layout
watch(addEvent, () => {
  openCreateModal()
})

const columns = [
  { title: 'Дата', key: 'date', width: 120 },
  { title: 'Событие', key: 'title', width: 250 },
  { title: 'Описание', key: 'description' },
  {
    title: 'Ссылка',
    key: 'link',
    render(row) {
      return row.link ? h('a', { href: row.link, target: '_blank', style: 'color: #FF6C36' }, row.link) : '—'
    }
  }
]

const rowProps = (row) => ({
  style: 'cursor: pointer',
  onClick: () => openEditModal(row)
})

const openCreateModal = () => {
  isEditMode.value = false
  model.value = { id: null, title: '', link: '', date: Date.now(), description: '' }
  showModal.value = true
}

const openEditModal = (row) => {
  isEditMode.value = true
  model.value = {
    id: row.id,
    title: row.title,
    link: row.link,
    // Преобразуем строку YYYY-MM-DD в timestamp для дейтпикера
    date: row.date ? parseISO(row.date).getTime() : Date.now(),
    description: row.description
  }
  showModal.value = true
}

const handleSave = async () => {
  if (!model.value.title || !model.value.date || !model.value.description) {
    return message.error('Заполните название, дату и описание')
  }

  // Форматируем дату обратно в YYYY-MM-DD для API
  const formattedDate = format(model.value.date, 'yyyy-MM-dd')

  const payload = {
    title: model.value.title,
    link: model.value.link,
    date: formattedDate,
    description: model.value.description
  }

  try {
    submitLoading.value = true
    if (isEditMode.value) {
      await store.UpdateHistory(model.value.id, payload)
      message.success('Запись обновлена')
    } else {
      await store.AddHistory(payload)
      message.success('Запись добавлена')
    }
    showModal.value = false
    await store.FetchHistory()
  } catch (e) {
    message.error('Ошибка при сохранении')
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = async () => {
  if (confirm('Удалить эту запись из истории?')) {
    try {
      submitLoading.value = true
      await store.DeleteHistory(model.value.id)
      message.success('Удалено')
      showModal.value = false
      await store.FetchHistory()
    } catch (e) {
      message.error('Ошибка при удалении')
    } finally {
      submitLoading.value = false
    }
  }
}

onMounted(() => {
  loading.value = true
  store.FetchHistory().finally(() => loading.value = false)
})
</script>
