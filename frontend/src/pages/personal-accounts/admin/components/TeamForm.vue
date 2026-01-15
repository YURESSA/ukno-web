<template>
  <form @submit.prevent="submit" class="form">
    <label>ФИО*</label>
    <input v-model="full_name" required />

    <label>Описание</label>
    <textarea v-model="description" />

    <label>Фото</label>
    <n-upload
      :key="uploadKey"
      :max="1"
      :file-list="photo"
      @update:file-list="photo = $event"
      list-type="image-card"
    />

    <button class="hidden-submit" type="submit">submit</button>
  </form>
</template>

<script setup>
import { ref } from 'vue'
import { NUpload } from 'naive-ui'

const emit = defineEmits(['submit'])

const full_name = ref('')
const description = ref('')
const photo = ref([])
const uploadKey = ref(1)

function submit() {
  emit('submit', {
    full_name: full_name.value,
    description: description.value,
    photoFile: photo.value?.[0]?.file || null
  })
}

defineExpose({
  submit,
  reset() {
    full_name.value = ''
    description.value = ''
    photo.value = []
    uploadKey.value++
  }
})
</script>

<style scoped>
.form { display: flex; flex-direction: column; gap: 12px; width: 500px; }
input, textarea { padding: 12px 14px; border: 1px solid #e5e7eb; border-radius: 10px; }
textarea { min-height: 90px; resize: vertical; }
.hidden-submit { display: none; }
</style>
