<template>
  <n-space vertical :size="12">
    <n-data-table
      ref="table"
      :columns="columns"
      :data="tableData"
      :pagination="pagination"
    />
  </n-space>
</template>

<script setup>
import { ref, computed } from "vue";

// Преобразуем исходные данные в формат для таблицы
const props = defineProps({
  orders: {
    type: Array,
    default: () => []
  }
});

const tableData = computed(() => {
  return props.orders.map(order => ({
    key: order.id,
    user_id: order.user_id,
    title: order.books?.[0]?.title || 'Нет названия',
    created_at: formatDate(order.created_at),
    due_date: formatDate(order.due_date),
    raw_created_at: order.created_at,
    raw_due_date: order.due_date
  }));
});

function formatDate(dateString) {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return date.toLocaleDateString('ru-RU');
}

const columns = [
  {
    title: "ID пользователя",
    key: "user_id",
    sorter: (row1, row2) => row1.user_id - row2.user_id
  },
  {
    title: "Название книги",
    key: "title",
    defaultSortOrder: "ascend",
    sorter: "default"
  },
  {
    title: "Дата создания",
    key: "created_at",
    sorter: (row1, row2) => new Date(row1.raw_created_at) - new Date(row2.raw_created_at)
  },
  {
    title: "Срок возврата",
    key: "due_date",
    sorter: (row1, row2) => new Date(row1.raw_due_date) - new Date(row2.raw_due_date)
  }
];

const table = ref(null);
const pagination = { pageSize: 5 };

function sortTitle() {
  table.value?.sort("title", "ascend");
}

function sortDate() {
  table.value?.sort("created_at", "ascend");
}

function clearFilters() {
  table.value?.clearFilters();
}

function clearSorter() {
  table.value?.clearSorter();
}
</script>
