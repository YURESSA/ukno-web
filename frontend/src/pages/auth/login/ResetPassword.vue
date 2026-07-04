<template>
  <div class="page-wrapper">
    <div class="login-wrapper">
      <form @submit.prevent="handleSubmit">
        <h3>Новый пароль</h3>
        <p class="description">Введите новый пароль для вашего аккаунта.</p>
        <input
          type="password"
          class="text-l text-medium"
          name="password"
          placeholder="Новый пароль *"
          v-model="password"
          required
          autocomplete="off"
          minlength="5"
        >
        <input
          type="password"
          class="text-l text-medium"
          name="confirmPassword"
          placeholder="Подтвердите пароль *"
          v-model="confirmPassword"
          required
          autocomplete="off"
          minlength="5"
        >
        <span class="error-message" v-if="error">{{ error }}</span>
        <DefaultButton type="submit" class="sumbit--btn" :text="loading ? 'Сброс...' : 'Сбросить пароль'" :disabled="loading"/>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import DefaultButton from '@/components/UI/button/DefaultButton.vue';
import { useDataStore } from '@/stores/counter';
import { notification } from '@/utils/notification';

const store = useDataStore();
const route = useRoute();
const router = useRouter();

const password = ref('');
const confirmPassword = ref('');
const error = ref('');
const loading = ref(false);
const token = ref('');

onMounted(() => {
  token.value = route.query.token;
  if (!token.value) {
    notification('Токен отсутствует или недействителен', 'negative');
    router.push('/login');
  }
});

const handleSubmit = async () => {
  if (password.value !== confirmPassword.value) {
    error.value = 'Пароли не совпадают';
    return;
  }

  if (password.value.length < 5) {
    error.value = 'Пароль должен быть не менее 5 символов';
    return;
  }

  loading.value = true;
  error.value = '';

  try {
    await store.PostResetPassword(JSON.stringify({
      token: token.value,
      new_password: password.value
    }));
    await notification('Пароль успешно изменен', 'positive');
    router.push('/login');
  } catch (err) {
    notification(err.response?.data?.message || 'Ошибка при смене пароля', 'negative');
    console.error(err);
  } finally {
    loading.value = false;
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

h3 {
  text-align: center;
  margin-bottom: 10px;
}

.description {
  text-align: center;
  font-size: 18px;
  color: #333;
  margin-bottom: 10px;
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

.sumbit--btn {
  width: 100%;
  padding: 20px;
  font-size: 24px;
  border-radius: 30px;
  border: 2px solid #333333;
  background-color: rgba(255, 255, 255, 0);
  color: #333333;
  margin-top: 10px;
}

.error-message {
  color: red;
  font-size: 20px;
  margin-top: -20px;
  font-weight: 700;
  display: block;
}

@media (max-width: 768px) {
  .page-wrapper {
    padding: 0px 24px;
    justify-content: flex-start;
    align-items: flex-start;
  }

  form {
    width: calc(100% - 48px);
    padding: 30px 20px;
    border-radius: 24px;
    gap: 20px;
    transform: translateY(0);
    border-width: 1.5px;
    backdrop-filter: blur(18px);
    background: rgba(253, 253, 253, 0.18);
  }

  input {
    padding: 14px 0;
    margin-bottom: 16px;
    font-size: 16px;
  }

  .sumbit--btn {
    padding: 18px;
    font-size: 16px;
    margin-top: 20px;
  }

  .description {
    font-size: 14px;
  }
}
</style>
