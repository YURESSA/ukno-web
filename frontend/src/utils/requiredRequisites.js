export const PERSONAL_DATA_REQUISITE = 'Обработка персональных данных'
export const REQUIRED_REQUISITES = [PERSONAL_DATA_REQUISITE, 'Договор оферты']

const normalizeTitle = title => String(title ?? '').trim().replace(/\s+/g, ' ').toLocaleLowerCase('ru')

export function getRequiredRequisiteTitle(title) {
  const normalized = normalizeTitle(title)
  return REQUIRED_REQUISITES.find(requiredTitle => normalizeTitle(requiredTitle) === normalized)
}

export function findRequiredRequisite(requisites, title) {
  if (!Array.isArray(requisites)) return undefined
  const matches = requisites.filter(item => getRequiredRequisiteTitle(item.title) === title)
  return matches.find(item => item.file) ?? matches[0]
}
