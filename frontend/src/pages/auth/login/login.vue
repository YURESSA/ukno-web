<template>
  <div class="page-wrapper">
    <div class="login-wrapper">
      <form @submit.prevent="handleSubmit">
        <h3>Вход</h3>
        <input
          type="email"
          class="text-l text-medium"
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
          class="text-l text-medium"
          placeholder="Пароль *"
          v-model="formData.password"
          required
          autocomplete="off"
          @input="clearError('password')"
          minlength="5"
        >
        <span class="error-message" v-if="showErrors && errors.password">{{ errors.password }}</span>
        <DefaultButton type="submit" class="sumbit--btn" text="Войти"/>
        <span class="bold">У ВАС НЕТ АККАУНТА? <RouterLink to="register"><span class="text-orange">ЗАРЕГИСТРИРОВАТЬСЯ</span></RouterLink></span>
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
  email: '',
  password: ''
});

const errors = ref({
  email: '',
  password: '',
});

const clearError = (field) => {
  errors.value[field] = '';
};

// Валидация email
const validateEmail = () => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(formData.value.email)) {
    errors.value.email = 'Введите корректный email';
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
    await store.PostLoginUser(JSON.stringify(formData.value));
    await store.GetProfile();
    alert('Вход выполнен успешно!');
    router.back();
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
  transform: translateY(-50px);
}

input {
  padding: 15px 0;
  border: none;
  border-bottom: 1px solid #0000008C;
  transition: background-color 99999999s ease;
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
