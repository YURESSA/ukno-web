<template>
  <div class="team-section">
    <n-space vertical size="large">
      <n-h2 style="margin: 0">Команда</n-h2>

      <n-data-table
        :columns="columns"
        :data="team"
        :loading="loading"
        :row-props="rowProps"
      />
    </n-space>

    <n-modal
      v-model:show="showModal"
      preset="card"
      style="width: 500px"
      :title="isEditMode ? 'Редактировать сотрудника' : 'Новый сотрудник'"
    >
      <n-form>
        <n-form-item label="ФИО">
          <n-input v-model:value="memberModel.full_name" placeholder="Константин Константинопольский" />
        </n-form-item>

        <n-form-item label="Описание">
          <Editor v-model="memberModel.description" />
        </n-form-item>

        <n-form-item label="Фото сотрудника">
          <n-upload
            v-model:file-list="fileList"
            @change="handleUploadChange"
            @remove="handleRemove"
            :max="1"
            list-type="image-card"
            accept="image/*"
          >
            Нажмите, чтобы <br> загрузить новое
          </n-upload>
        </n-form-item>
      </n-form>

      <template #footer>
        <n-space justify="space-between">
          <n-button v-if="isEditMode" type="error" ghost @click="handleDelete">Удалить</n-button>
          <div v-else></div> <n-space>
            <n-button @click="showModal = false">Отмена</n-button>
            <n-button type="primary" :loading="submitLoading" @click="handleSave">Сохранить</n-button>
          </n-space>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, onMounted, h, inject, watch, computed } from 'vue'
import { baseUrl, useDataStore } from '@/stores/counter'
import {
  NButton, useMessage, NSpace, NH2, NDataTable,
  NModal, NForm, NFormItem, NInput, NUpload, NImage, useDialog
} from 'naive-ui'
import Editor from '@/components/ui/Editor.vue'

const store = useDataStore()
const message = useMessage()
const dialog = useDialog();
const team = computed(() => store.getTeamData)
const fileList = ref([])

const addEvent = inject('admin-add-event')

const showModal = ref(false)
const isEditMode = ref(false)
const loading = ref(false)
const submitLoading = ref(false)

const memberModel = ref({
  id: null,
  full_name: '',
  description: '',
  photo: null,
  photo_url: ''
})

watch(addEvent, () => {
  openCreateModal()
})

const columns = [
  {
    title: 'Фото',
    key: 'photo',
    width: 350,
    render(row) {
      return h(NImage, {
        width: 90,
        height: 90,
        src: baseUrl + row.photo,
        style: 'border-radius: 4px; object-fit: cover;',
        onClick: (e) => e.stopPropagation()
      })
    }
  },
  { title: 'ФИО', key: 'full_name', width: 550 },
  { title: 'Описание', key: 'description' }
]

const rowProps = (row) => {
  return {
    style: 'cursor: pointer',
    onClick: () => {
      openEditModal(row)
    }
  }
}

const openEditModal = (row) => {
  isEditMode.value = true
  memberModel.value = {
    id: row.id,
    full_name: row.full_name,
    description: row.description,
    photo: null,
    photo_url: row.photo
  }

  if (row.photo) {
    fileList.value = [
      {
        id: 'existing-photo',
        name: 'current_photo.png',
        status: 'finished',
        url: baseUrl + row.photo
      }
    ]
  } else {
    fileList.value = []
  }

  showModal.value = true
}

const openCreateModal = () => {
  isEditMode.value = false
  memberModel.value = { id: null, full_name: '', description: '', photo: null, photo_url: '' }
  fileList.value = []
  showModal.value = true
}

const handleUploadChange = (data) => {
  memberModel.value.photo = data.fileList.length > 0 ? data.fileList[0].file : null
}

const handleSave = async () => {
  if (!memberModel.value.full_name) return message.error('Введите ФИО')

  const formData = new FormData()
  formData.append('full_name', memberModel.value.full_name)
  formData.append('description', memberModel.value.description || '')

  try {
    submitLoading.value = true
    if (isEditMode.value) {

      await store.UpdateTeamMember(memberModel.value.id, formData)
      if (memberModel.value.photo) {
        const photoData = new FormData()
        photoData.append('photo', memberModel.value.photo)
        await store.UpdatePhotoMember(memberModel.value.id, photoData)
      }
      message.success('Данные обновлены')
    } else {
      await store.AddTeamMember(formData)
      message.success('Сотрудник добавлен')
    }
    showModal.value = false
    await store.FetchTeam()
  } catch (e) {
    message.error('Ошибка при сохранении')
    console.error(e)
  } finally {
    submitLoading.value = false
  }
}

const handleRemove = (options) => {
  const { file } = options;

  if (file.id !== 'existing-photo') {
    memberModel.value.photo = null;
    return true;
  }

  return new Promise((resolve) => {
    dialog.warning({
      title: 'Удаление фото',
      content: 'Вы уверены, что хотите полностью удалить фото этого элемента с сервера?',
      positiveText: 'Удалить',
      negativeText: 'Отмена',
      onPositiveClick: async () => {
        try {
          submitLoading.value = true;
          await store.DeletePhotoMember(memberModel.value.id);

          message.success('Фото удалено с сервера');
          memberModel.value.photo_url = '';

          await store.FetchCulturalSpace();
          resolve(true);
        } catch (e) {
          console.error(e);
          message.error('Ошибка при удалении фото');
          resolve(false);
        } finally {
          submitLoading.value = false;
        }
      },
      onNegativeClick: () => resolve(false)
    });
  });
};

const handleDelete = async () => {
  if (confirm('Удалить этого сотрудника?')) {
    try {
      submitLoading.value = true
      await store.DeleteTeamMember(memberModel.value.id)
      message.success('Удалено')
      showModal.value = false
      await store.FetchTeam()
    } catch (e) {
      message.error('Ошибка при удалении')
    } finally {
      submitLoading.value = false
    }
  }
}

onMounted(() => {
  loading.value = true
  store.FetchTeam().finally(() => loading.value = false)
})
</script>

<style scoped>
:deep(.n-data-table-tr:hover) {
  background-color: rgba(255, 108, 54, 0.05) !important;
}
</style>
