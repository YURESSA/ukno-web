<template>
  <div class="page-wrapper page--margin">
    <div class="login-wrapper">
      <h3>Регистрация</h3>
      <form @submit.prevent="handleSubmit" autocomplete="off">
        <input
          type="text"
          name="full_name"
          placeholder="Фамилия Имя *"
          v-model="formData.full_name"
          required
          autocomplete="off"
          @input="clearError('full_name')"
        >
        <span class="error-message" v-if="showErrors && errors.full_name">{{ errors.full_name }}</span>
        <input
          type="tel"
          name="phone"
          placeholder="Номер телефона *"
          v-model="formData.phone"
          required
          autocomplete="off"
          @input="clearError('phone')"
        >
        <span class="error-message" v-if="showErrors && errors.phone">{{ errors.phone }}</span>

        <input
          type="email"
          name="email"
          placeholder="e-mail *"
          v-model="formData.email"
          required
          autocomplete="off"
          @input="clearError('email')"
        >
        <span class="error-message" v-if="showErrors && errors.email">{{ errors.email }}</span>

        <input
          type="password"
          name="password"
          placeholder="Пароль *"
          v-model="formData.password"
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
          v-model="formData.passwordConfirmation"
          required
          autocomplete="new-password"
          @input="clearError('passwordConfirmation')"
        >
        <span class="error-message" v-if="showErrors && errors.passwordConfirmation">{{ errors.passwordConfirmation }}</span>

        <DefaultButton type="submit" class="submit--btn" text="Зарегистрироваться"/>
      </form>
      <span>У ВАС УЖЕ ЕСТЬ АККАУНТ? <RouterLink to="login"><span class="orange">ВОЙТИ</span></RouterLink></span>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import DefaultButton from '@/components/UI/button/DefaultButton.vue';
import { useDataStore } from '@/stores/counter';
import router from '@/router';

const store = useDataStore();
const showErrors = ref(false);

const formData = ref({
  phone: '',
  email: '',
  password: '',
  full_name: '',
  role_name: 'user'
});

const errors = ref({
  phone: '',
  email: '',
  password: '',
  passwordConfirmation: ''
});

const clearError = (field) => {
  errors.value[field] = '';
};

// Валидация ФИО
const validateName = () =>{
  if(formData.value.full_name < 3){
    errors.value.full_name = 'Введите корректные ФИО';
  } else{
    errors.value.full_name = ''
  }
}

// Валидация email
const validateEmail = () => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(formData.value.email)) {
    errors.value.email = 'Введите корректный email';
  } else {
    errors.value.email = '';
  }
};

// Валидация телефона
const validatePhone = () => {
  const phoneRegex = /^(\+7|8)[0-9]{10}$/;
  const cleanPhone = formData.value.phone.replace(/[^\d+]/g, '');

  if (!phoneRegex.test(cleanPhone)) {
    errors.value.phone = 'Введите корректный номер телефона';
  } else {
    errors.value.phone = '';
  }
  formData.value.phone = cleanPhone;
};

// Валидация пароля
const validatePassword = () => {
  if (formData.value.password.length < 5) {
    errors.value.password = 'Пароль должен быть не менее 5 символов';
  } else {
    errors.value.password = '';
  }
  validatePasswordConfirmation();
};

// Проверка совпадения паролей
const validatePasswordConfirmation = () => {
  if (formData.value.password !== formData.value.passwordConfirmation) {
    errors.value.passwordConfirmation = 'Пароли не совпадают';
  } else {
    errors.value.passwordConfirmation = '';
  }
};

const handleSubmit = async () => {
  showErrors.value = true;

  // Проверяем все поля перед отправкой
  validateName();
  validateEmail();
  validatePhone();
  validatePassword();
  validatePasswordConfirmation();

  // Проверяем наличие ошибок
  const hasErrors = Object.values(errors.value).some(error => error !== '');

  if (hasErrors) {
    return;
  }

  try {
    await store.PostNewUser(JSON.stringify(formData.value));
    alert('Регистрация прошла успешно!');
    router.push('/login');
  } catch (error) {
    if (error.response?.status === 409) {
      alert('Пользователь с таким email уже существует');
    } else {
      alert('Произошла ошибка при регистрации');
    }
    console.error('Ошибка регистрации', error);
  }
};
</script>

<style scoped>
.page-wrapper {
  display: flex;
  justify-content: center;
  position: relative;
  min-height: calc(100vh - 188px - 246px)
}

.page-wrapper::before {
  content: '';
  position: absolute;
  top: -120px;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('/backgroung/eventsFeed.png') no-repeat;
  background-size: 100% auto;
  z-index: -1;
}

.login-wrapper {
  display: flex;
  flex-direction: column;
  justify-content: center;
  max-width: 1800px;
  position: relative;
}

h3{
  margin-bottom: 40px;
}

form {
  display: flex;
  flex-direction: column;
  gap: 40px;
  width: 600px;
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

.submit--btn{
  width: 100%;
  padding: 20px;
  border-radius: 30px;
  border: 2px solid #333333;
  background-color: white;
}

.orange{
  color: #F25C03;
}

.error-message {
  color: red;
  font-size: 20px;
  margin-top: -20px;
  font-weight: 700;
  display: block;
}

span{
  text-align: center;
}
</style>
