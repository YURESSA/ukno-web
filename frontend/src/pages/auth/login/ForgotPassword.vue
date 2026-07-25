<template>
  <div class="page-wrapper">
    <div class="login-wrapper">
      <form @submit.prevent="handleSubmit">
        <h3>Сброс пароля</h3>
        <p class="description">Введите ваш email, и мы отправим вам инструкцию по сбросу пароля.</p>
        <input
          type="email"
          class="text-l text-medium"
          name="email"
          placeholder="E-mail *"
          v-model="email"
          required
          autocomplete="off"
        >
        <span class="error-message" v-if="error">{{ error }}</span>
        <DefaultButton type="submit" class="sumbit--btn" :text="loading ? 'Отправка...' : 'Отправить'" :disabled="loading"/>
        <RouterLink to="/login" class="back-link">Вернуться ко входу</RouterLink>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import DefaultButton from '@/components/ui/button/DefaultButton.vue';
import { useDataStore } from '@/stores/counter';
import { notification } from '@/utils/notification';

const store = useDataStore();
const email = ref('');
const error = ref('');
const loading = ref(false);

const handleSubmit = async () => {
  if (!email.value) {
    error.value = 'Введите email';
    return;
  }

  loading.value = true;
  error.value = '';

  try {
    await store.PostResetPasswordRequest(JSON.stringify({ email: email.value }));
    await notification('Инструкции по сбросу пароля отправлены на ваш email', 'positive');
    email.value = '';
  } catch (err) {
    notification('Ошибка при отправке запроса', 'negative');
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

.back-link {
  text-align: center;
  color: #F25C03;
  text-decoration: none;
  font-weight: 700;
  font-size: 18px;
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
