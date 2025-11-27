<template>
  <div class="filter-wrapper">
    <div class="filter-main">
      <div class="filter-component">
        <h5>Поиск по названию</h5>
        <NInput
          class="inp"
          placeholder="Введите название книги"
          v-model:value="formData.title"
        ></NInput>
      </div>
      <div class="filter-component">
        <h5>Категория</h5>
        <n-checkbox-group v-model:value="formData.category">
          <n-space class="checkbox-group" item-style="display: flex;">
            <n-checkbox size="large" value="Нехудожественная литература">
              Нехудожественная литература
            </n-checkbox>
            <n-checkbox size="large" value="Художественная литература">
              Художественная литература
            </n-checkbox>
            <n-checkbox size="large" value="Бизнес литература">
              Бизнес литература
            </n-checkbox>
            <n-checkbox size="large" value="Детям и родителям">
              Детям и родителям
            </n-checkbox>
            <n-checkbox size="large" value="Учебная литература">
              Учебная литература
            </n-checkbox>
          </n-space>
        </n-checkbox-group>
      </div>
      <div class="filter-component">
        <h5>Автор</h5>
        <NInput
          class="inp"
          placeholder="Поиск по имени автора"
          v-model:value="formData.author"
        ></NInput>
      </div>
      <div class="filter-component">
        <h5>Возрастная категория</h5>
        <n-checkbox-group v-model:value="formData.age_category">
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
      <div class="filter-component">
        <h5>Язык</h5>
        <n-checkbox-group v-model:value="formData.language">
          <n-space class="checkbox-group" item-style="display: flex;">
            <n-checkbox size="large" value="Русский">
              Русский
            </n-checkbox>
            <n-checkbox size="large" value="Английский">
              Английский
            </n-checkbox>
            <n-checkbox size="large" value="Китайский">
              Китайский
            </n-checkbox>
            <n-checkbox size="large" value="Испанский">
              Испанский
            </n-checkbox>
          </n-space>
        </n-checkbox-group>
      </div>
    </div>
    <div class="interact-button">
      <NButton type="primary" @click="sendFilter">Поиск</NButton>
      <NButton @click="resetFilter">Сброс</NButton>
    </div>
  </div>
  <Footer></Footer>
</template>

<script setup>
import { ref } from 'vue'
import { NCheckbox, NCheckboxGroup, NSpace, NInput, NButton } from 'naive-ui'
import { useDataStore } from '@/stores/counter';
import Footer from '@/components/shared/footer.vue';

const store = useDataStore();


const formData = ref({
  title: '',
  author: '',
  category: [],
  age_category: [],
  language: [],

});


const sendFilter = async () => {
  try {
    const queryString = buildQueryString(formData.value);
    console.log('Параметры поиска:', queryString);

    await store.GetFilterBooks(queryString);
  } catch (error) {
    console.error('Ошибка при загрузке книг:', error);
  }
}

// Функция для сброса фильтра
const resetFilter = () => {
  formData.value = {
    title: '',
    author: '',
    category: [],
    age_category: [],
    language: [],
  };
  console.log('Фильтр сброшен');
}

// Функция для построения query string
function buildQueryString(data) {
  const params = new URLSearchParams();

  for (const [key, value] of Object.entries(data)) {
    if (value === null || value === undefined || value === '') continue;

    if (Array.isArray(value)) {
      if (value.length > 0) {
        params.append(key, value.join(','));
      }
    } else {
      params.append(key, value.toString());
    }
  }

  return params.toString();
}

// Для отладки - можно посмотреть formData в консоли
// watch(formData, (newVal) => {
//   console.log('formData обновлен:', newVal);
// }, { deep: true });
</script>


<style scoped>
.filter-wrapper{
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  max-width: 450px;
  box-shadow: 0px 4px 13px 0px #00000040;
  overflow-y: scroll;
  scrollbar-width: none;
  transition: all 0.5s ease;
  margin-bottom: 90px;
  padding: 15px 15px;;
}

.inp {
  flex: 1;
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
  gap: 15px;
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


.checkbox-group{
  flex-direction: column!important;
  gap: 10px!important;
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

h5 {
  font-size: 16px;
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
  justify-content: center;
  gap: 10px;
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
  font-size: 12px;
}

:deep(.n-checkbox__label){
  font-weight: 600;
  font-size: 14px;
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
  height: 40px;
  width: 100%;
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
  --n-font-size: 14px!important;
  transition: all 0.25s ease;
}

:deep(.n-input__input-el){
  font-weight: 600;
  text-align: center;
}

:deep(.n-checkbox-box){
  --n-color-checked: #F25C03;
}
</style>
