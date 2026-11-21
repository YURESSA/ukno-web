import { effectScope, onScopeDispose, reactive, shallowRef, watch } from 'vue'
import { getAdminFieldError, getAdminIssues } from '@/utils/adminValidation'
import { getApiErrorMessage, getApiFieldMessage } from '@/utils/apiError'

export function useAdminValidation() {
  const submitted = shallowRef(reactive(new WeakSet()))
  const touched = shallowRef(reactive(new WeakMap()))
  const serverErrors = shallowRef(reactive(new WeakMap()))
  const fields = new WeakMap()
  const rowKeys = new WeakMap()
  let requests = new WeakMap()
  let errorScope = effectScope(true)
  let nextRowKey = 0

  function rowKey(model) {
    if (!rowKeys.has(model)) {
      nextRowKey += 1
      rowKeys.set(model, nextRowKey)
    }
    return rowKeys.get(model)
  }

  function fieldProps(model, kind, key, isEdit = false, root = model, path = key) {
    if (!fields.has(model)) {
      fields.set(model, new Map())
    }
    fields.get(model).set(key, { model, key })

    if (root !== model) {
      if (!fields.has(root)) {
        fields.set(root, new Map())
      }
      fields.get(root).set(path, { model, key })
    }

    const wasSubmitted = submitted.value.has(root) || submitted.value.has(model)
    const wasTouched = touched.value.get(model)?.has(key)
    const clientFeedback =
      wasSubmitted || wasTouched ? getAdminFieldError(model, kind, key, isEdit) : ''
    const serverFeedback = serverErrors.value.get(model)?.get(key)
    const feedback = clientFeedback || serverFeedback || undefined

    return {
      feedback,
      validationStatus: feedback ? 'error' : undefined,
      onFocusout: (event) => {
        const focusStayedInField =
          event.relatedTarget && event.currentTarget.contains(event.relatedTarget)
        if (focusStayedInField) {
          return
        }
        if (!touched.value.has(model)) {
          touched.value.set(model, new Set())
        }
        touched.value.get(model).add(key)
      },
    }
  }

  function submitValidation(model, kind, isEdit = false) {
    submitted.value.add(model)
    const snapshot = new Map()
    for (const [path, field] of fields.get(model) || []) {
      const parentPath = path.split('.').slice(0, -1)
      const owner = parentPath.reduce((current, segment) => current?.[segment], model)
      if (owner !== field.model) {
        continue
      }
      serverErrors.value.get(owner)?.delete(field.key)
      snapshot.set(path, { ...field, value: owner[field.key] })
    }
    requests.set(model, snapshot)
    return getAdminIssues(model, kind, isEdit)
  }

  function applyApiErrors(error, model, fallback, aliases = {}) {
    const snapshot = requests.get(model)
    const { status, data } = error?.response || {}
    const errors = [400, 409, 422].includes(status) ? data?.errors : null
    const paths = []
    const unmappedErrors = []
    for (const [key, value] of Object.entries(errors || {})) {
      const path = Object.hasOwn(aliases, key) ? aliases[key] : key.replace(/\[(\d+)\]/g, '.$1')
      const field = snapshot?.get(path)
      const feedback = getApiFieldMessage(value)
      const fieldHasChanged = field && field.model[field.key] !== field.value
      if (!field || !feedback || fieldHasChanged) {
        unmappedErrors.push([key, value])
        continue
      }
      const { model: owner, key: fieldKey } = field
      if (!serverErrors.value.has(owner)) {
        serverErrors.value.set(owner, new Map())
      }
      const feedbackByField = serverErrors.value.get(owner)
      feedbackByField.set(fieldKey, feedback)
      errorScope.run(() => {
        watch(
          () => owner[fieldKey],
          () => feedbackByField.delete(fieldKey),
          { once: true, flush: 'sync' },
        )
      })
      paths.push(path)
    }
    if (!paths.length) {
      return { paths, message: getApiErrorMessage(error, fallback) }
    }
    if (!unmappedErrors.length) {
      return { paths, message: '' }
    }
    const remaining = { response: { status, data: { errors: Object.fromEntries(unmappedErrors) } } }
    return { paths, message: getApiErrorMessage(remaining, fallback) }
  }

  function resetValidation() {
    submitted.value = reactive(new WeakSet())
    touched.value = reactive(new WeakMap())
    serverErrors.value = reactive(new WeakMap())
    requests = new WeakMap()
    errorScope.stop()
    errorScope = effectScope(true)
  }

  onScopeDispose(() => errorScope.stop())

  return { fieldProps, submitValidation, resetValidation, applyApiErrors, rowKey }
}
