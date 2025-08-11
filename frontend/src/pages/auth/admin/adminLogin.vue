<template>
  <div class="page-wrapper">
    <div class="login-wrapper">
      <h3>Вход для администратора</h3>
      <form @submit.prevent="handleSubmit">
        <input
          type="email"
          name="email"
          placeholder="e-mail *"
          v-model="formData.username"
          required
          autocomplete="email"
          @input="clearError('email')"
        >
        <span class="error-message" v-if="showErrors && errors.username">{{ errors.username }}</span>
        <input
          type="password"
          name="password"
          placeholder="Пароль *"
          v-model="formData.password"
          required
          autocomplete="password"
          @input="clearError('password')"
          minlength="5"
        >
        <span class="error-message" v-if="showErrors && errors.password">{{ errors.password }}</span>
        <DefaultButton type="submit" class="sumbit--btn" text="Войти"/>
      </form>
      <span>У ВАС НЕТ АККАУНТА? <RouterLink to="register"><span class="text-orange">ЗАРЕГИСТРИРОВАТЬСЯ</span></RouterLink></span>
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
  username: '',
  password: ''
});

const errors = ref({
  username: '',
  password: '',
});

const clearError = (field) => {
  errors.value[field] = '';
};

// Валидация email
const validateEmail = () => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(formData.value.username)) {
    errors.value.username = 'Введите корректный email';
    return false;
  }
  return true;
};

// Валидация телефона
const validatePassword = () => {
  if (formData.value.password.length < 5) {
    errors.value.password = 'Пароль должен быть не менее 5 символов';
    return false;
  }
  return true;
};

const handleSubmit = async () => {
  showErrors.value = true;

  const isEmailValid = validateEmail();
  const isPasswordValid = validatePassword();
  if (!isEmailValid || !isPasswordValid) {
    return;
  }
  try {
    await store.PostLoginAdmin(JSON.stringify(formData.value));
    alert('Вход выполнен успешно!');
    router.push('/');
  } catch (error) {
    if (error.response?.status === 401) {
      alert('Неверные учетные данные');
    } else {
      alert('Произошла ошибка при входе');
    }
    console.error('Ошибка входа', error);
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
  gap: 50px;
  max-width: 600px;
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

.sumbit--btn{
  width: 100%;
  padding: 20px;
  border-radius: 30px;
  border: 2px solid #333333;
  background-color: white;
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
</style>
