<template>
  <div class="section-container">
    <div class="filter-panel" style="margin-bottom: 20px;">
      <n-space justify="space-between">
        <n-input
          v-model:value="searchQuery"
          placeholder="Поиск по ФИО, телефону или ID..."
          clearable
          style="width: 400px"
        />
        <n-button type="info" ghost @click="store.FetchAdminReservations()">
          Обновить данные
        </n-button>
      </n-space>
    </div>

    <n-data-table
      :loading="loading"
      :columns="columns"
      :data="filteredReservations"
      :row-props="rowProps"
      :pagination="{ pageSize: 10 }"
    />

    <n-modal
      v-model:show="showModal"
  preset="card"
  style="width: 800px"
  :title="`Детали бронирования #${selectedItem.reservation_id}`"
>
  <n-spin :show="detailLoading">
    <div class="booking-details">
      <n-grid :cols="2" :x-gap="40" :y-gap="20">

        <n-form-item-gi span="2" label="Экскурсия">
          <div class="text-value header-value">{{ selectedItem.excursion_title }}</div>
        </n-form-item-gi>

        <n-form-item-gi label="ФИО Клиента">
          <div class="text-value">{{ selectedItem.full_name }}</div>
        </n-form-item-gi>

        <n-form-item-gi label="Номер телефона">
          <div class="text-value">{{ selectedItem.phone_number }}</div>
        </n-form-item-gi>

        <n-form-item-gi label="Email">
          <div class="text-value">{{ selectedItem.email || '—' }}</div>
        </n-form-item-gi>

        <n-form-item-gi label="Участников">
          <div class="text-value">{{ selectedItem.participants_count }} чел.</div>
        </n-form-item-gi>

        <n-form-item-gi label="Начало сессии">
          <div class="text-value">{{ selectedItem.session_start_datetime }}</div>
        </n-form-item-gi>

        <n-form-item-gi label="Место встречи">
          <div class="text-value">{{ selectedItem.place }}</div>
        </n-form-item-gi>

        <n-form-item-gi label="Стоимость">
          <div class="text-value price-value">{{ selectedItem.total_cost }} ₽</div>
        </n-form-item-gi>

        <n-form-item-gi label="Техническая инфо">
          <div class="text-value tech-info">
            User ID: {{ selectedItem.user_id }} | Session: {{ selectedItem.session_id }}
          </div>
        </n-form-item-gi>

        <n-form-item-gi span="2" label="Статусы">
          <n-space size="large">
            <n-tag :type="selectedItem.is_paid ? 'success' : 'error'" round size="large">
              {{ selectedItem.is_paid ? 'Оплачено' : 'Ожидает оплаты' }}
            </n-tag>
            <n-tag v-if="selectedItem.is_cancelled" type="error" ghost size="large">
              Бронирование отменено
            </n-tag>
            <n-tag type="info" size="large" variant="outline">
              Статус: {{ selectedItem.payment_status }}
            </n-tag>
              </n-space>
            </n-form-item-gi>

          </n-grid>
        </div>
      </n-spin>

      <template #footer>
        <n-space justify="end">
          <n-button type="error" ghost @click="confirmDelete">Удалить бронирование</n-button>
          <n-button @click="showModal = false">Закрыть</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, h } from 'vue';
import { useDataStore } from '@/stores/counter';
import {
  NDataTable, NModal, NFormItemGi, NGrid, NInput, NButton, NSpace, NTag, useMessage, useDialog
} from 'naive-ui';

const store = useDataStore();
const message = useMessage();
const dialog = useDialog();
const loading = ref(false);

const showModal = ref(false);
const searchQuery = ref('');

// Объект один в один как в новостях
const selectedItem = ref({
  reservation_id: null,
  full_name: '',
  phone_number: '',
  email: '',
  excursion_title: '',
  participants_count: 0,
  total_cost: 0,
  is_paid: false,
  is_cancelled: false,
  booked_at: null,
  place: ''
});

const detailLoading = ref(false);

const rowProps = (row) => ({
  style: 'cursor: pointer',
  onClick: async () => {
    await openDetails(row.reservation_id);
  }
});

async function openDetails(id) {
  try {
    detailLoading.value = true;

    // 1. Делаем запрос. Стор должен возвращать res.data,
    // где лежит { reservation: {...} }
    const response = await store.FetchAdminReservationDetails(id);

    // ПРОВЕРКА: Если сервер вернул структуру как в твоем примере
    const data = response?.reservation;

    if (!data) {
      throw new Error("Данные бронирования не найдены в ответе сервера");
    }

    // 2. Безопасное форматирование дат
    // Используем опциональную цепочку ?. чтобы не упасть, если поля пустые
    const formattedData = { ...data };

    if (formattedData.booked_at) {
      formattedData.booked_at = formattedData.booked_at.replace('T', ' ').substring(0, 19);
    }
    if (formattedData.session_start_datetime) {
      formattedData.session_start_datetime = formattedData.session_start_datetime.replace('T', ' ').substring(0, 16);
    }

    // 3. Сначала записываем данные, потом открываем модалку
    selectedItem.value = formattedData;
    showModal.value = true;
  } catch (e) {
    console.error('Ошибка в openDetails:', e);
    message.error('Не удалось загрузить детали бронирования');
  } finally {
    detailLoading.value = false;
  }
}

// --- КОЛОНКИ ТАБЛИЦЫ ---
const columns = [
  { title: 'ID', key: 'reservation_id', width: 60 },
  { title: 'Клиент', key: 'full_name' },
  { title: 'Телефон', key: 'phone_number' },
  { title: 'Экскурсия', key: 'excursion_title', ellipsis: { tooltip: true } },
  {
    title: 'Статус',
    key: 'is_paid',
    render: (row) => h(NTag, {
      type: row.is_paid ? 'success' : 'error',
      size: 'small'
    }, { default: () => row.is_paid ? 'Оплачено' : 'Нет' })
  }
];

// --- ФИЛЬТРАЦИЯ ---
const filteredReservations = computed(() => {
  // Достаем массив ИЗ объекта.
  // Используем опциональную цепочку ?. чтобы не упасть, если данных еще нет
  const data = store.adminReservations?.reservations || [];

  if (!searchQuery.value) return data;

  const s = searchQuery.value.toLowerCase();
  return data.filter(r =>
    r.full_name?.toLowerCase().includes(s) ||
    r.reservation_id?.toString().includes(s)
  );
});

// --- УДАЛЕНИЕ (КОПИЯ НОВОСТЕЙ) ---
function confirmDelete() {
  dialog.warning({
    title: 'Удаление бронирования',
    content: `Вы уверены, что хотите удалить бронь #${selectedItem.value.reservation_id}?`,
    positiveText: 'Удалить',
    negativeText: 'Отмена',
    onPositiveClick: async () => {
      try {
        loading.value = true;
        await store.DeleteAdminReservation(selectedItem.value.reservation_id);
        message.success('Успешно удалено');
        showModal.value = false;
        await store.FetchAdminReservations();
      } catch (e) {
        message.error('Ошибка при удалении', e);
      } finally {
        loading.value = false;
      }
    }
  });
}

onMounted(() => store.FetchAdminReservations());
</script>

<style scoped>
/* Стили для текстового вывода данных */
.text-value {
  font-size: 16px;
  color: #333;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f2; /* Легкое подчеркивание для структуры */
  min-height: 24px;
}

.header-value {
  font-weight: 600;
  font-size: 18px;
  color: #18a058; /* Цвет Naive UI Success (зеленый) */
  border-bottom: none;
}

.price-value {
  font-weight: bold;
  color: #d03050; /* Цвет акцента на цене */
}

/* Настройка заголовков n-form-item */
:deep(.n-form-item-label) {
  font-weight: 500;
  color: #888 !important;
  text-transform: uppercase;
  font-size: 12px;
  letter-spacing: 0.5px;
}
</style>
