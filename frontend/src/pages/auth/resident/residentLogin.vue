<template>
  <div class="page-wrapper">
    <div class="login-wrapper">
<<<<<<< HEAD
      <h3>Вход для резидента</h3>
      <form @submit.prevent="handleSubmit">
        <input
          type="username"
=======
      <form @submit.prevent="handleSubmit">
        <h3>Вход для резидента</h3>
        <input
          type="username"
          class="text-l text-medium"
>>>>>>> main-frontend
          name="username"
          placeholder="e-mail *"
          v-model="formData.email"
          required
          autocomplete="email"
        >
        <input
          type="password"
<<<<<<< HEAD
=======
          class="text-l text-medium"
>>>>>>> main-frontend
          name="password"
          placeholder="Пароль *"
          v-model="formData.password"
          required
          autocomplete="password"
        >
        <DefaultButton type="submit" class="sumbit--btn" text="Войти"/>
      </form>
<<<<<<< HEAD
      <span>У ВАС НЕТ АККАУНТА? <RouterLink to="register"><span class="orange">ЗАРЕГЕСТРИРОВАТЬСЯ</span></RouterLink></span>
=======
>>>>>>> main-frontend
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import DefaultButton from '@/components/UI/button/DefaultButton.vue';
import { useDataStore } from '@/stores/counter';
import router from '@/router';

const store = useDataStore();

const formData = ref({
  email: '',
  password: ''
});


const handleSubmit = async () => {
  try {
    await store.PostLoginResident(JSON.stringify(formData.value));
<<<<<<< HEAD
    alert('Вход выполнен успешно!');
    router.push('/');
=======
    await store.GetResidentProfile();
    alert('Вход выполнен успешно!');
    router.back();
>>>>>>> main-frontend
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
<<<<<<< HEAD
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
=======
  align-items: center;
  position: relative;
  height: 100%;
  padding: 0px;
>>>>>>> main-frontend
}

.login-wrapper {
  display: flex;
  flex-direction: column;
  justify-content: center;
  max-width: 1800px;
<<<<<<< HEAD
  position: relative;
}

h3{
  margin-bottom: 40px;
=======
  max-height: max-content;
  position: relative;
  z-index: 99;
>>>>>>> main-frontend
}

form {
  display: flex;
  flex-direction: column;
<<<<<<< HEAD
  gap: 50px;
  max-width: 600px;
  margin-bottom: 30px;
=======
  gap: 30px;
  width: 624px;
  border: 2px solid #f25c03;
  border-radius: 38px;
  padding: 40px 30px 30px 30px;
  backdrop-filter: blur(16.5px);
  background: rgba(255, 255, 255, 0.52);
  transform: translateY(-50px);
>>>>>>> main-frontend
}

input {
  padding: 15px 0;
  border: none;
  border-bottom: 1px solid #0000008C;
<<<<<<< HEAD
  transition: all 0.5s ease;
=======
  transition: background-color 99999999s ease;
  margin-bottom: 20px;
  background: rgba(255, 255, 255, 0);
>>>>>>> main-frontend
}

input:focus {
  outline: none;
<<<<<<< HEAD
  background-color: #F3F3F3;
=======
>>>>>>> main-frontend
}

.sumbit--btn{
  width: 100%;
  padding: 20px;
  border-radius: 30px;
  border: 2px solid #333333;
<<<<<<< HEAD
  background-color: white;
}

.orange{
=======
  background-color: rgba(255, 255, 255, 0);
  margin-top: 10px;
}

.text-orange{
>>>>>>> main-frontend
  color: #F25C03;
}

.error-message {
  color: red;
  font-size: 20px;
  margin-top: -20px;
  font-weight: 700;
  display: block;
}
<<<<<<< HEAD
=======

span{
  text-align: center;
}
>>>>>>> main-frontend
</style>
