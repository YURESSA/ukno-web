<template>
  <div class="page-wrapper">
    <div class="header">
      <IconBtn><img src='../../public/assets/icon/icon-arrow.svg'></IconBtn>
      <h2>Авторизация</h2>
    </div>
    <div class="login">
      <div class="hello">
        <h1>С возвращением!</h1>
        <p>Войди в систему, чтобы продолжить</p>
      </div>
      <div class="logo">
        <img src="/public/assets/icon/logo.svg" atl="Логотип"></img>
      </div>
      <form @submit.prevent="handleSubmit">
        <NInput placeholder="Логин" v-model:value="formData.username"></NInput>
        <NInput placeholder="Пароль" v-model:value="formData.password" type="password"></NInput>
        <button>Забыли свой пароль?</button>
      </form>
      <NButton type="primary" @click="handleSubmit">Войти</NButton>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { NInput } from 'naive-ui';
import { NButton } from 'naive-ui';
import IconBtn from '@/components/ui/icon-btn.vue';
import { useDataStore } from '@/stores/counter';
import router from '@/router';

const store = useDataStore();

const formData = ref({
  username: '',
  password: ''
})

const handleSubmit = async () => {
  try {
    const formDataToSend = new FormData();
    formDataToSend.append('username', formData.value.username);
    formDataToSend.append('password', formData.value.password);

    await store.PostLoginUser(formDataToSend);
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
  background-color: #F7742A;
  display: flex;
  flex-direction: column;

}

form {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

form button {
  border: none;
  background-color: transparent;
  color: #CACACA;
  display: flex;
  justify-content: flex-end;
}

.header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 31px 24px;
}

.header h2 {
  color: white;
  margin: 0;
}

.header button {
  margin: 0;
  padding: 0;

}



.login {
  background-color: white;
  border-radius: 20px 20px 0 0;

  padding: 24px;
  border: none;

  display: flex;
  flex-direction: column;
  gap: 65px;
  padding-bottom: 20%;
  flex: 1;
}

h1 {
  padding: 0;
  margin: 0;
}

.hello {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

p {
  padding: 0;
  margin: 0;
}

.logo {
  display: flex;
  justify-content: center;
}
</style>
