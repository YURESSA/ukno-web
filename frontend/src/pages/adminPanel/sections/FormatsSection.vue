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
      :data="format"
      :bordered="false"
      :pagination="{ pageSize: 10 }"
    />

    <n-modal
      v-model:show="showModal"
      preset="card"
      style="width: 500px"
      title="Создание нового формата"
      :segmented="{ content: 'soft', footer: 'soft' }"
    >
      <n-form ref="formRef" :model="selectedItem" label-placement="top">
        <n-form-item label="Название формата">
          <n-input v-model:value="selectedItem.format_type_name" placeholder="Например: Индивидуальная" />
        </n-form-item>
      </n-form>

      <template #footer>
        <div class="modal-footer">
          <n-space justify="center">
            <n-button @click="showModal = false">Отмена</n-button>
            <BaseButton
              class="small-btn"
              text="Создать формат"
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
import BaseButton from '@/components/ui/button/BaseButton.vue';

const store = useDataStore();
const format = computed(() => store.getFormat);
const message = useMessage();
const dialog = useDialog();
const loading = ref(false);

const showModal = ref(false);
const selectedItem = ref({
  format_type_name: ''
});

const columns = [
  { title: 'ID', key: 'format_type_id'},
  { title: 'Название', key: 'format_type_name' },
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
          onClick: () => confirmDelete(row)
        },
        { default: () => 'Удалить' }
      );
    }
  }
];

const addTrigger = inject('admin-add-event');
watch(addTrigger, () => {
  selectedItem.value = { format_type_name: '' };
  showModal.value = true;
});

async function handleSave() {
  if (!selectedItem.value.format_type_name.trim()) {
    message.error('Введите название формата');
    return;
  }

  try {
    loading.value = true;
    await store.PostAdminNewFormat({ name: selectedItem.value.format_type_name });
    message.success('Формат успешно создан');
    showModal.value = false;
    await store.FetchFormat();
  } catch (e) {
    message.error('Ошибка при создании', e);
  } finally {
    loading.value = false;
  }
}

function confirmDelete(format) {
  dialog.warning({
    title: 'Удаление категории',
    content: `Вы действительно хотите удалить категорию "${format.format_type_name}"?`,
    positiveText: 'Удалить',
    negativeText: 'Отмена',
    onPositiveClick: async () => {
      try {
        await store.deleteFormat(format.format_type_id);
        message.success('Категория удалена');
        await store.FetchFormat();
      } catch (e) {
        message.error('Не удалось удалить категорию', e);
      }
    }
  });
}

onMounted(() => store.FetchFormat());
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
