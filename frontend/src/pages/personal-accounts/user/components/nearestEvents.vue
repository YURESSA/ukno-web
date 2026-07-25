<template>
  <div class="nearest-events">
    <h5>Ближайшее событие</h5>
    <div class="events" v-if="filteredReservations.length !== 0">
      <div class="card-wrapper">
        <h5>{{ filteredReservations[0].excursion_title }}</h5>
        <!-- <p>{{ getExcursionDescription(reservation.excursion_id) }}</p> -->
        <p>{{ formatDateTime(filteredReservations[0].session_start_datetime) }} | {{ filteredReservations[0].place }}</p>
        <p>Участников: {{ filteredReservations[0].participants_count }}</p>
        <div class="price">
          <span>{{ formatPrice(filteredReservations[0].total_cost) }} ₽</span>
        </div>
        <BaseButton @click="deletReserv(filteredReservations[0].reservation_id)" class="delet--btn" text="Отменить бронь"/>
      </div>
    </div>
    <p v-if="filteredReservations.length === 0">Нет предстоящих событий</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { NCarousel, NCarouselItem } from 'naive-ui';
import BaseButton from '@/components/ui/button/BaseButton.vue'
import { useDataStore } from '@/stores/counter';

const store = useDataStore();
const props = defineProps({
  reservationsData: Object
})

// Фильтруем бронирования: только будущие и не отмененные
const filteredReservations = computed(() => {
  if (!props.reservationsData?.reservations) return []

  const now = new Date()
  const filterReservations = props.reservationsData.reservations.filter(res =>
    !res.is_cancelled && new Date(res.session_start_datetime) > now
  ).sort((a, b) => new Date(a.session_start_datetime) - new Date(b.session_start_datetime))
  return filterReservations
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
    await store.DeleteReservation(delet_id);
  } catch (error) {
    console.error('Ошибка при удалении:', error);
  }
  for (const e of filteredReservations.value) {
      if (e.reservation_id === id) {
          e.is_cancelled = true;
          break;
      }
  }
}
</script>

<style scoped>

.nearest-events {
  width: 100%;
  overflow: visible;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Стили для карусели (не актуально?)*/
/* :deep(.n-carousel) {
  overflow: visible;
}

:deep(.n-carousel__slides) {
  align-items: center;
}

:deep(.n-carousel__arrow-group) {
  bottom: 50%!important;
  transform: translateY(50%);
  right: -80px!important;
}

:deep(.n-carousel__dots ) {
  transform: translateY(-50%)!important;
  top: 50%!important;
  left: 18px!important;
  background-color: none!important;
  width: max-content!important;
  height: max-content!important;
}

:deep(.n-carousel__slide){
  top: 50%;
  left: 50%!important;
  transform: translateY(-50%) translateX(-40%)!important;
}

:deep(.n-carousel__dot){
  background-color: #333333!important;
}


:deep(.n-carousel__dot--active){
  background-color: #F25C03!important;
} */

.card-wrapper{
  display: flex;
  flex-direction: column;
  justify-content: center;
  max-height: max-content;
  gap: 20px;
  padding: 40px;

  width: calc(100% - 80px);
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
