<template>
  <div class="page-wrapper">
    <div class="login-wrapper">
      <form @submit.prevent="handleSubmit" autocomplete="off">
        <h3>Регистрация</h3>
        <input
          type="text"
          name="full_name"
          placeholder="Фамилия Имя *"
          class="text-l text-medium"
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
          class="text-l text-medium"
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
          class="text-l text-medium"
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
          class="text-l text-medium"
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
          class="text-l text-medium"
          v-model="formData.passwordConfirmation"
          required
          autocomplete="new-password"
          @input="clearError('passwordConfirmation')"
        >
        <span class="error-message" v-if="showErrors && errors.passwordConfirmation">{{ errors.passwordConfirmation }}</span>

        <DefaultButton type="submit" class="sumbit--btn" text="Зарегистрироваться"/>
        <span class="bold">У ВАС УЖЕ ЕСТЬ АККАУНТ? <RouterLink to="login"><span class="text-orange">ВОЙТИ</span></RouterLink></span>
      </form>
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
  align-items: center;
  position: relative;
  height: 100%;
  padding: 0px;
}

.login-wrapper {
  display: flex;
  flex-direction: column;
  justify-content: center;
  max-width: 1800px;
  max-height: max-content;
  position: relative;
  z-index: 99;
}

form {
  display: flex;
  flex-direction: column;
  gap: 30px;
  width: 624px;
  border: 2px solid #f25c03;
  border-radius: 38px;
  padding: 40px 30px 30px 30px;
  backdrop-filter: blur(16.5px);
  background: rgba(255, 255, 255, 0.52);
}

input {
  padding: 15px 0;
  border: none;
  border-bottom: 1px solid #0000008C;
  transition: all 0.5s ease;
  margin-bottom: 20px;
  background: rgba(255, 255, 255, 0);
}

input:focus {
  outline: none;
}

.sumbit--btn{
  width: 100%;
  padding: 20px;
  border-radius: 30px;
  border: 2px solid #333333;
  background-color: rgba(255, 255, 255, 0);
  margin-top: 10px;
}

.text-orange{
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
