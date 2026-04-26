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
      :data="categories"
      :bordered="false"
      :pagination="{ pageSize: 10 }"
    />

    <n-modal
      v-model:show="showModal"
      preset="card"
      style="width: 500px"
      title="Создание новой категории"
      :segmented="{ content: 'soft', footer: 'soft' }"
    >
      <n-form ref="formRef" :model="selectedItem" label-placement="top">
        <n-form-item label="Название категории">
          <n-input v-model:value="selectedItem.category_name" placeholder="Например: Воркшоп" />
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
const categories = computed(() => store.getCategories);
const message = useMessage();
const dialog = useDialog();
const loading = ref(false);

const showModal = ref(false);
const selectedItem = ref({
  category_name: ''
});

// --- КОЛОНКИ ТАБЛИЦЫ ---
const columns = [
  { title: 'ID', key: 'category_id'},
  { title: 'Название', key: 'category_name' },
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
  selectedItem.value = { category_name: '' };
  showModal.value = true;
});

// --- СОЗДАНИЕ ---
async function handleSave() {
  if (!selectedItem.value.category_name.trim()) {
    message.error('Введите название категории');
    return;
  }

  try {
    loading.value = true;
    await store.PostAdminNewCategories({ name: selectedItem.value.category_name });
    message.success('Категория успешно создана');
    showModal.value = false;
    await store.FetchCategories();
  } catch (e) {
    message.error('Ошибка при создании', e);
  } finally {
    loading.value = false;
  }
}

// --- УДАЛЕНИЕ (теперь принимает объект категории) ---
function confirmDelete(category) {
  dialog.warning({
    title: 'Удаление категории',
    content: `Вы действительно хотите удалить категорию "${category.category_name}"?`,
    positiveText: 'Удалить',
    negativeText: 'Отмена',
    onPositiveClick: async () => {
      try {
        await store.deleteCatigories(category.category_id);
        message.success('Категория удалена');
        await store.FetchCategories();
      } catch (e) {
        message.error('Не удалось удалить категорию', e);
      }
    }
  });
}

onMounted(() => store.FetchCategories());
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
