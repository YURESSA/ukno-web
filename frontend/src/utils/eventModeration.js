export const moderationOptions = [
  { value: 'pending', label: 'На проверке', type: 'warning' },
  { value: 'returned', label: 'На доработке', type: 'error' },
  { value: 'approved', label: 'Одобрено', type: 'success' },
]

export const eventModeration = status => moderationOptions.find(item => item.value === status)
  || { label: 'Статус недоступен', type: 'default' }
