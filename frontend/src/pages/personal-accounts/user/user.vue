<template>
  <Header/>
  <div class="page-wrapper">
    <Username/>
    <div class="user-data-wrapper">
      <Userdata/>
      <NearestEvents/>
      <DefaultButton class="profie__btn" text="История записей"/>
      <DefaultButton class="profie__btn" text="Выйти"/>
    </div>
  </div>
</template>

<script setup>
import Header from '@/components/shared/header.vue';
import Username from '../_shared/username.vue';
import Userdata from '../_shared/userdata.vue';
import NearestEvents from './components/nearestEvents.vue';
import DefaultButton from '@/components/UI/button/DefaultButton.vue';
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
</style>
