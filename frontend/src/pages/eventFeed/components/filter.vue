<template>
  <div class="filter-wrapper">
    <div class="filter-header">
      <div class="title">
        <h4>Фильтры</h4>
      </div>
      <div>
        <button class="close__button"><img src="/icon/filter/close.svg" alt="Закрыть" @click="closeFilter"></button>
      </div>
    </div>
    <div class="filter-main">
      <div class="filter-component">
        <h5>Формат</h5>
        <div class="checkbox-wrapper">
          <n-checkbox
            size="large"
            value="Все варинаты"
            label="Все варинаты"
            @update:checked="(checked) => handleCheckboxChange(checked)"
          />
          <n-checkbox-group v-model:value="formData.category">
            <n-space class="checkbox-group" item-style="display: flex;">
              <n-checkbox
                v-for="option in allFormatOptions"
                :key="option"
                size="large"
                :value="option"
                :label="option"
              />
            </n-space>
          </n-checkbox-group>
        </div>
      </div>
      <div class="filter-component">
        <h5>Даты</h5>
        <n-date-picker v-model:value="range" type="daterange" clearable />
      </div>
      <!-- <div class="filter-component participants-filter">
        <h5>Количество участников</h5>
        <div class="participants-input">
          <div class="participants">
            <IconButton class="participants--btn left--btn" type="button" @click="minusParticipants" text="-"/>
            <input v-model="formData.participants_count" @input="validateParticipants"/>
            <IconButton class="participants--btn right--btn" type="button" @click="plusParticipants" text="+"/>
          </div>
        </div>
      </div> -->
      <div class="filter-component">
        <h5>Тип экскурсии</h5>
        <n-checkbox-group v-model:value="formData.format_type">
          <n-space class="checkbox-group" item-style="display: flex;">
            <n-checkbox size="large" value="Индивидуальная">
              Индивидуальная<br>
              <span class="type-descript">Личная встреча для вас или для вашей компании</span>
            </n-checkbox>
            <n-checkbox size="large" value="Групповая">
              Групповая<br>
              <span class="type-descript">Вы будете на экскурсии в группе с другими участниками</span>
            </n-checkbox>
            <n-checkbox size="large" value="Мини-группа">
              Мини-группа<br>
              <span class="type-descript">До 10 человек</span>
            </n-checkbox>
          </n-space>
        </n-checkbox-group>
      </div>
      <div class="filter-component">
        <h5>Цена за событие, ₽</h5>
        <n-space class="price-slider" vertical>
          <n-space class="price-input">
            <n-input-number v-model:value="priceRange[0]" :step="100" placeholder="Сумма от" size="small" :show-button="false" />
            <n-input-number class="right-input" v-model:value="priceRange[1]" :step="100" placeholder="Сумма до" size="small" :show-button="false" />
          </n-space>
          <n-slider v-model:value="priceRange" range :step="100" :min="excursionsStats.cost.min" :max="excursionsStats.cost.max" />
        </n-space>
      </div>
      <div class="filter-component">
        <h5>Возрастная категория</h5>
        <n-checkbox-group v-model:value="formData.age_category" @update:value="handleFormatTypeChange">
          <n-space class="checkbox-group" item-style="display: flex;">
            <n-checkbox size="large" value="Для детей (0-6 лет)">
              Для детей (0-6 лет)
            </n-checkbox>
            <n-checkbox size="large" value="Для школьников (7-17 лет)">
              Для школьников (7-17 лет)
            </n-checkbox>
            <n-checkbox size="large" value="Для взрослых (18+)">
              Для взрослых (18+)
            </n-checkbox>
            <n-checkbox size="large" value="Для всех возрастов (семейные)">
              Для всех возрастов (семейные)
            </n-checkbox>
          </n-space>
        </n-checkbox-group>
      </div>
    </div>
    <div class="interact-button">
      <BaseButton type="button" text="Показать" @click="sendFilter"/>
      <DefaultButton class="reset-button" @click="resetFilter" text="Сбросить" icon="" />
    </div>
  </div>
</template>

<script setup>
import { ref, defineEmits, watch, onMounted, computed } from 'vue'
import { NCheckbox, NCheckboxGroup, NSpace, NInputNumber, NSlider, NDatePicker } from 'naive-ui'
import BaseButton from '@UI/button/BaseButton.vue'
import DefaultButton from '@UI/button/DefaultButton.vue'
import IconButton from '@/components/UI/button/IconButton.vue'
import { useDataStore } from '@/stores/counter';

const store = useDataStore();

onMounted(async () => {
  await store.FetchExcursionsStats();
});

const excursionsStats = computed(() => store.getExcursionsStats);

const allFormatOptions = computed(() => {
  if (!excursionsStats.value || !excursionsStats.value.categories) {
    return ['Загрузка...'];
  }
  return [...excursionsStats.value.categories.map(item => item.category_name)];
});

const priceRange = ref([excursionsStats.value.cost.min, excursionsStats.value.cost.max])
const range = ref([Date.now(), Date.now() + 7 * 24 * 60 * 60 * 1000]);

const formData = ref({
  category: [],
  start_date: '',
  end_date: '',
  participants_count: 1,
  format_type: '',
  min_price: '',
  max_price: '',
  age_category: '',
});


function handleCheckboxChange(ch){
  if(ch){
    formData.value.category = allFormatOptions.value;
  } else {
    formData.value.category = [];
  }
}

function validateParticipants(){
  if(formData.value.participants_count < 1){
    formData.value.participants_count = 1
  }
}

function minusParticipants(){
  if (formData.value.participants_count > 1){
    formData.value.participants_count -= 1;
  }
}

function plusParticipants(){
  formData.value.participants_count += 1;
}

const emit = defineEmits(['close']);

function closeFilter(){
  emit('close')
}

function buildQueryString(formData) {
  const [startDate, endDate] = range.value.map(timestamp => {
    return new Date(timestamp).toISOString().split('T')[0];
  });
  formData.value.start_date = startDate;
  formData.value.end_date = endDate;
  formData.value.min_price = priceRange.value[0];
  formData.value.max_price = priceRange.value[1];

  const params = new URLSearchParams();

  for (const [key, value] of Object.entries(formData.value)) {
    if (value === null || value === undefined || value === '') continue;

    if (Array.isArray(value)) {
      if (value.length > 0) {
        params.append(key, value.join(','));
      }
    } else {
      params.append(key, value);
    }
  }

  console.log(params.toString());
  return params.toString();
}

const sendFilter = async () => {
  const queryString = buildQueryString(formData);
  try {
    await store.GetFilterExcursions(queryString);
  } catch (error) {
    console.error('Ошибка при загрузке экскурсий:', error);
  }
}

const resetFilter = async () => {
  try {
    await store.FetchExcursions();
    formData.value = {
      category: [],
      start_date: '',
      end_date: '',
      participants_count: 1,
      format_type: '',
      min_price: '',
      max_price: '',
      age_category: '',
    }
  } catch (error) {
    console.error('Ошибка при загрузке экскурсий:', error);
  }
}
</script>


<style scoped>
.filter-wrapper{
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  max-width: 450px;
  background-color: #FFFFFF;
  padding: 40px 45px;
  box-shadow: 0px 4px 13px 0px #00000040;
  border-radius: 38px;

  position: fixed;
  top: 150px;
  right: -150%;
  z-index: 100;

  overflow-y: scroll;
  height: calc(100vh - 230px);

  scrollbar-width: none;

  transition: all 0.5s ease;
}

.filter-wrapper {
  /* Стили для WebKit (Chrome, Safari, Edge) */
  &::-webkit-scrollbar {
    width: 8px; /* ширина вертикального скролла */
  }

  &::-webkit-scrollbar-track {
    background: #f1f1f1; /* цвет трека */
    border-radius: 4px;
  }

  &::-webkit-scrollbar-thumb {
    background: #888; /* цвет ползунка */
    border-radius: 4px;
  }

  &::-webkit-scrollbar-thumb:hover {
    background: #555; /* цвет при наведении */
  }
}

.filter-header{
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  border-bottom: 2px solid #7A797873;
  padding-bottom: 20px;
  margin-bottom: 20px;
}

.filter-main{
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 40px;
}

.filter-component{
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
}

.filter-component.participants-filter{
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  width: 100%;
}

.close__button{
  padding: 6px 6px;
  border-radius: 100%;
  background-color: #EDEDED8A;
}

.close__button:hover{
  background-color: #afaeae8a;
}

.close__button:active{
  background-color: #e7e4e4b7;
}

.checkbox-group {
  flex-direction: column!important;
  gap: 10px!important;
}

.checkbox-wrapper > .n-checkbox{
  margin-bottom: 10px;
}

.participants-input{
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.participants{
  display: flex;
  max-width: 150px;
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

.type-descript{
  color: #8C8C8C;
}

.price-slider{
  display: flex;
  flex-direction: column;
  margin: 0 auto;
  width: 350px;
}

.price-input{
  display: flex;
  justify-content: center!important;
  gap: 0!important;
  border-radius: 0 0 0 0!important;
  margin-bottom: 20px;
}

.interact-button{
  display: flex;
  justify-content: space-between;
  width: 100%;
  margin-top: 40px;
}

.reset-button{
  width: 226;
  height: 45;
  border-radius: 15px;
  padding: 10px 50px;
  color: #000000;
  font-weight: 400;
  font-size: 20px;
}

:deep(.n-checkbox__label){
  font-weight: 600;
  font-size: 20px;
}

:deep(.n-slider-rail__fill){
  --n-fill-color: #F25C03;
  --n-fill-color-hover: #F25C03;
  --n-fill-color-focus: #F25C03;
}

:deep(.n-slider-handle){
  border: 7px solid #F25C03;
}

:deep(.n-input-number){
  width: 175px;
}

:deep(.n-input-wrapper){
  height: 52px;
  display: flex;
  justify-content: center;
  align-items: center;
}

:deep(.n-input){
  border-radius: 0px;
  --n-border: 1px solid #BABABA;
  --n-border-hover: 2px solid #F25C03 !important;
  --n-border-focus: 2px solid #F25C03 !important;
  --n-box-shadow-focus: none!important;
  --n-font-size: 20px!important;
  transition: all 0.25s ease;
}

:deep(.n-input__input-el){
  font-weight: 600;
  text-align: center;
}

:deep(.n-checkbox-box){
  --n-color-checked: #F25C03;
}

@media (max-width: 768px) {
  .filter-wrapper{
    width: calc(100vw - 48px);
    padding: 24px 24px;
    box-shadow: none;
    border-radius: 0;
    top: 0px;
    z-index: 1000;
    height: 100%;
    overflow-x: hidden;
  }
  .filter-main[data-v-60029d04] {
    gap: 20px;
  }
  h4{
    font-size: 28px;
  }
  h5{
    font-size: 20px;
  }
  :deep(.n-checkbox__label){
    font-size: 16px;
  }
  :deep(.n-input-number){
    width: 175px;
  }
  :deep(.n-input-wrapper){
    height: 40px;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  :deep(.n-input){
    --n-font-size: 16px!important;
  }
  .interact-button{
    margin-top: 20px;
    margin-bottom: 50px;
  }
}
</style>
