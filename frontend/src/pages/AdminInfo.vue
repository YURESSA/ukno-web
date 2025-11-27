<template>
  <div class="header">
    <h2>Административная панель</h2>
  </div>
  <div class="content">
    <div class="first-element">
      <h3>Создание читательского билета</h3>
      <NButton type="primary" @click="creatUser">Создать пользователя</NButton>
    </div>
    <div class="text-data">
      <h4>Номер читательского билета:</h4>
      <p>{{ data.ticket_id }}</p>
    </div>
    <div class="text-data">
      <h4>Пароль для входа в аккаунт:</h4>
      <p>{{ data.password }}</p>
    </div>
    <div class="first-element">
      <Table :orders="booked"></Table>
    </div>
    <div class="first-element">
      <CreatBook></CreatBook>
    </div>
  </div>
</template>

<script setup>
import { NInput, NButton } from 'naive-ui';
import { useDataStore } from '@/stores/counter';
import { computed, onMounted, ref } from 'vue';
import Table from '@/components/table.vue';
import CreatBook from '@/components/creatBook.vue';

const store = useDataStore();
const data = ref('')
const booked = computed(() => store.booked)

onMounted(() => {
  store.getAllBooked();
})

async function creatUser() {
  data.value = await store.creatUser()
}
</script>

<style scoped>

.header{
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #ed6840;
  height: 80px;
}

.first-element{
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
}

.content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  margin-top: 20px;
}

.text-data {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-top: 10px;
}

</style>
