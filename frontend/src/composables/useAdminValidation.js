import { ref } from 'vue'
import { getAdminFieldError } from '@/utils/adminValidation'

export function useAdminValidation() {
  const submitted = ref(false)
  const touched = ref(new Set())
  const touchField = path => touched.value.add(path)
  const fieldFeedback = (model, kind, key, path, isEdit = false) => {
    if (!submitted.value && !touched.value.has(path)) return undefined
    return getAdminFieldError(model, kind, key, isEdit) || undefined
  }
  const fieldProps = (model, kind, key, path, isEdit = false) => {
    const feedback = fieldFeedback(model, kind, key, path, isEdit)
    return {
      feedback,
      validationStatus: feedback ? 'error' : undefined,
      onFocusout: () => touchField(path),
    }
  }
  const resetValidation = () => {
    submitted.value = false
    touched.value = new Set()
  }
  return { submitted, fieldProps, resetValidation }
}
