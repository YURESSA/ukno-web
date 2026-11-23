<template>
  <Header/>
  <div class="page-wrapper page--margin">
    <Username :full_name="profileData.full_name" :role="profileData.role"/>
    <div class="user-data-wrapper">
      <Userdata
        :email="profileData.email"
        :phone="profileData.phone"
        @open="isChangeOpen = true"
      />
      <NearestEvents :reservationsData="reservationsData"/>
      <DefaultButton class="profie__btn" text="История записей" @click="isAllEventOpen = true"/>
      <DefaultButton @click="logOut" class="profie__btn" text="Выйти"/>
    </div>
  </div>
  <ChangePassword v-if="isChangeOpen" @close="isChangeOpen = false"/>
  <AllEventModal
    v-if="isAllEventOpen"
    :reservations="reservationsData.reservations"
    @close="isAllEventOpen = false"
  />
</template>

<script setup>
import Header from '@/components/shared/header.vue';
import Username from '../_shared/username.vue';
import Userdata from '../_shared/userdata.vue';
import NearestEvents from './components/nearestEvents.vue';
import DefaultButton from '@/components/ui/button/DefaultButton.vue';
import { onMounted, computed, ref } from 'vue';
import { useDataStore } from '@/stores/counter';
import router from '@/router';
import ChangePassword from '../_shared/changePassword.vue';
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
  width: 660px;
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
    order: 2;
  }
}

</style>
