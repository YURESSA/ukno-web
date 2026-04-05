<template>
  <div class="section-container">
    <!-- <div class="filter-panel">
      <n-space>
        <n-input v-model:value="searchQuery" placeholder="Поиск категории..." clearable style="width: 300px" />
      </n-space>
    </div> -->

    <n-data-table
      :loading="loading"
      :columns="columns"
      :data="age"
      :bordered="false"
      :pagination="{ pageSize: 10 }"
    />

    <n-modal
      v-model:show="showModal"
      preset="card"
      style="width: 500px"
      title="Создание новой возрастной категории"
      :segmented="{ content: 'soft', footer: 'soft' }"
    >
      <n-form ref="formRef" :model="selectedItem" label-placement="top">
        <n-form-item label="Название возрастной категории">
          <n-input v-model:value="selectedItem.age_category_name" placeholder="Например: Для детей (0-6 лет)" />
        </n-form-item>
      </n-form>

      <template #footer>
        <div class="modal-footer">
          <n-space justify="center">
            <n-button @click="showModal = false">Отмена</n-button>
            <BaseButton
              class="small-btn"
              text="Создать категорию"
              @click="handleSave"
              :loading="loading"
            />
          </n-space>
        </div>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, computed, inject, watch, onMounted, h } from 'vue';
import { useDataStore } from '@/stores/counter';
import { NDataTable, NModal, NForm, NFormItem, NInput, NButton, NSpace, useMessage, useDialog } from 'naive-ui';
import BaseButton from '@/components/UI/button/BaseButton.vue';

const store = useDataStore();
const age = computed(() => store.getAge);
const message = useMessage();
const dialog = useDialog();
const loading = ref(false);

const showModal = ref(false);
const selectedItem = ref({
  age_category_name: ''
});

// --- КОЛОНКИ ТАБЛИЦЫ ---
const columns = [
  { title: 'ID', key: 'age_category_id'},
  { title: 'Название', key: 'age_category_name' },
  {
    title: 'Действия',
    key: 'actions',
    width: 150,
    align: 'center',
    render(row) {
      return h(
        NButton,
        {
          type: 'error',
          size: 'small',
          ghost: true,
          onClick: () => confirmDelete(row) // Передаем строку целиком в функцию удаления
        },
        { default: () => 'Удалить' }
      );
    }
  }
];

// Обработка кнопки "Добавить" из Header
const addTrigger = inject('admin-add-event');
watch(addTrigger, () => {
  selectedItem.value = { age_category_name: '' };
  showModal.value = true;
});

// --- СОЗДАНИЕ ---
async function handleSave() {
  if (!selectedItem.value.age_category_name.trim()) {
    message.error('Введите название возрастной категории');
    return;
  }

  try {
    loading.value = true;
    await store.PostAdminNewAge({ name: selectedItem.value.age_category_name });
    message.success('Возрастная категория успешно создана');
    showModal.value = false;
    await store.FetchAge();
  } catch (e) {
    message.error('Ошибка при создании', e);
  } finally {
    loading.value = false;
  }
}

// --- УДАЛЕНИЕ (теперь принимает объект категории) ---
function confirmDelete(age) {
  dialog.warning({
    title: 'Удаление категории',
    content: `Вы действительно хотите удалить категорию "${age.age_category_name}"?`,
    positiveText: 'Удалить',
    negativeText: 'Отмена',
    onPositiveClick: async () => {
      try {
        await store.deleteAge(age.age_category_id);
        message.success('Возрастная категория удалена');
        await store.FetchAge();
      } catch (e) {
        message.error('Не удалось удалить категорию', e);
      }
    }
  });
}

onMounted(() => store.FetchAge());
</script>

<style scoped>
.modal-footer {
  display: flex;
  flex-direction: column;
  gap: 15px;
  width: 100%;
}
.action-btn {
  display: flex;
  justify-content: center;
  gap: 10px;
}
.save-btn {
  display: flex;
  justify-content: center;
}
.small-btn {
  font-size: 16px;
}
</style>
