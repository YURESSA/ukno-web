<template>
  <div class="create-book-wrapper">
    <n-card title="Добавить новую книгу" class="create-book-card">
      <n-form ref="formRef" :model="bookForm" :rules="rules" label-placement="left" label-width="auto">

        <n-form-item label="Название книги" path="title">
          <n-input v-model:value="bookForm.title" placeholder="Введите название книги" />
        </n-form-item>

        <n-form-item label="Автор" path="author">
          <n-input v-model:value="bookForm.author" placeholder="Введите автора" />
        </n-form-item>

        <n-form-item label="Описание" path="description">
          <n-input
            v-model:value="bookForm.description"
            type="textarea"
            placeholder="Введите описание книги"
            :autosize="{ minRows: 3, maxRows: 6 }"
          />
        </n-form-item>

        <n-form-item label="Дата публикации" path="published_date">
          <n-date-picker
            v-model:value="bookForm.published_date"
            type="date"
            value-format="yyyy-MM-dd"
            placeholder="Выберите дату публикации"
          />
        </n-form-item>

        <n-form-item label="ISBN" path="isbn">
          <n-input v-model:value="bookForm.isbn" placeholder="Введите ISBN" />
        </n-form-item>

        <n-form-item label="Количество страниц" path="pages">
          <n-input-number
            v-model:value="bookForm.pages"
            :min="1"
            :max="10000"
            placeholder="Введите количество страниц"
          />
        </n-form-item>

        <n-form-item label="Язык" path="language">
          <n-select
            v-model:value="bookForm.language"
            :options="languageOptions"
            placeholder="Выберите язык"
          />
        </n-form-item>

        <n-form-item label="ID серии" path="series_id">
          <n-input-number
            v-model:value="bookForm.series_id"
            :min="0"
            placeholder="Введите ID серии (0 если нет)"
          />
        </n-form-item>

        <n-form-item label="ID жанров" path="genre_ids">
          <n-dynamic-tags v-model:value="bookForm.genre_ids" />
          <div class="form-hint">Вводите ID жанров и нажимайте Enter</div>
        </n-form-item>

        <n-space justify="end">
          <n-button @click="resetForm">
            Очистить
          </n-button>
          <n-button
            type="primary"
            :loading="loading"
            @click="handleSubmit"
          >
            {{ loading ? 'Создание...' : 'Создать книгу' }}
          </n-button>
        </n-space>
      </n-form>
    </n-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import {
  NCard,
  NForm,
  NFormItem,
  NInput,
  NInputNumber,
  NDatePicker,
  NSelect,
  NDynamicTags,
  NSpace,
  NButton
} from 'naive-ui'
import { useDataStore } from '@/stores/counter'

const store = useDataStore()
const formRef = ref(null)
const loading = ref(false)

// Данные формы
const bookForm = ref({
  title: '',
  author: '',
  description: '',
  published_date: null,
  isbn: '',
  pages: 0,
  language: 'ru',
  series_id: 0,
  genre_ids: []
})

// Опции для выбора языка
const languageOptions = [
  { label: 'Русский', value: 'ru' },
  { label: 'Английский', value: 'en' },
  { label: 'Французский', value: 'fr' },
  { label: 'Немецкий', value: 'de' },
  { label: 'Испанский', value: 'es' },
  { label: 'Китайский', value: 'zh' }
]

// Правила валидации
const rules = {
  title: [
    { required: true, message: 'Название книги обязательно', trigger: 'blur' },
    { min: 1, max: 255, message: 'Название должно быть от 1 до 255 символов', trigger: 'blur' }
  ],
  author: [
    { required: true, message: 'Автор обязателен', trigger: 'blur' },
    { min: 1, max: 255, message: 'Имя автора должно быть от 1 до 255 символов', trigger: 'blur' }
  ],
  published_date: [
    { required: true, type: 'number', message: 'Дата публикации обязательна', trigger: 'blur' }
  ],
  isbn: [
    { required: true, message: 'ISBN обязателен', trigger: 'blur' }
  ],
  pages: [
    { required: true, type: 'number', min: 1, message: 'Количество страниц должно быть положительным числом', trigger: 'blur' }
  ],
  language: [
    { required: true, message: 'Язык обязателен', trigger: 'change' }
  ]
}

// Обработка отправки формы
const handleSubmit = (e) => {
  e.preventDefault()

  formRef.value?.validate(async (errors) => {
    if (!errors) {
      loading.value = true
      try {
        // Преобразуем данные для отправки
        const submitData = {
          ...bookForm.value,
          genre_ids: bookForm.value.genre_ids.map(id => Number(id) || 0),
          series_id: Number(bookForm.value.series_id) || 0,
          pages: Number(bookForm.value.pages) || 0
        }

        // Вызываем метод из хранилища
        await store.createBook(submitData)

        // Вместо useMessage используем console.log или другой способ уведомления
        console.log('Книга успешно создана!')
        alert('Книга успешно создана!') // временное решение

        resetForm()

      } catch (error) {
        console.error('Ошибка при создании книги:', error)
        alert('Ошибка при создании книги: ' + (error.response?.data?.detail || error.message))
      } finally {
        loading.value = false
      }
    } else {
      alert('Пожалуйста, заполните все обязательные поля корректно')
    }
  })
}

// Сброс формы
const resetForm = () => {
  bookForm.value = {
    title: '',
    author: '',
    description: '',
    published_date: null,
    isbn: '',
    pages: 0,
    language: 'ru',
    series_id: 0,
    genre_ids: []
  }
  formRef.value?.restoreValidation()
}
</script>

<style scoped>
.create-book-wrapper {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.create-book-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.form-hint {
  font-size: 12px;
  color: #8c8c8c;
  margin-top: 4px;
}
</style>
