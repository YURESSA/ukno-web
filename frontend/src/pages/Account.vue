<template>
  <div class="page-wrapper">
    <div class="header">
      <h1>Личный кабинет</h1>
    </div>
    <div class="personal-info" v-if="info">
      <h4>Ваш номер читательского билета: {{ info.ticket_id }}</h4>
      <NInput placeholder="email" v-model:value="currentEmail"></NInput>
      <NButton v-if="currentEmail !== originalEmail" type="primary" class="save-btn" @click="saveChanges">Сохранить</NButton>
      <NButton v-if="currentEmail !== originalEmail" type="default" class="cancel-btn" @click="cancelChanges">Отмена</NButton>
    </div>
    <div class="likes">
      <button><h4>Избранное</h4></button>
      <ul>
        <bookCard></bookCard>
      </ul>
    </div>
    <div class="rezerv">
      <h2>Забронированные книги</h2>
        <BookedCard
          v-for="(book, i) in orderList"
          :key="i"
          :book="book"
        ></BookedCard>
    </div>
    <div class="reviews">
      <NButton><p>Отзывы</p></NButton>
    </div>
    <div class="alerts">
      <h2>Уведомления</h2>
      <Alert></Alert>
      <Alert></Alert>
      <Alert></Alert>
    </div>
    <Footer></Footer>
  </div>
</template>

<script setup>
import { NButton, NInput } from 'naive-ui';
import { useDataStore } from '@/stores/counter';
import { computed, onMounted, ref } from 'vue';
import Alert from '@/components/shared/alert.vue';
import Footer from '@/components/shared/footer.vue';
import BookedCard from '@/components/bookedCard.vue';

const store = useDataStore();
const info = computed(() => store.userInfo)
const orderList = computed(() => store.orderListget)

const currentEmail = ref('')
const originalEmail = ref('')

onMounted(async () => {
  await store.GetUserInfo();
  await store.GetOrderList();
  currentEmail.value = info.value.email
  originalEmail.value = info.value.email
})

function cancelChanges() {
  currentEmail.value = originalEmail.value
}

async function saveChanges() {
  const email = currentEmail.value
  try {
    await store.updateUserInfo(email)
    originalEmail.value = currentEmail.value
    console.log('Email сохранен:', currentEmail.value)
  } catch (error) {
    console.error('Ошибка сохранения:', error)
  }
}
</script>

<style scoped>

.rezerv{
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 5px;
  height: 100%;
  width: 100%;
}

.rezerv-btn {
  margin-bottom: 10px;
}

.rezerv button {
  width: 100%;
  display: flex;
  justify-content: flex-start;
  box-shadow: 2px 2px 4px 0px rgba(34, 60, 80, 0.2);
  background-color: #F3F3F3;
}
.reviews button {
  width: 100%;
  display: flex;
  justify-content: flex-start;
  background-color: #F3F3F3;
}
.reviews button p {
  color: black;
}
.page-wrapper {
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding-bottom: 100px;
}

.save-btn {
  margin-top: 10px;
}

.cancel-btn {
  margin-left: 5px;
}

.likes {
  background-color: #F3F3F3;
  display: flex;
  flex-direction: column;
  gap: 7px;
  padding: 10px 5px;
  box-shadow: 2px 2px 4px 0px rgba(34, 60, 80, 0.2);

}
.likes ul {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  gap: 2px;
}
.likes button {
  width: 30%;
  border: none;
}
.header {
  display: flex;
  justify-content: center;
  padding: 0;
  margin: 0;
  gap: 10px;

}
.header img {
  padding-top: 5px;
}
.alerts {
  background-color: #F3F3F3;
  padding: 9px 26px;
  display: flex;
  gap: 10px;
  flex-direction: column;
  border-radius: 5px;
  box-shadow: 2px 2px 4px 0px rgba(34, 60, 80, 0.2);

}
</style>
