import { getRequiredRequisiteTitle } from './requiredRequisites'

const requiredFields = {
  user: [
    ['full_name', 'Введите ФИО'],
    ['email', 'Введите электронную почту'],
  ],
  event: [
    ['title', 'Введите название события'],
    ['description', 'Введите описание события'],
    ['place', 'Укажите место проведения'],
  ],
  residentEvent: [
    ['title', 'Введите название события'],
    ['description', 'Введите описание события'],
    ['category', 'Выберите категорию'],
    ['format_type', 'Выберите формат'],
    ['age_category', 'Выберите возрастную категорию'],
    ['place', 'Укажите место проведения'],
  ],
  news: [
    ['title', 'Введите заголовок'],
    ['content', 'Введите текст новости'],
  ],
  category: [['category_name', 'Введите название категории']],
  format: [['format_type_name', 'Введите название формата']],
  age: [['age_category_name', 'Введите название возрастной категории']],
  project: [
    ['title', 'Введите название'],
    ['link', 'Введите ссылку'],
  ],
  partner: [['name', 'Введите название партнёра']],
  history: [
    ['title', 'Введите название'],
    ['description', 'Введите описание'],
  ],
  team: [['full_name', 'Введите ФИО']],
  requisites: [['title', 'Введите название']],
  culture: [['text', 'Введите текст']],
  product: [['name', 'Введите название товара']],
  merchCategory: [['name', 'Введите название категории']],
}

const richTextFields = { event: 'description', residentEvent: 'description', news: 'content' }
const nonNegativeFields = ['order_index', 'duration', 'distance_to_center', 'time_to_nearest_stop']
const userRoles = ['admin', 'resident', 'user']
const maxPhoneInputLength = 32

const hasText = (value) => typeof value === 'string' && value.trim().length > 0
const isNonNegativeNumber = (value) =>
  typeof value === 'number' && Number.isFinite(value) && value >= 0

function hasRichText(value) {
  if (typeof value !== 'string') {
    return false
  }

  const plainText = value.replace(/<[^>]*>/g, '').replace(/&nbsp;|&#0*160;|&#x0*a0;/gi, ' ')
  return hasText(plainText)
}

export const validEmail = (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value || '')

export function validLink(value) {
  if (!value) {
    return true
  }
  if (typeof value !== 'string' || /[\s\\]/.test(value)) {
    return false
  }
  if (value.startsWith('/') && !value.startsWith('//')) {
    return true
  }

  try {
    const { protocol } = new URL(value)
    return protocol === 'http:' || protocol === 'https:'
  } catch {
    return false
  }
}

const requiredValues = {
  user: ['role', 'password'],
  event: ['category_id', 'format_type_id', 'age_category_id', 'duration', 'photos'],
  residentEvent: ['duration'],
  session: ['start_datetime', 'max_participants', 'cost'],
  history: ['date'],
  product: ['price', 'stock', 'colors', 'images'],
  color: ['name'],
  size: ['size_name', 'stock'],
  banner: ['image'],
  requisites: ['file'],
}

const nestedFields = {
  event: ['sessions', 'session'],
  residentEvent: ['sessions', 'session'],
  product: ['colors', 'color'],
  color: ['sizes', 'size'],
}

export function getAdminIssues(model, kind, isEdit = false) {
  const keys = new Set([
    ...(requiredFields[kind] || []).map(([key]) => key),
    ...(requiredValues[kind] || []),
    ...Object.keys(model),
  ])
  const issues = []
  for (const key of keys) {
    const message = getAdminFieldError(model, kind, key, isEdit)
    if (message) {
      issues.push({ path: key, message })
    }
  }
  const nested = nestedFields[kind]
  if (nested && (kind !== 'product' || model.withSizeChart)) {
    const [key, childKind] = nested
    const children = model[key] || []
    children.forEach((child, index) => {
      for (const issue of getAdminIssues(child, childKind, isEdit)) {
        issues.push({ ...issue, path: `${key}.${index}.${issue.path}` })
      }
    })
  }
  return issues
}

export function validateAdmin(model, kind, isEdit = false) {
  return getAdminIssues(model, kind, isEdit)[0]?.message || ''
}

export function allowPhoneInput(value) {
  const allowedCharacters = /^\+?[0-9 ()-]*$/
  return allowedCharacters.test(value) && value.length <= maxPhoneInputLength
}

export function sanitizePhoneInput(value) {
  const allowedCharacters = String(value || '').replace(/[^0-9+ ()-]/g, '')
  const phone = allowedCharacters.replace(/\+/g, (_, offset) => (offset === 0 ? '+' : ''))
  return phone.slice(0, maxPhoneInputLength)
}

function isValidPhone(value) {
  if (!allowPhoneInput(value)) {
    return false
  }

  const phone = value.replace(/[ ()-]/g, '')
  const phoneNumberPattern = /^\+?\d{7,15}$/
  return phoneNumberPattern.test(phone)
}

export function getAdminFieldError(model, kind, key, isEdit = false) {
  const value = model[key]
  const isEvent = kind === 'event' || kind === 'residentEvent'

  if (kind === 'user' && key === 'email' && isEdit) {
    return ''
  }

  const requiredField = (requiredFields[kind] || []).find(([field]) => field === key)
  if (requiredField) {
    const hasValue = richTextFields[kind] === key ? hasRichText(value) : hasText(value)
    if (!hasValue) {
      return requiredField[1]
    }
  }

  if (isEvent && key === 'duration' && (!Number.isInteger(value) || value < 0)) {
    return 'Укажите продолжительность целым неотрицательным числом минут'
  }
  if (isEvent && key === 'is_active' && value !== undefined && typeof value !== 'boolean') {
    return 'Выберите статус события'
  }
  if (kind === 'color' && key === 'name' && !hasText(value)) {
    return 'Введите название цвета'
  }
  if (kind === 'size' && key === 'size_name' && !hasText(value)) {
    return 'Укажите размер'
  }
  if (kind === 'size' && key === 'stock' && (!Number.isInteger(value) || value < 0)) {
    return 'Укажите целый неотрицательный остаток'
  }

  if (['email', 'contact_email'].includes(key) && value && !validEmail(value)) {
    return 'Введите корректную электронную почту'
  }
  if (['link', 'link_url'].includes(key) && !validLink(value)) {
    return 'Введите корректную ссылку: https://… или /путь'
  }
  if (key === 'phone' && value && !isValidPhone(value)) {
    return 'Введите номер телефона: от 7 до 15 цифр, например +7 (999) 123-45-67'
  }
  if (kind === 'user' && key === 'role' && !userRoles.includes(value)) {
    return 'Выберите роль'
  }
  if (kind === 'user' && key === 'password' && (!isEdit || value) && !hasText(value)) {
    return 'Введите пароль'
  }

  if (nonNegativeFields.includes(key) && value !== undefined) {
    const isOrderIndex = key === 'order_index'
    const needsValidation = value !== null || isOrderIndex
    const invalidOrderIndex = isOrderIndex && !Number.isInteger(value)

    if (needsValidation && (!isNonNegativeNumber(value) || invalidOrderIndex)) {
      return 'Укажите корректное неотрицательное число'
    }
  }
  if (
    kind === 'history' &&
    key === 'date' &&
    (value == null || !Number.isFinite(new Date(value).getTime()))
  ) {
    return 'Укажите корректную дату'
  }

  if (kind === 'event' && !value) {
    if (key === 'category_id') {
      return 'Выберите категорию'
    }
    if (key === 'format_type_id') {
      return 'Выберите формат'
    }
    if (key === 'age_category_id') {
      return 'Выберите возрастную категорию'
    }
  }
  if (kind === 'event' && key === 'photos' && !isEdit && !value?.length) {
    return 'Добавьте хотя бы одну фотографию события'
  }
  if (kind === 'banner' && key === 'image' && !isEdit && !value) {
    return 'Выберите изображение баннера'
  }
  if (kind === 'requisites' && key === 'file' && !isEdit && !value) {
    return 'Выберите файл документа'
  }
  if (
    kind === 'requisites' &&
    key === 'title' &&
    !model.requiredDocument &&
    getRequiredRequisiteTitle(value)
  ) {
    return 'Замените файл в строке обязательного документа'
  }

  if (kind === 'session') {
    if (key === 'start_datetime' && (!value || !Number.isFinite(new Date(value).getTime()))) {
      return 'Выберите корректные дату и время сеанса'
    }
    if (key === 'max_participants' && (!Number.isInteger(value) || value < 1)) {
      return 'Количество мест должно быть положительным целым числом'
    }
    if (key === 'cost' && !isNonNegativeNumber(value)) {
      return 'Укажите неотрицательную стоимость сеанса'
    }
  }
  if (kind === 'product') {
    if (key === 'price' && !isNonNegativeNumber(value)) {
      return 'Укажите неотрицательную цену товара'
    }
    if (key === 'stock' && !model.withSizeChart && (!Number.isInteger(value) || value < 0)) {
      return 'Укажите целое неотрицательное количество товара'
    }
    if (key === 'colors' && model.withSizeChart && !value?.some(color => color.sizes?.length)) {
      return 'Добавьте хотя бы один цвет с размером'
    }
    if (key === 'images' && !value?.length) {
      return 'Добавьте хотя бы одну фотографию товара'
    }
  }
  if (
    kind === 'merchCategory' &&
    key === 'slug' &&
    value &&
    !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(value)
  ) {
    return 'Slug: латинские строчные буквы, цифры и дефисы'
  }

  return ''
}
