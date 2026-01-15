<template>
  <div class="details">
    <p class="title">Бронирование #{{ reservation?.reservation_id }}</p>

    <div class="grid">
      <div class="row"><span class="k">ФИО:</span><span class="v">{{ reservation?.full_name }}</span></div>
      <div class="row"><span class="k">Телефон:</span><span class="v">{{ reservation?.phone_number }}</span></div>
      <div class="row"><span class="k">Email:</span><span class="v">{{ reservation?.email }}</span></div>
      <div class="row"><span class="k">Количество участников:</span><span class="v">{{ reservation?.participants_count }}</span></div>

      <div class="row"><span class="k">Оплачена:</span><span class="v">{{ yesNo(reservation?.is_paid) }}</span></div>
      <div class="row"><span class="k">Статус оплаты:</span><span class="v">{{ reservation?.payment_status }}</span></div>
      <div class="row"><span class="k">Сумма оплаты:</span><span class="v">{{ reservation?.total_cost }} ₽</span></div>

      <div class="row"><span class="k">Отменена:</span><span class="v">{{ yesNo(reservation?.is_cancelled) }}</span></div>
      <div class="row"><span class="k">Дата бронирования:</span><span class="v">{{ reservation?.booked_at }}</span></div>

      <div class="row"><span class="k">Экскурсия:</span><span class="v">{{ reservation?.excursion_title }}</span></div>
      <div class="row"><span class="k">Место:</span><span class="v">{{ reservation?.place }}</span></div>
    </div>

    <div class="actions">
      <button class="delete" type="button" @click="onDelete">Удалить бронирование</button>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  reservation: { type: Object, default: null }
})
const emit = defineEmits(['delete'])

function yesNo(v) {
  return v ? 'Да' : 'Нет'
}

function onDelete() {
  if (!props.reservation?.reservation_id) return
  emit('delete', props.reservation.reservation_id)
}
</script>

<style scoped>
.title { font-size: 18px; font-weight: 700; margin-bottom: 14px; }
.grid { display: grid; gap: 10px; }
.row { display: grid; grid-template-columns: 220px 1fr; gap: 16px; }
.k { color: #111827; font-weight: 600; }
.v { color: #111827; }
.actions { display: flex; justify-content: flex-end; margin-top: 18px; }
.delete { border: none; background: transparent; color: #ef4444; cursor: pointer; font-weight: 600; }
</style>
