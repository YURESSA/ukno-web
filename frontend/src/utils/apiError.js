const statusMessages = {
  400: 'Проверьте введённые данные.',
  401: 'Не удалось подтвердить авторизацию. Войдите снова.',
  403: 'Недостаточно прав для выполнения действия.',
  404: 'Запрошенные данные не найдены.',
  409: 'Данные изменились или уже существуют. Обновите страницу и повторите попытку.',
  413: 'Файл слишком большой. Выберите файл меньшего размера.',
  422: 'Проверьте введённые данные.',
  429: 'Слишком много запросов. Повторите попытку позже.',
}

function details(value) {
  if (typeof value === 'string') return value.trim()
  if (Array.isArray(value)) return value.map(details).filter(Boolean).join('; ')
  if (value && typeof value === 'object') {
    return Object.entries(value).map(([key, item]) => `${key}: ${details(item)}`).join('; ')
  }
  return ''
}

export function getApiErrorMessage(error, fallback = 'Не удалось выполнить запрос.') {
  if (error?.code === 'ERR_CANCELED') return ''
  if (error?.code === 'ECONNABORTED' || error?.code === 'ETIMEDOUT') {
    return 'Сервер не ответил вовремя. Повторите попытку.'
  }
  if (!error?.response) {
    return error?.request || error?.code === 'ERR_NETWORK'
      ? 'Нет связи с сервером. Проверьте подключение и повторите попытку.'
      : fallback
  }
  const { status, data } = error.response
  if (status >= 500) return 'Ошибка сервера. Повторите попытку позже.'
  const fields = details(data?.errors)
  const text = [data?.message, data?.msg, data?.error, data?.detail]
    .find(value => typeof value === 'string' && value.trim())
  return fields || text?.trim() || statusMessages[status] || fallback
}
