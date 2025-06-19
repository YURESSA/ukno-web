<template>
  <div class="page-wrapper">
    <div class="payment-wrapper">
      <div class="header-wrapper">
        <h4>Новое событие</h4>
        <IconButton @click="closePage" class="close_btn"><img src="/icon/maki_cross.svg" alt=""></IconButton>
      </div>
      <div class="person-info">
        <form @submit.prevent="submitEvent">
          <h5>О событии</h5>
            <input
              type="EventName"
              name="EventName"
              placeholder="Название события*"
              v-model="formData.title"
            >
            <input
              type="EventName"
              name="EventName"
              placeholder="Описание события*"
              v-model="formData.description"
            >
            <input
              type="EventName"
              name="EventName"
              placeholder="Формат события*"
              v-model="formData.format_type"
            >
            <input
              type="EventName"
              name="EventName"
              placeholder="Тип события*"
              v-model="formData.category"
            >
            <input
              type="EventName"
              name="EventName"
              placeholder="Возрастная категория*"
              v-model="formData.age_category"
            >

            <h5>Условие проведения</h5>
            <span>Дата и время события</span>
            <n-config-provider :locale="ruRU" :date-locale="dateRuRU">
              <n-date-picker
                v-model:formatted-value="formattedValue"
                value-format="yyyy-MM-dd HH:mm"
                type="datetime"
                clearable
                :time-picker-props="{
                  format: 'HH:mm',
                  hoursLabel: 'Часы',
                  minutesLabel: 'Минуты',
                  showSecond: false,
                }"
              />
            </n-config-provider>
            <input
              type="EventName"
              name="EventName"
              placeholder="Место сбора*"
              v-model="formData.place"
            >
            <div class="participants-input">
              <span>Продолжительность события (в минутах)</span>
              <div class="participants">
                <IconButton class="participants--btn left--btn" type="button" @click="minusDuration" text="-"/>
                <input v-model="formData.duration" @input="validateParticipants"/>
                <IconButton class="participants--btn right--btn" type="button" @click="plusDuration" text="+"/>
              </div>
            </div>
            <div class="participants-input">
              <span>Количество участников</span>
              <div class="participants">
                <IconButton class="participants--btn left--btn" type="button" @click="minusParticipants" text="-"/>
                <input v-model="formData.sessions[0].max_participants" @input="validateParticipants"/>
                <IconButton class="participants--btn right--btn" type="button" @click="plusParticipants" text="+"/>
              </div>
            </div>
            <div class="participants-input">
              <span>Стоимость</span>
              <div class="participants">
                <IconButton class="participants--btn left--btn" type="button" @click="minusPrice" text="-"/>
                <input v-model="formData.sessions[0].cost" @input="validateParticipants"/>
                <IconButton class="participants--btn right--btn" type="button" @click="plusPrice" text="+"/>
              </div>
            </div>
            <h5>Остальная информация</h5>
            <input
              type="EventName"
              name="EventName"
              placeholder="Органиатор*"
              v-model="formData.conducted_by"
            >
            <span>Время работы организации</span>
            <input
              type="EventName"
              name="EventName"
              placeholder="Ежедневно с 10:00 до 21:00"
              v-model="formData.working_hours"
            >
            <span>Почта для связи</span>
            <input
              type="EventName"
              name="EventName"
              placeholder="construct@ekbtour.ru"
              v-model="formData.contact_email"
            >
            <input
              type="EventName"
              name="EventName"
              placeholder="iframe карты с местоположением"
              v-model="formData.iframe_url"
            >
            <input
              type="EventName"
              name="EventName"
              placeholder="Telegram"
              v-model="formData.telegram"
            >
            <input
              type="EventName"
              name="EventName"
              placeholder="Vk"
              v-model="formData.vk"
            >
            <input
              type="EventName"
              name="EventName"
              placeholder="Дистанция от центра города (в метрах)"
              v-model="formData.distance_to_center"
            >
            <input
              type="EventName"
              name="EventName"
              placeholder="Время от ближайшей остановки (в минутах)"
              v-model="formData.time_to_nearest_stop"
            >
            <span>Хэштеги</span>
            <input
              type="EventName"
              name="EventName"
              placeholder="архитектура, конструктивизм, история"
              v-model="formData.tags"
            >

            <h5>Изображения</h5>
            <n-upload
              :default-file-list="previewFileList"
              list-type="image-card"
              @preview="handlePreview"
              @change="handleFileChange"
            />
            <n-modal
              v-model:show="showModal"
              preset="card"
              style="width: 600px"
              title="A Cool Picture"
            >
              <img :src="previewImageUrl" style="width: 100%">
            </n-modal>
            <BaseButton type="submit" class="sumbit--btn" text="Создать событие"/>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { ref } from 'vue';
import IconButton from '@/components/UI/button/IconButton.vue';
import BaseButton from '@/components/UI/button/BaseButton.vue';
import { useDataStore } from '@/stores/counter';
import { NDatePicker, NConfigProvider, NModal, NUpload } from 'naive-ui';
import { ruRU, dateRuRU } from 'naive-ui';

const store = useDataStore();
const router = useRouter();
const formattedValue = ref(null);

const formData = ref({
  title: '',
  description: '',
  category: '',
  format_type: '',
  age_category: '',
  place: '',
  conducted_by: '',
  is_active: true,
  working_hours: '',
  contact_email: '',
  iframe_url: '',
  telegram: '',
  vk: '',
  distance_to_center: '',
  time_to_nearest_stop: '',
  tags: '',
  sessions: [
    {
      start_datetime: '',
      max_participants: 1,
      cost: 0,
    }
  ],
  duration: 60,
});

function closePage(){
  router.back();
}

function minusDuration(){
  if (formData.value.duration > 10){
    formData.value.duration -= 10;
  }
}

function plusDuration(){
  formData.value.duration += 10;
}

function minusPrice(){
  if (formData.value.sessions[0].cost > 0){
    formData.value.sessions[0].cost -= 100;
    if(formData.value.sessions[0].cost < 0){
      formData.value.sessions[0].cost = 0;
    }
  }
}

function plusPrice(){
  formData.value.sessions[0].cost += 100;
}

function minusParticipants(){
  if (formData.value.sessions[0].max_participants > 1){
    formData.value.sessions[0].max_participants -= 1;
  }
}

function plusParticipants(){
  formData.value.sessions[0].max_participants += 1;
}


const showModal = ref(false);
const previewImageUrl = ref('');
const fileList = ref([]);
const previewFileList = ref([]);

const handlePreview = (file) => {
  previewImageUrl.value = file.url;
  showModal.value = true;
};

const handleFileChange = (data) => {
  fileList.value = data.fileList;
};

const submitEvent = async () => {
  try {
    // 1. Форматируем дату в ISO-формат (если formattedValue содержит "2025-06-06 22:45")
    const isoFormatted = formattedValue.value.replace(" ", "T") + ":00";
    formData.value.sessions[0].start_datetime = isoFormatted;

    // 2. Создаем FormData для файлов и JSON-данных
    const formDataToSend = new FormData();

    if (formData.value.tags) {
      formData.value.tags = formData.value.tags
        .split(',') // Разделяем по запятым
        .map(tag => tag.trim()) // Убираем пробелы по краям
        .filter(tag => tag.length > 0); // Удаляем пустые элементы
    }

    // 3. Добавляем файлы (если есть)
    fileList.value.forEach(file => {
      formDataToSend.append('photos', file.file);
    });

    // 4. Добавляем остальные данные в формате JSON
    formDataToSend.append('data', JSON.stringify(formData.value));

    console.log(formDataToSend)

    await store.PostNewEvent(formDataToSend);
    alert('Событие успешно создано')
    router.back();
  } catch (error) {
    console.error('Upload failed:', error);
    throw error;
  }
};
</script>

<style scoped>
.header-wrapper{
  display: flex;
  width: 100%;
  height: max-content;
  align-items: center;
  justify-content: flex-end;
  padding-bottom: 20px;
  border-bottom: 2px solid #7A797873;
}

.page-wrapper {
  display: flex;
  justify-content: center;
  position: relative;
  min-height: calc(100vh - 100px);
}

.payment-wrapper{
  width: 100%;
  max-width: 1800px;
}

h4{
  flex: 1;
  text-align: center;
  margin: 0;
}

.close_btn{
  width: 23px;
  height: 23px;
  padding: 4px;
  border-radius: 5px;
  border: none;
  background-color: #EDEDED8A;
}

form {
  display: flex;
  flex-direction: column;
  width: 60%;
  margin-bottom: 30px;
  gap: 20px;
}

.person-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  max-width: 1800px;
  position: relative;
  margin-top: 30px;
}

input {
  padding: 15px 0;
  border: 2px solid #2C2C2C24;
  border-radius: 8px;
  padding-left: 20px;
  transition: all 0.5s ease;
}

input:focus {
  outline: none;
  background-color: #F3F3F3;
}

.participants-input{
  display: flex;
  flex-direction: column;
  gap: 10px;
  color: #9E9E9E;
}

span{
  color: #9E9E9E;
}

.participants{
  display: flex;
  max-width: 150px;
  margin-bottom: 10px;
}

.participants > input {
  width: 45px;
  padding: 0;
  border: none;
  text-align: center;
  border: 2px solid #E2E2E2;
  border-width: 2px 0;
  border-radius: 0;
}

.participants--btn{
  border: 2px solid #E2E2E2;
  padding: 10px 16px;
  border-radius: 12px 0 0 12px;
}

.left--btn{
  border-radius: 12px 0 0 12px;
}

.right--btn{
  border-radius: 0 12px 12px 0;
}

</style>
