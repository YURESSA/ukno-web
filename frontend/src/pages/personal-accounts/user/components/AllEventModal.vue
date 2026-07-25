<template>
  <div class="modal" @click.stop>
    <div class="header-modal">
      <h4>История записей</h4>
      <IconButton @click="$emit('close')" class="close_btn">
        <img src="/icon/maki_cross.svg" alt="Закрыть">
      </IconButton>
    </div>
    <div class="modal-content">
      <div v-if="events.reservations && events.reservations.length > 0" class="reservations-list">
        <!-- Активные записи -->
        <div v-if="activeReservations.length > 0" class="reservation-group">
          <h4 class="group-title active-title">Активные записи ({{ activeReservations.length }})</h4>
          <div v-for="reservation in activeReservations" :key="reservation.reservation_id" class="reservation-item">
            <div class="reservation-info">
              <div class="reservation-header">
                <h4>{{ reservation.excursion_title }}</h4>
                <span :class="['status-badge', 'status-active']">
                  Активна
                </span>
              </div>

              <div class="reservation-details">
                <p><strong>Дата и время:</strong> {{ formatDateTime(reservation.session_start_datetime) }}</p>
                <p><strong>Место:</strong> {{ reservation.place }}</p>
                <p><strong>Количество участников:</strong> {{ reservation.participants_count }}</p>
                <p><strong>Забронировано:</strong> {{ formatDateTime(reservation.booked_at) }}</p>
                <p><strong>Стоимость:</strong> {{ formatCost(reservation.total_cost) }}</p>
                <p><strong>Статус оплаты:</strong> {{ getPaymentStatusText(reservation.payment_status) }}</p>
              </div>
            </div>

            <div class="reservation-actions">
              <button
                @click="cancelReservation(reservation)"
                class="cancel-btn"
              >
                Отменить бронь
              </button>
            </div>
          </div>
        </div>

        <!-- Отмененные записи (скрываемая секция) -->
        <div v-if="cancelledReservations.length > 0" class="reservation-group collapsible">
          <div class="group-header other-status" @click="toggleCancelled">
            <h3 class="group-title">
              Отмененные записи ({{ cancelledReservations.length }})
              <span class="collapse-icon" :class="{ 'collapsed': !showCancelled }">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M7.41 8.59L12 13.17L16.59 8.59L18 10L12 16L6 10L7.41 8.59Z" fill="currentColor"/>
                </svg>
              </span>
            </h3>
          </div>
          <div v-show="showCancelled" class="group-content">
            <div v-for="reservation in cancelledReservations" :key="reservation.reservation_id" class="reservation-item">
              <div class="reservation-info">
                <div class="reservation-header">
                  <h4>{{ reservation.excursion_title }}</h4>
                  <span :class="['status-badge', 'status-cancelled']">
                    Отменена
                  </span>
                </div>

                <div class="reservation-details">
                  <p><strong>Дата и время:</strong> {{ formatDateTime(reservation.session_start_datetime) }}</p>
                  <p><strong>Место:</strong> {{ reservation.place }}</p>
                  <p><strong>Количество участников:</strong> {{ reservation.participants_count }}</p>
                  <p><strong>Забронировано:</strong> {{ formatDateTime(reservation.booked_at) }}</p>
                  <p><strong>Отменена:</strong> {{ formatDateTime(reservation.booked_at) }}</p>
                  <p><strong>Стоимость:</strong> {{ formatCost(reservation.total_cost) }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Прошедшие записи (скрываемая секция) -->
        <div v-if="pastReservations.length > 0" class="reservation-group collapsible">
          <div class="group-header other-status" @click="togglePast">
            <h3 class="group-title">
              Прошедшие записи ({{ pastReservations.length }})
              <span class="collapse-icon" :class="{ 'collapsed': !showPast }">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M7.41 8.59L12 13.17L16.59 8.59L18 10L12 16L6 10L7.41 8.59Z" fill="currentColor"/>
                </svg>
              </span>
            </h3>
          </div>
          <div v-show="showPast" class="group-content">
            <div v-for="reservation in pastReservations" :key="reservation.reservation_id" class="reservation-item">
              <div class="reservation-info">
                <div class="reservation-header">
                  <h4>{{ reservation.excursion_title }}</h4>
                  <span :class="['status-badge', 'status-past']">
                    Завершена
                  </span>
                </div>

                <div class="reservation-details">
                  <p><strong>Дата и время:</strong> {{ formatDateTime(reservation.session_start_datetime) }}</p>
                  <p><strong>Место:</strong> {{ reservation.place }}</p>
                  <p><strong>Количество участников:</strong> {{ reservation.participants_count }}</p>
                  <p><strong>Забронировано:</strong> {{ formatDateTime(reservation.booked_at) }}</p>
                  <p><strong>Стоимость:</strong> {{ formatCost(reservation.total_cost) }}</p>
                  <p><strong>Статус оплаты:</strong> {{ getPaymentStatusText(reservation.payment_status) }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="empty-state">
        <p>У вас пока нет записей на экскурсии.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import IconButton from '@/components/ui/button/IconButton.vue'
import { useDataStore } from '@/stores/counter'
import { notification } from '@/utils/notification'


const store = useDataStore();
const props = defineProps({
  events: Object,
})

const emit = defineEmits(['close', 'cancelReservation'])

// Состояния для скрытия/показа секций
const showCancelled = ref(false)
const showPast = ref(false)
const localReservations = ref([])

// Определяем, прошло ли событие
const isEventPast = (reservation) => {
  const eventDate = new Date(reservation.session_start_datetime)
  const now = new Date()
  return eventDate < now
}

// Копируем данные из props при их изменении
watch(() => props.events.reservations, (newVal) => {
  localReservations.value = newVal ? [...newVal] : []
}, { immediate: true })

// Замените все computed свойства, чтобы они использовали localReservations вместо props.events.reservations
const activeReservations = computed(() => {
  if (!localReservations.value || localReservations.value.length === 0) return []

  return localReservations.value
    .filter(reservation => !reservation.is_cancelled && !isEventPast(reservation))
    .sort((a, b) => {
      const dateA = new Date(a.session_start_datetime)
      const dateB = new Date(b.session_start_datetime)
      return dateA - dateB
    })
})

const cancelledReservations = computed(() => {
  if (!localReservations.value || localReservations.value.length === 0) return []

  return localReservations.value
    .filter(reservation => reservation.is_cancelled)
    .sort((a, b) => {
      const dateA = new Date(a.booked_at)
      const dateB = new Date(b.booked_at)
      return dateB - dateA
    })
})

const pastReservations = computed(() => {
  if (!localReservations.value || localReservations.value.length === 0) return []

  return localReservations.value
    .filter(reservation => !reservation.is_cancelled && isEventPast(reservation))
    .sort((a, b) => {
      const dateA = new Date(a.session_start_datetime)
      const dateB = new Date(b.session_start_datetime)
      return dateB - dateA
    })
})

// Форматирование даты и времени
const formatDateTime = (dateTimeString) => {
  const date = new Date(dateTimeString)
  return date.toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Форматирование стоимости
const formatCost = (cost) => {
  if (cost === 0 || cost === '0') return 'Бесплатно'
  return `${cost} ₽`
}

// Текст статуса оплаты
const getPaymentStatusText = (paymentStatus) => {
  const statusMap = {
    'succeeded': 'Оплачено',
    'unpaid': 'Не оплачено',
    'pending': 'Ожидает оплаты',
    'refunded': 'Возвращено'
  }
  return statusMap[paymentStatus] || paymentStatus
}

// Обработка отмены брони
const cancelReservation = async (reservation) => {
  if (!confirm('Вы уверены, что хотите отменить бронирование?')) {
    return
  }

  const delet_id = { reservation_id: reservation.reservation_id }

  try {
    // Отправляем запрос на сервер
    await store.DeleteReservation(delet_id)

    // Вручную обновляем данные на фронте
    const index = localReservations.value.findIndex(
      r => r.reservation_id === reservation.reservation_id
    )

    if (index !== -1) {
      // Создаем копию записи с обновленными данными
      const updatedReservation = {
        ...localReservations.value[index],
        is_cancelled: true,
        // Добавляем timestamp отмены, если нужно
        cancelled_at: new Date().toISOString()
      }

      // Обновляем запись в массиве
      localReservations.value[index] = updatedReservation

      // Создаем новый массив для реактивности
      localReservations.value = [...localReservations.value]

      await notification('Бронь успешно отменена, на почту отправленно сообщение с информацией по возврату', 'positive');

      // Автоматически раскрываем секцию отмененных записей
      if (!showCancelled.value && cancelledReservations.value.length > 0) {
        showCancelled.value = true
      }
    }
  } catch (error) {
    console.error('Ошибка при отмене бронирования:', error)
    await notification('Произошла ошибка при отмене бронирования. Попробуйте еще раз.', 'negative');
  }
}

// Переключение отображения секций
const toggleCancelled = () => {
  showCancelled.value = !showCancelled.value
}

const togglePast = () => {
  showPast.value = !showPast.value
}
</script>

<style scoped>
.modal{
  position: absolute;
  width: 800px;
  background-color: #FFFFFF;
  box-shadow: 0px 4px 12.7px 0px #00000040;
  border-radius: 14px;
  padding: 40px 40px 45px 40px;
  top: 50%;
  left: 50%;
  transform: translateY(-50%) translateX(-50%);
  z-index: 1000;
}

.close_btn{
  width: 23px;
  height: 23px;
  padding: 4px;
  border-radius: 5px;
  border: none;
  background-color: #EDEDED8A;
}

.header-modal{
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-content {
  max-height: 70vh;
  overflow-y: auto;
  padding: 20px;
}

.reservations-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.reservation-group {
  display: flex;
  flex-direction: column;
}

/* Стили для активных записей (всегда открыты) */
.reservation-group:not(.collapsible) {
  gap: 16px;
}

/* Стили для скрываемых секций */
.reservation-group.collapsible {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.reservation-group.collapsible .group-header {
  padding: 16px;
  background-color: #f9f9f9;
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.reservation-group.collapsible .group-header:hover {
  background-color: #f0f0f0;
}

.reservation-group.collapsible .group-title {
  margin: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.collapse-icon {
  transition: transform 0.3s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #666;
}

.collapse-icon.collapsed {
  transform: rotate(-90deg);
}

.reservation-group.collapsible .group-content {
  padding: 16px;
  background-color: #fff;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Стили заголовков групп */
.active-title {
  color: #F25C03;
}

.other-status {
  border-left: 4px solid #f44336;
}

/* Общие стили для записей */
.reservation-item {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  background-color: #fff;
  transition: border-color 0.2s;
}

.reservation-item:hover {
  border-color: #bdbdbd;
}

.reservation-info {
  flex: 1;
}

.reservation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.reservation-header h4 {
  margin: 0;
  font-size: 16px;
  color: #333;
  font-weight: 600;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-active {
  background-color: #e8f5e9;
  color: #2e7d32;
  border: 1px solid #c8e6c9;
}

.status-cancelled {
  background-color: #ffebee;
  color: #c62828;
  border: 1px solid #ffcdd2;
}

.status-past {
  background-color: #f5f5f5;
  color: #616161;
  border: 1px solid #e0e0e0;
}

.reservation-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.reservation-details p {
  margin: 0;
  font-size: 14px;
  color: #666;
  line-height: 1.4;
}

.reservation-details strong {
  color: #333;
  font-weight: 500;
  min-width: 140px;
  display: inline-block;
}

.reservation-actions {
  margin-left: 20px;
  display: flex;
  align-items: flex-start;
}

.cancel-btn {
  padding: 8px 20px;
  background-color: #ffebee;
  color: #c62828;
  border: 1px solid #ffcdd2;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
  white-space: nowrap;
}

.cancel-btn:hover {
  background-color: #ffcdd2;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.cancel-btn:active {
  transform: translateY(0);
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #757575;
  font-size: 16px;
}

@media (max-width: 768px) {
  .reservation-item {
    flex-direction: column;
    gap: 16px;
  }

  .reservation-actions {
    margin-left: 0;
    width: 100%;
  }

  .cancel-btn {
    width: 100%;
  }

  .reservation-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .reservation-details {
    grid-template-columns: 1fr;
  }

  .reservation-details strong {
    min-width: 120px;
  }

  .group-title {
    font-size: 15px;
  }
}

@media (max-width: 480px) {
  .reservation-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .status-badge {
    align-self: flex-start;
  }

  .reservation-header h4 {
    font-size: 15px;
  }

  .group-title {
    font-size: 14px;
  }

  .collapse-icon {
    margin-left: 8px;
  }
}
</style>
