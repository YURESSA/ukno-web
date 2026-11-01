const requiredFields = {
    user: [['full_name', 'Введите ФИО'], ['email', 'Введите электронную почту']],
    event: [['title', 'Введите название события'], ['description', 'Введите описание события'], ['place', 'Укажите место проведения']],
    residentEvent: [['title', 'Введите название события'], ['description', 'Введите описание события'], ['category', 'Выберите категорию'], ['format_type', 'Выберите формат'], ['age_category', 'Выберите возрастную категорию'], ['place', 'Укажите место проведения']],
    news: [['title', 'Введите заголовок'], ['content', 'Введите текст новости']],
    category: [['category_name', 'Введите название категории']],
    format: [['format_type_name', 'Введите название формата']],
    age: [['age_category_name', 'Введите название возрастной категории']],
    project: [['title', 'Введите название'], ['link', 'Введите ссылку']],
    partner: [['name', 'Введите название партнёра']],
    history: [['title', 'Введите название'], ['description', 'Введите описание']],
    team: [['full_name', 'Введите ФИО']],
    requisites: [['title', 'Введите название']],
    culture: [['text', 'Введите текст']],
    product: [['name', 'Введите название товара']],
    merchCategory: [['name', 'Введите название категории']],
  }

const text = value => typeof value === 'string' && value.replace(/<[^>]*>/g, '').replace(/&nbsp;/g, ' ').trim().length > 0
const nonNegative = value => typeof value === 'number' && Number.isFinite(value) && value >= 0
export const validEmail = value => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value || '')
export function validLink(value) {
  if (!value) return true
  if (typeof value !== 'string' || /\s/.test(value)) return false
  if (value.startsWith('/') && !value.startsWith('//')) return true
  try { return ['http:', 'https:'].includes(new URL(value).protocol) } catch { return false }
}

export function validateAdmin(model, kind, isEdit = false) {

  const keys = new Set([...(requiredFields[kind] || []).map(([key]) => key), ...Object.keys(model)])
  if (kind === 'user') keys.add('password')
  if (['event', 'residentEvent'].includes(kind)) keys.add('duration')
  for (const key of keys) {
    const error = getAdminFieldError(model, kind, key, isEdit)
    if (error) return error
  }
  if (['event', 'residentEvent'].includes(kind)) {
    if (kind === 'event' && (!model.category_id || !model.format_type_id || !model.age_category_id)) return 'Выберите категорию, формат и возрастную категорию'
    for (const session of model.sessions || []) {
      const error = validateAdmin(session, 'session')
      if (error) return error
    }
  }
  if (kind === 'session') {
    if (!model.start_datetime || !Number.isFinite(new Date(model.start_datetime).getTime())) return 'Выберите корректные дату и время сеанса'
    if (!Number.isInteger(model.max_participants) || model.max_participants < 1) return 'Количество мест должно быть положительным целым числом'
    if (!nonNegative(model.cost)) return 'Укажите неотрицательную стоимость сеанса'
  }
  if (kind === 'product') {
    if (!nonNegative(model.price)) return 'Укажите неотрицательную цену товара'
    for (const color of model.colors || []) {
      if (!text(color.name)) return 'Введите название каждого цвета'
      for (const size of color.sizes || []) {
        if (!text(size.size_name)) return 'Укажите каждый размер'
        if (!Number.isInteger(size.stock) || size.stock < 0) return 'Остаток должен быть неотрицательным целым числом'
      }
    }
  }
  if (kind === 'merchCategory' && model.slug && !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(model.slug)) return 'Slug: латинские строчные буквы, цифры и дефисы'
  return ''
}

export function allowPhoneInput(value) {
  return /^\+?[0-9 ()-]*$/.test(value) && value.length <= 32
}

export function sanitizePhoneInput(value) {
  const cleaned = String(value || '').replace(/[^0-9+ ()-]/g, '')
  return cleaned.replace(/\+/g, (match, offset) => offset === 0 ? '+' : '').slice(0, 32)
}

export function getAdminFieldError(model, kind, key, isEdit = false) {
  const value = model[key]
  const required = (requiredFields[kind] || []).find(([field]) => field === key)
  if (required && !text(value)) return required[1]
  if (['event', 'residentEvent'].includes(kind) && key === 'duration' && (!Number.isInteger(value) || value < 0)) return 'Укажите продолжительность целым неотрицательным числом минут'
  if (['event', 'residentEvent'].includes(kind) && key === 'is_active' && value !== undefined && typeof value !== 'boolean') return 'Выберите статус события'
  if (kind === 'color' && key === 'name' && !text(value)) return 'Введите название цвета'
  if (kind === 'size' && key === 'size_name' && !text(value)) return 'Укажите размер'
  if (kind === 'size' && key === 'stock' && (!Number.isInteger(value) || value < 0)) return 'Укажите целый неотрицательный остаток'
  if (['email', 'contact_email'].includes(key) && value && !validEmail(value)) return 'Введите корректную электронную почту'
  if (['link', 'link_url'].includes(key) && !validLink(value)) return 'Введите корректную ссылку: https://… или /путь'
  if (key === 'phone' && value && (!allowPhoneInput(value) || !/^\+?\d{7,15}$/.test(value.replace(/[ ()-]/g, '')))) return 'Введите номер телефона: от 7 до 15 цифр, например +7 (999) 123-45-67'
  if (kind === 'user' && key === 'role' && !['admin', 'resident', 'user'].includes(value)) return 'Выберите роль'
  if (kind === 'user' && key === 'password' && !isEdit && !text(value)) return 'Введите пароль'
  if (['order_index', 'duration', 'distance_to_center', 'time_to_nearest_stop'].includes(key) && value !== undefined && (value !== null || key === 'order_index')) {
    if (!nonNegative(value) || (key === 'order_index' && !Number.isInteger(value))) return 'Укажите корректное неотрицательное число'
  }
  if (kind === 'history' && key === 'date' && (value == null || !Number.isFinite(new Date(value).getTime()))) return 'Укажите корректную дату'
  if (kind === 'event' && ['category_id', 'format_type_id', 'age_category_id'].includes(key) && !value) return 'Выберите значение'
  if (kind === 'session') {
    if (key === 'start_datetime' && (!value || !Number.isFinite(new Date(value).getTime()))) return 'Выберите корректные дату и время сеанса'
    if (key === 'max_participants' && (!Number.isInteger(value) || value < 1)) return 'Количество мест должно быть положительным целым числом'
    if (key === 'cost' && !nonNegative(value)) return 'Укажите неотрицательную стоимость сеанса'
  }
  if (kind === 'product' && key === 'price' && !nonNegative(value)) return 'Укажите неотрицательную цену товара'
  if (kind === 'merchCategory' && key === 'slug' && value && !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(value)) return 'Slug: латинские строчные буквы, цифры и дефисы'
  return ''
}
