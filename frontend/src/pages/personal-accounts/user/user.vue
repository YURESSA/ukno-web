<template>
  <Header/>
  <div class="page-wrapper page--margin">
    <Username :full_name="profileData.full_name" :role="profileData.role"/>
    <div class="user-data-wrapper">
      <Userdata
        :email="profileData.email"
        :phone="profileData.phone"
        @open="openChange"
      />
      <NearestEvents :reservationsData="reservationsData"/>
      <DefaultButton class="profie__btn" text="История записей" @click="openAllEvents"/>
      <DefaultButton @click="logOut" class="profie__btn" text="Выйти"/>
    </div>
  </div>
  <ChangePassword @close="closeChange" :role="profileData.role" v-if="isChangeOpen && !$isMobile()"/>
  <AllEventModal @close="closeAllEvents" :events="reservationsData" v-if="isAllEventOpen && !$isMobile()"/>
  <DropMenu
    :class="{ 'drop-open': isChangeOpen }"
    @close="closeAll"
    v-if="$isMobile()">
        <form @submit.prevent="handleSubmit" autocomplete="off">
      <div class="header-form">
        <h4>Сменить пароль</h4>
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
        <BaseButton class="sbm-button" text="Сохранить" />
        <DefaultButton class="reset-button" text="Сбросить" @click="resetForm" type="button" />
      </div>
    </form>
  </DropMenu>
    <div
    class="modal-open-wrapper"
    v-if="isChangeOpen || isAllEventOpen"
    @click="closeAll"
  ></div>
</template>

<script setup>
import Header from '@/components/shared/header.vue';
import Username from '../_shared/username.vue';
import Userdata from '../_shared/userdata.vue';
import NearestEvents from './components/nearestEvents.vue';
import DefaultButton from '@/components/ui/button/DefaultButton.vue';
import DropMenu from '@/components/shared/dropMenu.vue';
import { onMounted, computed, ref } from 'vue';
import { useDataStore } from '@/stores/counter';
import router from '@/router';
import ChangePassword from '../_shared/changePassword.vue';
import BaseButton from '@/components/ui/button/BaseButton.vue';
import AllEventModal from './components/AllEventModal.vue';

const store = useDataStore();
const profileData = computed(() => store.profileData);
const reservationsData = computed(() => store.reservationsData);
const isChangeOpen = ref(false);
const isAllEventOpen = ref(false);

onMounted(async () => {
  try {
    await store.GetProfile();
    await store.GetUserReservations();
  } catch (error) {
    console.error('Ошибка при загрузке:', error);
  }
});

async function logOut(){
  await store.clearTokenRole();
  router.push('/');
}

function openChange(){
  document.body.classList.add('body-no-scroll');
  isChangeOpen.value = true;
}

function closeChange(){
  document.body.classList.remove('body-no-scroll');
  isChangeOpen.value = false;
}

function openAllEvents(){
  document.body.classList.add('body-no-scroll');
  isAllEventOpen.value = true;
}

function closeAllEvents(){
  document.body.classList.remove('body-no-scroll');
  isAllEventOpen.value = false;
}

function closeAll(){
  document.body.classList.remove('body-no-scroll');
  isChangeOpen.value = false;
  isAllEventOpen.value = false;
}

const passwordConfirmation = ref('');
const showErrors = ref(true);


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
    await notification('Пароль успешно изменён!', 'positive');

  } catch (error) {
    if (error.response?.status === 400) {
      await notification('Неверный старый пароль', 'negative');
    } else {
      await notification('Произошла ошибка при смене пароля', 'negative');
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
.modal-open-wrapper{
  display: block;
  content: '';
  width: 100%;
  height: 100vh;
  position: fixed;
  top: 0;
  overflow: hidden;
  background-color: rgba(128, 128, 128, 0.459);
  z-index: 999;
}


.page-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  position: relative;
  min-height: calc(100vh - 100px);
  max-width: max-content;
  margin: 0 auto;
}

.user-data-wrapper{
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  max-height: max-content;
  padding: 60px 80px;
  min-width: 660px;
  max-width: 740px;
  gap: 20px;

  border-radius: 26px;
  box-shadow: 0px 0px 12.7px 0px #0000002E;
}

.profie__btn{
  height: 62px;
  padding: 20px 0;
  font-size: 20px;
  width: 100%;
  border-radius: 30px;
  border: 1px solid #33333329
}

@media (max-width: 768px) {
  .page-wrapper {
    width: calc(100vw - 48px);
  }
  .user-data-wrapper{
    padding: 25px 24px;
    min-width: calc(100vw - 48px);
    max-width: calc(100vw - 48px);
    box-shadow: none;
  }
  .profie__btn{
    border: none;
    font-size: 16px;
    background-color: #F5F5F5;
  }
  .bottom-btn{
    display: flex;
    flex-direction: column;
  }
  .exit--btn{
    font-size: 16px;
    width: 100%;
  }
  .profie__btn.exit--btn {
    order: 2; /* Переместить вниз */
  }
}

.drop-open{
  bottom: 0;
  opacity: 1;
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

.sbm-button{
  padding: 5px 25px;
  width: 50%;
}

.reset-button{
  width: 50%;
  height: 45;
  border-radius: 15px;
  padding: 5px 25px;
  color: #000000;
  font-weight: 400;
  font-size: 20px;
}

.button-wrapper{
  display: flex;
  gap: 15px;
}
</style>
