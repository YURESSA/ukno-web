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
      <DefaultButton @click="openEvents" class="profie__btn" text="Управление событиями"/>
      <div class="bottom-btn">
        <DefaultButton @click="logOut" class="profie__btn exit--btn" text="Выйти"/>
        <BaseButton @click="pushToCreateEvent" class="exit--btn" text="Создать событие" />
      </div>
    </div>
  </div>
  <ChangePassword @close="closeChange" :role="profileData.role" v-if="openPasswordModal"/>
  <EventsModal @close="closeEvents" v-if="openEventsModal"/>
</template>

<script setup>
import Header from '@/components/shared/header.vue';
import ChangePassword from '../_shared/changePassword.vue';
import EventsModal from '../_shared/EventsModal.vue';
import Username from '../_shared/username.vue';
import Userdata from '../_shared/userdata.vue';
import DefaultButton from '@/components/UI/button/DefaultButton.vue';
import BaseButton from '@/components/UI/button/BaseButton.vue';
import { onMounted, computed, ref } from 'vue';
import { useDataStore } from '@/stores/counter';
import router from '@/router';

const store = useDataStore();
const profileData = computed(() => store.profileData);
const openPasswordModal = ref(false);
const openEventsModal = ref(false);

function openChange(){
  document.body.style.overflowY = 'hidden'
  openPasswordModal.value = true;
}

function closeChange(){
  document.body.style.overflowY = 'auto'
  openPasswordModal.value = false;
}

function openEvents(){
  document.body.style.overflowY = 'hidden'
  openEventsModal.value = true;
}

function closeEvents(){
  document.body.style.overflowY = 'auto'
  openEventsModal.value = false;
}

onMounted(async () => {
  try {
    await store.GetResidentProfile();
  } catch (error) {
    console.error('Ошибка при загрузке:', error);
  }
});

function pushToCreateEvent(){
  router.push('/newEvent')
}

async function logOut(){
  await store.clearTokenRole();
  router.push('/login');
}
</script>

<style scoped>
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

.bottom-btn{
  display: flex;
  width: 100%;
  justify-content: space-between;
  gap: 20px;
}

.exit--btn{
  width: 50%;
  border-radius: 30px;
}
</style>
