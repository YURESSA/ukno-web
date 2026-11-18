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
        <n-space>
          <n-button type="info" ghost @click="store.FetchAdminReservations()">
            Обновить данные
          </n-button>
          <n-button type="primary" @click="showExportModal = true">
            Выгрузка в Excel
          </n-button>
        </n-space>
      </n-space>
    </div>

    <n-data-table
      :loading="loading"
      :columns="columns"
      :data="filteredReservations"
      :row-key="row => row.reservation_id"
      :row-props="rowProps"
      :pagination="{ pageSize: 10 }"
    />

    <n-modal
      v-model:show="showExportModal"
      preset="card"
      title="Выгрузка броней в Excel"
      style="width: min(480px, calc(100vw - 32px))"
      :closable="!exporting"
      :mask-closable="!exporting"
      :close-on-esc="!exporting"
    >
      <n-form label-placement="top" :disabled="exporting">
        <n-form-item label="Фильтровать по">
          <n-select v-model:value="exportDateType" :options="exportDateOptions" />
        </n-form-item>
        <n-form-item label="Период">
          <n-date-picker
            v-model:formatted-value="exportDateRange"
            type="daterange"
            format="dd.MM.yyyy"
            value-format="yyyy-MM-dd"
            start-placeholder="Начало периода"
            end-placeholder="Конец периода"
            clearable
            style="width: 100%"
          />
        </n-form-item>
      </n-form>
      <p>Без выбранного периода в файл попадут все брони.</p>
      <template #footer>
        <n-space justify="end">
          <n-button :disabled="exporting" @click="showExportModal = false">Отмена</n-button>
          <n-button type="primary" :loading="exporting" @click="downloadReservations">
            Скачать Excel
          </n-button>
        </n-space>
      </template>
    </n-modal>

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
import { getApiErrorMessage } from '@/utils/apiError'
import { ref, computed, onMounted, h } from 'vue';
import { useDataStore } from '@/stores/counter';
import {
  NDataTable, NModal, NForm, NFormItem, NFormItemGi, NGrid, NInput, NSelect, NDatePicker,
  NButton, NSpace, NTag, NSpin, useMessage, useDialog
} from 'naive-ui';

const store = useDataStore();
const message = useMessage();
const dialog = useDialog();
const loading = ref(false);
const exporting = ref(false);
const showExportModal = ref(false);
const exportDateType = ref('booked');
const exportDateRange = ref(null);
const exportDateOptions = [
  { label: 'Дата создания брони', value: 'booked' },
  { label: 'Дата сеанса', value: 'date' },
];

const showModal = ref(false);
const searchQuery = ref('');

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

    const response = await store.FetchAdminReservationDetails(id);

    const data = response?.reservation;

    if (!data) {
      throw new Error("Данные бронирования не найдены в ответе сервера");
    }

    const formattedData = { ...data };

    if (formattedData.booked_at) {
      formattedData.booked_at = formattedData.booked_at.replace('T', ' ').substring(0, 19);
    }
    if (formattedData.session_start_datetime) {
      formattedData.session_start_datetime = formattedData.session_start_datetime.replace('T', ' ').substring(0, 16);
    }

    selectedItem.value = formattedData;
    showModal.value = true;
  } catch (e) {
    console.error('Ошибка в openDetails:', e);
    message.error(getApiErrorMessage(e, 'Не удалось загрузить детали бронирования'));
  } finally {
    detailLoading.value = false;
  }
}

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

const sortedReservations = computed(() => [...(store.adminReservations?.reservations || [])].sort((a, b) =>
  (b.booked_at || '').localeCompare(a.booked_at || '') ||
  b.reservation_id - a.reservation_id
));

const filteredReservations = computed(() => {
  if (!searchQuery.value) return sortedReservations.value;
  const s = searchQuery.value.toLowerCase();
  return sortedReservations.value.filter(r =>
    r.full_name?.toLowerCase().includes(s) ||
    r.reservation_id?.toString().includes(s)
  );
});

async function downloadReservations() {
  if (exporting.value) return;
  exporting.value = true;
  try {
    const params = {};
    if (exportDateRange.value) {
      const [from, to] = exportDateRange.value;
      params[`${exportDateType.value}_from`] = from;
      params[`${exportDateType.value}_to`] = to;
    }
    const file = await store.ExportAdminReservations(params);
    const url = URL.createObjectURL(file);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'reservations.xlsx';
    document.body.append(link);
    link.click();
    link.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
    showExportModal.value = false;
  } catch (error) {
    const feedback = getApiErrorMessage(error, 'Не удалось скачать брони в Excel');
    if (feedback) message.error(feedback);
  } finally {
    exporting.value = false;
  }
}

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
        message.error(getApiErrorMessage(e, 'Ошибка при удалении'));
      } finally {
        loading.value = false;
      }
    }
  });
}

onMounted(() => store.FetchAdminReservations().catch(e => message.error(getApiErrorMessage(e, 'Ошибка загрузки данных'))));
</script>

<style scoped>
.text-value {
  font-size: 16px;
  color: #333;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f2;
  min-height: 24px;
}

.header-value {
  font-weight: 600;
  font-size: 18px;
  color: #18a058;
  border-bottom: none;
}

.price-value {
  font-weight: bold;
  color: #d03050;
}

:deep(.n-form-item-label) {
  font-weight: 500;
  color: #888 !important;
  text-transform: uppercase;
  font-size: 12px;
  letter-spacing: 0.5px;
}
</style>
