<template>
  <div class="nearest-events">
    <h5>Ближайшие события</h5>
    <div class="events" v-if="filteredReservations.length !== 0">
      <n-carousel
        effect="fade"
        direction="vertical"
        slides-per-view="auto"
        :space-between="20"
        :centered-slides="true"
        :show-arrow="true"
        dot-placement="right"
        draggable
        style="height: 400px; padding: 0 20px;"
      >
        <n-carousel-item
          v-for="reservation in filteredReservations"
          :key="reservation.reservation_id"
        >
          <div class="card-wrapper">
            <h5>{{ reservation.excursion_title }}</h5>
            <!-- <p>{{ getExcursionDescription(reservation.excursion_id) }}</p> -->
            <p>{{ formatDateTime(reservation.start_datetime) }} | Старт у фонтана</p>
            <p>Участников: {{ reservation.participants_count }}</p>
            <div class="price">
              <span>{{ formatPrice(reservation.cost) }} ₽</span>
            </div>
            <BaseButton @click="deletReserv(reservation.reservation_id)" class="delet--btn" text="Отменить бронь"/>
          </div>
        </n-carousel-item>
      </n-carousel>
    </div>
    <p v-if="filteredReservations.length === 0">Нет предстоящих событий</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { NCarousel, NCarouselItem } from 'naive-ui';
import BaseButton from '@/components/UI/button/BaseButton.vue'
import { useDataStore } from '@/stores/counter';

const store = useDataStore();
const props = defineProps({
  reservationsData: Object
})

// Фильтруем бронирования: только будущие и не отмененные
const filteredReservations = computed(() => {
  if (!props.reservationsData?.reservations) return []

  const now = new Date()
  return props.reservationsData.reservations.filter(res =>
    !res.is_cancelled && new Date(res.start_datetime) > now
  ).sort((a, b) => new Date(a.start_datetime) - new Date(b.start_datetime))
})

// Форматируем дату и время
const formatDateTime = (datetime) => {
  const date = new Date(datetime)
  return `${date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' })} | ${date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}`
}

// Форматируем цену
const formatPrice = (price) => {
  return parseFloat(price).toLocaleString('ru-RU')
}


async function deletReserv(id){
  const delet_id = {reservation_id: id}
  try {
    await store.DeletReservation(JSON.stringify(delet_id));
  } catch (error) {
    console.error('Ошибка при удалении:', error);
  }
}
</script>

<style scoped>

.nearest-events {
  width: 70%;
  overflow: visible;
}

/* Стили для карусели */
:deep(.n-carousel) {
  overflow: visible;
}

:deep(.n-carousel__slides) {
  align-items: center;
}

:deep(.n-carousel__arrow-group) {
  bottom: 50%!important;
  transform: translateY(50%);
}

:deep(.n-carousel__dots ) {
  transform: translateY(-50%)!important;
  top: 50%!important;
  left: 18px!important;
  background-color: black!important;
  width: max-content!important;
  height: max-content!important;
}

.card-wrapper{
  display: flex;
  flex-direction: column;
  justify-content: center;
  max-height: max-content;
  gap: 20px;
  padding: 40px;

  width: 300px;
  border-radius: 14px;
  border: 1px solid #DEDEDE;
  margin-bottom: 10px;
}

p{
  margin-bottom: 10px;
}

.price{
  width: 150px;
  text-align: center;
  background-color: #FFD6BD;
  color: #F25C03;
  border-radius: 30px;

  font-size: 16px;
  font-weight: 700;
}

.delet--btn{
  background-color: rgb(219, 51, 51);
}

.delet--btn:hover{
  background-color: rgb(199, 41, 41);
}

</style>
