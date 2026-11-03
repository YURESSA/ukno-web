import { ref } from 'vue'
import { getAdminFieldError } from '@/utils/adminValidation'
import { getApiErrorMessage } from '@/utils/apiError'

export function useAdminValidation() {
  const submitted = ref(false)
  const touched = ref(new Set())
  const serverErrors = ref({})
  const applyApiErrors = (error, model) => {
    serverErrors.value = Object.fromEntries(Object.entries(error.response?.data?.errors || {}).map(([key, value]) => [key, {
      value: model[key], feedback: getApiErrorMessage({ response: { status: 400, data: { errors: { [key]: value } } } }),
    }]))
  }
  const touchField = path => touched.value.add(path)
  const fieldFeedback = (model, kind, key, path, isEdit = false) => {
    if (!submitted.value && !touched.value.has(path)) return undefined
    const server = serverErrors.value[key]
    return getAdminFieldError(model, kind, key, isEdit) || (server && server.value === model[key] ? server.feedback : undefined)
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
    serverErrors.value = {}
  }
  return { submitted, fieldProps, resetValidation, applyApiErrors }
}
