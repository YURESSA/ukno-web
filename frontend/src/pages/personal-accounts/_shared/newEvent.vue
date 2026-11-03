<template>
  <div class="page-wrapper">
    <div class="payment-wrapper">
      <div class="header-wrapper">
        <h4>Новое событие</h4>
        <IconButton @click="closePage" aria-label="Закрыть форму события" class="close_btn"><img src="/icon/maki_cross.svg" alt=""></IconButton>
      </div>
      <div class="person-info">
        <form @submit.prevent="submitEvent" novalidate>
          <p class="text-standart bold">О событии</p>
            <input
              type="EventName"
              name="EventName"
              placeholder="Название события*"
              v-model="formData.title"
            >
            <span v-if="fieldError('title')" class="field-error" role="alert">{{ fieldError('title') }}</span>
            <textarea
              type="EventName"
              name="EventName"
              placeholder="Описание события*" required
              v-model="formData.description"
            ></textarea>
            <span v-if="fieldError('description')" class="field-error" role="alert">{{ fieldError('description') }}</span>

            <select v-model="formData.format_type" class="custom-select" required>
              <option class="placeholder" value="" disabled>Формат события*</option>
              <option
              class="option"
              :value="format.format_type_name"
              v-for="format in excursionsStats.format_types"
              :key="format.format_type_id"
              >
                {{ format.format_type_name }}
              </option>
            </select>
            <span v-if="fieldError('format_type')" class="field-error" role="alert">{{ fieldError('format_type') }}</span>

            <select v-model="formData.category" class="custom-select" required>
              <option class="placeholder" value="" disabled>Тип события*</option>
              <option
              class="option"
              :value="category.category_name"
              v-for="category in excursionsStats.categories"
              :key="category.category_id"
              >
                {{ category.category_name }}
              </option>
            </select>
            <span v-if="fieldError('category')" class="field-error" role="alert">{{ fieldError('category') }}</span>

            <select v-model="formData.age_category" class="custom-select" required>
              <option class="placeholder" value="" disabled>Возрастная категория*</option>
              <option
              class="option"
              :value="age_category.age_category_name"
              v-for="age_category in excursionsStats.age_categories"
              :key="age_category.age_category_id"
              >
                {{ age_category.age_category_name }}
              </option>
            </select>
            <span v-if="fieldError('age_category')" class="field-error" role="alert">{{ fieldError('age_category') }}</span>

            <p class="text-standart bold">Условие проведения</p>
            <span>Дата и время события*</span>
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
            <span v-if="sessionError('start_datetime')" class="field-error" role="alert">{{ sessionError('start_datetime') }}</span>
            <input
              type="EventName"
              name="EventName"
              placeholder="Место сбора*"
              v-model="formData.place"
            >
            <span v-if="fieldError('place')" class="field-error" role="alert">{{ fieldError('place') }}</span>
            <div class="participants-input">
              <span>Продолжительность события (в минутах)*</span>
              <div class="participants">
                <IconButton class="participants--btn left--btn" type="button" @click="minusDuration" text="-"/>
                <input type="number" v-model.number="formData.duration" min="0" step="1" />
            <span v-if="fieldError('duration')" class="field-error" role="alert">{{ fieldError('duration') }}</span>
                <IconButton class="participants--btn right--btn" type="button" @click="plusDuration" text="+"/>
              </div>
            </div>
            <div class="participants-input">
              <span>Количество участников*</span>
              <div class="participants">
                <IconButton class="participants--btn left--btn" type="button" @click="minusParticipants" text="-"/>
                <input type="number" v-model.number="formData.sessions[0].max_participants" min="1" step="1" /><span v-if="sessionError('max_participants')" class="field-error" role="alert">{{ sessionError('max_participants') }}</span>
                <IconButton class="participants--btn right--btn" type="button" @click="plusParticipants" text="+"/>
              </div>
            </div>
            <div class="participants-input">
              <span>Стоимость*</span>
              <div class="participants">
                <IconButton class="participants--btn left--btn" type="button" @click="minusPrice" text="-"/>
                <input type="number" v-model.number="formData.sessions[0].cost" min="0" step="any" /><span v-if="sessionError('cost')" class="field-error" role="alert">{{ sessionError('cost') }}</span>
                <IconButton class="participants--btn right--btn" type="button" @click="plusPrice" text="+"/>
              </div>
            </div>
            <p class="text-standart bold">Остальная информация</p>
            <input
              type="EventName"
              name="EventName"
              placeholder="Организатор"
              v-model="formData.conducted_by"
            >
            <span v-if="fieldError('conducted_by')" class="field-error" role="alert">{{ fieldError('conducted_by') }}</span>
            <span>Время работы организации</span>
            <input
              type="EventName"
              name="EventName"
              placeholder="Ежедневно с 10:00 до 21:00"
              v-model="formData.working_hours"
            >
            <span v-if="fieldError('working_hours')" class="field-error" role="alert">{{ fieldError('working_hours') }}</span>
            <span>Почта для связи</span>
            <input
              type="EventName"
              name="EventName"
              placeholder="construct@ekbtour.ru"
              v-model="formData.contact_email"
            >
            <span v-if="fieldError('contact_email')" class="field-error" role="alert">{{ fieldError('contact_email') }}</span>
            <span>Местоположение на карте</span>
            <MapPicker
              map-id="new-event-map"
              @update:coords="onCoordsUpdate"
            />
            <input
              type="EventName"
              name="EventName"
              placeholder="Telegram"
              v-model="formData.telegram"
            >
            <span v-if="fieldError('telegram')" class="field-error" role="alert">{{ fieldError('telegram') }}</span>
            <input
              type="EventName"
              name="EventName"
              placeholder="Vk"
              v-model="formData.vk"
            >
            <span v-if="fieldError('vk')" class="field-error" role="alert">{{ fieldError('vk') }}</span>
            <input type="number"
              name="EventName"
              placeholder="Дистанция от центра города (в метрах)"
              v-model.number="formData.distance_to_center" min="0" step="any"
            >
            <span v-if="fieldError('distance_to_center')" class="field-error" role="alert">{{ fieldError('distance_to_center') }}</span>
            <input type="number"
              name="EventName"
              placeholder="Время от ближайшей остановки (в минутах)"
              v-model.number="formData.time_to_nearest_stop" min="0" step="any"
            >
            <span v-if="fieldError('time_to_nearest_stop')" class="field-error" role="alert">{{ fieldError('time_to_nearest_stop') }}</span>

            <p class="text-standart bold">Изображения*</p>
            <span v-if="submitted && !fileList.some(file => file.file)" class="field-error" role="alert">Добавьте хотя бы одну фотографию события</span>
            <n-upload
              accept="image/*"
              :default-upload="false"
              :default-file-list="previewFileList"
              list-type="image-card"
              @preview="handlePreview"
              @change="handleFileChange"
            />
            <n-modal
              v-model:show="showModal"
              preset="card"
              style="width: 600px"
              title="Просмотр фотографии"
            >
              <img :src="previewImageUrl" style="width: 100%">
            </n-modal>
            <p>После создания событие будет отправлено на проверку администратору и появится на сайте после одобрения.</p>
            <BaseButton :loading="saving" type="submit" class="sumbit--btn" text="Отправить на проверку"/>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { validateAdmin, getAdminFieldError } from '@/utils/adminValidation'
import { getApiErrorMessage } from '@/utils/apiError'
import { useRouter } from 'vue-router';
import { ref, onMounted, computed } from 'vue';
import IconButton from '@/components/ui/button/IconButton.vue';
import BaseButton from '@/components/ui/button/BaseButton.vue';
import MapPicker from '@/components/shared/MapPicker.vue';
import { useDataStore } from '@/stores/counter';
import { NDatePicker, NConfigProvider, NModal, NUpload } from 'naive-ui';
import { ruRU, dateRuRU } from 'naive-ui';
import { notification } from '@/utils/notification'

const store = useDataStore();
const router = useRouter();
const formattedValue = ref(null);
const submitted = ref(false);
const saving = ref(false);
const fieldError = key => {
  if (!submitted.value) return '';
  const value = formData.value[key];
  const optionalNumber = ['distance_to_center', 'time_to_nearest_stop'].includes(key);
  return getAdminFieldError({ ...formData.value, [key]: optionalNumber && value === '' ? null : value }, 'residentEvent', key);
};
const sessionError = key => submitted.value ? getAdminFieldError({ ...formData.value.sessions[0], start_datetime: formattedValue.value }, 'session', key) : '';

onMounted(async () => {
  await store.FetchExcursionsStats();
});

const excursionsStats = computed(() => store.getExcursionsStats);


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
  latitude: null,
  longitude: null,
  telegram: '',
  vk: '',
  distance_to_center: null,
  time_to_nearest_stop: null,
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

function onCoordsUpdate({ latitude, longitude }) {
  formData.value.latitude = latitude;
  formData.value.longitude = longitude;
}

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
  if (saving.value) return;
  submitted.value = true;
  const payload = {
    ...formData.value,
    distance_to_center: formData.value.distance_to_center === '' ? null : formData.value.distance_to_center,
    time_to_nearest_stop: formData.value.time_to_nearest_stop === '' ? null : formData.value.time_to_nearest_stop,
    sessions: [{ ...formData.value.sessions[0], start_datetime: formattedValue.value ? formattedValue.value.replace(' ', 'T') + ':00' : '' }],
    tags: String(formData.value.tags || '').split(',').map(tag => tag.trim()).filter(Boolean),
  };
  const validationError = validateAdmin(payload, 'residentEvent');
  if (validationError) return notification(validationError, 'negative');
  if (!fileList.value.some(file => file.file)) return notification('Добавьте хотя бы одну фотографию события', 'negative');
  try {
    saving.value = true;
    const formDataToSend = new FormData();
    fileList.value.forEach(file => { if (file.file) formDataToSend.append('photos', file.file); });
    formDataToSend.append('data', JSON.stringify(payload));
    await store.PostNewEvent(formDataToSend);
    await notification('Событие создано и отправлено на проверку', 'positive');
    router.back();
  } catch (error) {
    notification(getApiErrorMessage(error, 'Не удалось создать событие'), 'negative');
  } finally {
    saving.value = false;
  }
};

</script>

<style scoped>
.field-error { color: #d03050; font-size: 13px; }
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

input, textarea, select {
  padding: 15px 0;
  border: 2px solid #2C2C2C24;
  border-radius: 8px;
  padding-left: 20px;
  transition: all 0.5s ease;
  font-size: 14px;
  font-weight: 400 !important;
  font-family: 'Manrope' !important;
}

.custom-select option.placeholder {
  color: #999;
}

.custom-select {
  color: #777;
}

.option{
  color: #333;
}

.custom-select:valid {
  color: #333;
}

input:focus, textarea:focus {
  outline: none;
  background-color: #F3F3F3;
}

input::placeholder,
textarea::placeholder {
  font-weight: 400 !important;
}

.participants--btn {
  background: white;
  color: #9E9E9E;
}

input::-webkit-input-placeholder,
textarea::-webkit-input-placeholder {
  font-weight: 400 !important;
}

input::-moz-placeholder,
textarea::-moz-placeholder {
  font-weight: 400 !important;
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

@media (max-width: 768px) {
  h4{
    font-size: 28px;
  }
  form{
    width: 100%;
  }
}
</style>
