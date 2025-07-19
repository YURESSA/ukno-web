<template>
  <div class="modal-wrapper" @click="$emit('close')">
    <div class="modal" @click.stop>
      <form @submit.prevent="handleSubmit" autocomplete="off">
        <div class="header-form">
          <h4>Сменить пароль</h4>
          <IconButton @click="$emit('close')" class="close_btn"><img src="/icon/maki_cross.svg" alt=""></IconButton>
        </div>
        <input
          type="password"
          name="password"
          placeholder="Старый пароль *"
          v-model="formData.old_password"
          required
          autocomplete="new-password"
          @input="clearError('password')"
          minlength="5"
        >
        <input
          type="password"
          name="password"
          placeholder="Новый пароль *"
          v-model="formData.new_password"
          required
          autocomplete="new-password"
          @input="clearError('password')"
          minlength="5"
        >
        <span class="error-message" v-if="showErrors && errors.password">{{ errors.password }}</span>

        <input
          type="password"
          name="passwordConfirmation"
          placeholder="Повторите пароль *"
          v-model="passwordConfirmation"
          required
          autocomplete="new-password"
          @input="clearError('passwordConfirmation')"
        >
        <span class="error-message" v-if="showErrors && errors.passwordConfirmation">{{ errors.passwordConfirmation }}</span>
        <div class="button-wrapper">
          <BaseButton text="Сохранить" />
          <DefaultButton class="reset-button" text="Сбросить" @click="resetForm" type="button" />
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useDataStore } from '@/stores/counter';
import IconButton from '@/components/UI/button/IconButton.vue';
import BaseButton from '@/components/UI/button/BaseButton.vue';
import DefaultButton from '@/components/UI/button/DefaultButton.vue';

const store = useDataStore();
const passwordConfirmation = ref('');
const showErrors = ref(true);
const emit = defineEmits(['close']);

const props = defineProps({
  role: String,
})

const formData = ref({
  old_password: '',
  new_password: ''
});

const errors = ref({
  password: '',
  passwordConfirmation: ''
});

// Валидация пароля
const validatePassword = () => {
  if (formData.value.new_password.length < 5) {
    errors.value.password = 'Пароль должен быть не менее 5 символов';
  } else {
    errors.value.password = '';
  }
  validatePasswordConfirmation();
};

// Проверка совпадения паролей
const validatePasswordConfirmation = () => {
  if (formData.value.new_password !== passwordConfirmation.value) {
    errors.value.passwordConfirmation = 'Пароли не совпадают';
  } else {
    errors.value.passwordConfirmation = '';
  }
};

const clearError = (field) => {
  errors.value[field] = '';
};

const handleSubmit = async () => {
  showErrors.value = true;

  validatePassword();
  validatePasswordConfirmation();

  // Проверяем наличие ошибок
  const hasErrors = Object.values(errors.value).some(error => error !== '');

  if (hasErrors) {
    return;
  }

  let url = ''

  switch(props.role) {
  case 'user':
    url = '/api/user/profile/password'
    break;

  case 'resident':
    url = '/api/resident/profile'
    break;

  case 'admin':
    url = '/api/admin/profile'
    break;

  default:
    console.warn(`Неизвестная роль: ${props.role}`);
    break;
}

  try {
    await store.PutPassword(JSON.stringify(formData.value), url);
    alert('Пароль успешно изменён!');
    emit('close')
  } catch (error) {
    if (error.response?.status === 400) {
      alert('Неверный старый пароль');
    } else {
      alert('Произошла ошибка при смене пароля');
    }
    console.error('Ошибка при смене пароля', error);
  }
};

function resetForm(){
  formData.value.old_password = '';
  formData.value.new_password = '';
  passwordConfirmation.value = '';
}
</script>

<style scoped>
.modal-wrapper{
  display: block;
  content: '';
  width: 100%;
  height: 100vh;
  position: fixed;
  top: 0;
  overflow: hidden;
  background-color: rgba(128, 128, 128, 0.459);
  z-index: 99;
}

.header-form{
  display: flex;
  justify-content: space-between;
}

.button-wrapper{
  display: flex;
  gap: 20px;
}

.modal{
  position: absolute;
  width: 460px;
  background-color: #FFFFFF;
  box-shadow: 0px 4px 12.7px 0px #00000040;
  border-radius: 14px;
  padding: 40px 40px 45px 40px;
  top: 50%;
  left: 50%;
  transform: translateY(-50%) translateX(-50%);
}

form {
  display: flex;
  flex-direction: column;
  gap: 40px;
  margin-bottom: 30px;
}

input {
  padding: 15px 0;
  border: none;
  border-bottom: 1px solid #0000008C;
  transition: all 0.5s ease;
}

input:focus {
  outline: none;
  background-color: #F3F3F3;
}

.reset-button{
  width: 100%;
  height: 45;
  border-radius: 15px;
  padding: 10px 50px;
  color: #000000;
  font-weight: 400;
  font-size: 20px;
}

.close_btn{
  width: 23px;
  height: 23px;
  padding: 4px;
  border-radius: 5px;
  border: none;
  background-color: #EDEDED8A;
}
</style>
