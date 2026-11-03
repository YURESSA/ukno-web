<template>
  <div class="section-container">
    <div class="filter-panel">
      <n-space>
        <n-input v-model:value="searchQuery" placeholder="Поиск по всем полям..." clearable style="width: 300px" />
        <n-select v-model:value="roleFilter" placeholder="Роль" :options="roleOptions" clearable style="width: 150px" />
      </n-space>
    </div>

    <n-data-table
      :loading="loading"
      :columns="columns"
      :data="filteredUsers"
      :row-props="rowProps"
      :pagination="{ pageSize: 10 }"
    />

    <n-modal
      v-model:show="showModal"
      preset="card"
      style="width: 600px"
      :title="isEdit ? 'Редактирование пользователя' : 'Регистрация нового пользователя'"
      :segmented="{ content: 'soft', footer: 'soft' }"
    >
      <n-form ref="formRef" :model="selectedItem" label-placement="top">
        <n-grid :cols="2" :x-gap="20">
          <n-form-item-gi span="2" label="Полное имя (ФИО)" v-bind="fieldProps(selectedItem, 'user', 'full_name', 'selectedItem.full_name', isEdit)">
            <n-input v-model:value="selectedItem.full_name" placeholder="Иванов Иван Иванович" />
          </n-form-item-gi>

          <n-form-item-gi label="Электронная почта" v-bind="fieldProps(selectedItem, 'user', 'email', 'selectedItem.email', isEdit)">
            <n-input
              v-model:value="selectedItem.email"
              placeholder="example@mail.com"
              :disabled="isEdit"
            />
          </n-form-item-gi>

          <n-form-item-gi label="Номер телефона" v-bind="fieldProps(selectedItem, 'user', 'phone', 'selectedItem.phone', isEdit)">
            <n-input v-model:value="selectedItem.phone" :allow-input="allowPhoneInput" :maxlength="32" :input-props="{ inputmode: 'tel', autocomplete: 'tel' }" placeholder="+7 (999) 000-00-00" />
          </n-form-item-gi>

          <n-form-item-gi label="Роль в системе" v-bind="fieldProps(selectedItem, 'user', 'role', 'selectedItem.role', isEdit)">
            <n-select v-model:value="selectedItem.role" :options="roleOptions" />
          </n-form-item-gi>

          <n-form-item-gi label="Пароль" v-bind="fieldProps(selectedItem, 'user', 'password', 'selectedItem.password', isEdit)">
            <n-input
              v-model:value="selectedItem.password"
              type="password"
              show-password-on="click"
              :placeholder="isEdit ? 'Заполните только для смены' : 'Введите пароль'"
            />
          </n-form-item-gi>
        </n-grid>
      </n-form>

      <template #footer>
        <div class="modal-footer">
          <div class="action-btn">
            <n-button
              v-if="isEdit"
              type="error"
              ghost
              @click="confirmDelete"
            >
              Удалить пользователя
            </n-button>
            <n-button @click="showModal = false">Отмена</n-button>
          </div>

          <div class="save-btn">
            <BaseButton
            class="small-btn"
              :text="isEdit ? 'Сохранить изменения' : 'Создать'"
              @click="handleSave"
              :loading="loading"
            />
          </div>
        </div>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { useAdminValidation } from '@/composables/useAdminValidation'
import { validateAdmin, allowPhoneInput } from '@/utils/adminValidation'
import { getApiErrorMessage } from '@/utils/apiError'
import { ref, computed, inject, watch, onMounted, h } from 'vue';
import { useDataStore } from '@/stores/counter';
import {
  NDataTable, NModal, NForm, NFormItemGi, NGrid, NInput,
  NSelect, NButton, NSpace, NTag, useMessage, useDialog
} from 'naive-ui';
import BaseButton from '@/components/ui/button/BaseButton.vue';

const { submitted, fieldProps, resetValidation } = useAdminValidation();

const store = useDataStore();
const users = computed(() => store.getUsers);
const message = useMessage();
const dialog = useDialog();
const loading = ref(false);

const showModal = ref(false);
const isEdit = ref(false);
const selectedItem = ref({
  user_id: null,
  full_name: '',
  email: '',
  phone: '',
  role: 'user',
  password: ''
});

const roleOptions = [
  { label: 'Администратор', value: 'admin' },
  { label: 'Резидент', value: 'resident' },
  { label: 'Пользователь', value: 'user' }
];

const searchQuery = ref('');
const roleFilter = ref(null);

const filteredUsers = computed(() => {
  if (!users.value) return [];
  const s = searchQuery.value.toLowerCase().trim();
  return users.value.filter(user => {
    const matchesRole = !roleFilter.value || user.role === roleFilter.value;
    if (!matchesRole) return false;
    if (!s) return true;
    return Object.values(user).some(val => String(val).toLowerCase().includes(s));
  });
});

const columns = [
  { title: 'ID', key: 'user_id' },
  { title: 'ФИО', key: 'full_name' },
  { title: 'Email', key: 'email' },
  { title: 'Телефон', key: 'phone', render: (row) => row.phone || '—' },
  {
    title: 'Роль',
    key: 'role',
    render(row) {
      const rolesMap = {
        admin: { type: 'error', label: 'Админ' },
        resident: { type: 'warning', label: 'Резидент' },
        user: { type: 'info', label: 'Пользователь' }
      };
      const config = rolesMap[row.role] || rolesMap.user;
      return h(
        NTag,
        { type: config.type, bordered: false },
        { default: () => config.label }
      );
    }
  }
];

const rowProps = (row) => ({
  style: 'cursor: pointer',
  onClick: () => {
    isEdit.value = true;
    selectedItem.value = { ...row, password: '' };
    showModal.value = true;
  }
});

const addTrigger = inject('admin-add-event');
watch(addTrigger, () => {
  isEdit.value = false;
  selectedItem.value = {
    user_id: null,
    full_name: '',
    email: '',
    phone: '',
    role: 'user',
    password: ''
  };
  showModal.value = true;
});

async function handleSave() {
  if (loading.value) return;
  submitted.value = true;
  const validationError = validateAdmin(selectedItem.value, 'user', isEdit.value);
  if (validationError) return message.error(validationError);
  const payload = {
    full_name: selectedItem.value.full_name,
    email: selectedItem.value.email,
    phone: selectedItem.value.phone,
    role_name: selectedItem.value.role,
  };

  if (selectedItem.value.password) {
    payload.password = selectedItem.value.password;
  }

  try {
    loading.value = true;
    if (isEdit.value) {
      await store.PutAdminUser(payload, selectedItem.value.email);
      message.success('Данные пользователя обновлены');
    } else {
      await store.PostAdminNewUser(payload);
      message.success('Пользователь успешно создан');
    }
    showModal.value = false;
    await store.FetchUsers();
  } catch (e) {
    message.error(getApiErrorMessage(e, 'Ошибка при сохранении'));
  } finally {
    loading.value = false;
  }
}

function confirmDelete() {
  dialog.warning({
    title: 'Подтверждение удаления',
    content: `Вы действительно хотите удалить пользователя ${selectedItem.value.full_name}? Это действие нельзя отменить.`,
    positiveText: 'Удалить',
    negativeText: 'Отмена',
    onPositiveClick: async () => {
      try {
        await store.DeleteAdminUser(selectedItem.value.email);
        message.success('Пользователь удален');
        showModal.value = false;
        await store.FetchUsers();
      } catch (e) {
        message.error(getApiErrorMessage(e, 'Ошибка при удалении'));
      }
    }
  });
}

onMounted(() => store.FetchUsers().catch(e => message.error(getApiErrorMessage(e, 'Ошибка загрузки данных'))));

watch(showModal, resetValidation);
</script>

<style scoped>
.modal-footer {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
  text-align: right;
}

.action-btn {
  display: flex;
  justify-content: center;
  width: 100%;
  gap: 10px;
}

.save-btn {
  display: flex;
  justify-content: center;
  width: 100%;
}

.small-btn {
    font-size: 16px;
}
</style>
