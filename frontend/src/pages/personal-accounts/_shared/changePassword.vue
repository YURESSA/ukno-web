<template>
  <n-modal
    :show="true"
    preset="card"
    title="Сменить пароль"
    style="width: min(520px, calc(100% - 32px)); border-radius: 20px"
    :mask-closable="!saving"
    :close-on-esc="!saving"
    :closable="!saving"
    @update:show="visible => { if (!visible) emit('close') }"
  >
    <form class="password-form" novalidate @submit.prevent="handleSubmit" @input="formError = ''">
      <label>
        Текущий пароль
        <input
          v-model="passwords.old_password"
          type="password"
          name="old_password"
          autocomplete="current-password"
          :disabled="saving"
          :aria-invalid="Boolean(showErrors && errors.old_password)"
          required
        >
        <span v-if="showErrors && errors.old_password" class="password-error" role="alert">{{ errors.old_password }}</span>
      </label>
      <label>
        Новый пароль
        <input
          v-model="passwords.new_password"
          type="password"
          name="new_password"
          autocomplete="new-password"
          :disabled="saving"
          :aria-invalid="Boolean(showErrors && errors.new_password)"
          minlength="5"
          required
        >
        <span v-if="showErrors && errors.new_password" class="password-error" role="alert">{{ errors.new_password }}</span>
      </label>
      <label>
        Повторите новый пароль
        <input
          v-model="confirmation"
          type="password"
          name="password_confirmation"
          autocomplete="new-password"
          :disabled="saving"
          :aria-invalid="Boolean(showErrors && errors.confirmation)"
          required
        >
        <span v-if="showErrors && errors.confirmation" class="password-error" role="alert">{{ errors.confirmation }}</span>
      </label>
      <p v-if="formError" class="password-error" role="alert">{{ formError }}</p>
      <div class="password-actions">
        <BaseButton type="submit" text="Сохранить" :loading="saving" />
        <DefaultButton type="button" text="Сбросить" :disabled="saving" @click="resetForm" />
      </div>
    </form>
  </n-modal>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { NModal } from 'naive-ui'
import BaseButton from '@/components/ui/button/BaseButton.vue'
import DefaultButton from '@/components/ui/button/DefaultButton.vue'
import { useDataStore } from '@/stores/counter'
import { getApiErrorMessage } from '@/utils/apiError'
import { notification } from '@/utils/notification'

const emit = defineEmits(['close'])
const store = useDataStore()

const passwords = reactive({ old_password: '', new_password: '' })
const confirmation = ref('')
const showErrors = ref(false)
const saving = ref(false)
const formError = ref('')

const errors = computed(() => ({
  old_password: passwords.old_password ? '' : 'Введите текущий пароль',
  new_password: passwords.new_password.length < 5 ? 'Введите не менее 5 символов' : '',
  confirmation: !confirmation.value
    ? 'Повторите новый пароль'
    : confirmation.value !== passwords.new_password ? 'Пароли не совпадают' : '',
}))

async function handleSubmit() {
  if (saving.value) return
  showErrors.value = true
  formError.value = ''
  if (Object.values(errors.value).some(Boolean)) return

  saving.value = true
  try {
    await store.PutPassword({ ...passwords })
    emit('close')
    notification('Пароль успешно изменён!', 'positive')
  } catch (error) {
    formError.value = getApiErrorMessage(error, 'Не удалось изменить пароль. Попробуйте ещё раз.')
  } finally {
    saving.value = false
  }
}

function resetForm() {
  passwords.old_password = ''
  passwords.new_password = ''
  confirmation.value = ''
  formError.value = ''
  showErrors.value = false
}
</script>

<style scoped>
.password-form,
.password-form label {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.password-form label {
  gap: 6px;
  font-size: 16px;
}

.password-form input {
  box-sizing: border-box;
  width: 100%;
  min-width: 0;
  padding: 10px 12px;
  border: 1px solid #b2b2b2;
  border-radius: 8px;
  font: inherit;
}

.password-form input:focus {
  outline: 2px solid #f25c03;
  outline-offset: 2px;
}

.password-form input[aria-invalid='true'] {
  border-color: #b42318;
}

.password-error {
  margin: 0;
  color: #b42318;
  font-size: 14px;
}

.password-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.password-actions button {
  flex: 1 1 130px;
  width: auto;
  height: 45px;
  padding: 10px 16px;
}
</style>
