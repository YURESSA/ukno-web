<template>
  <div class="page-wrapper page--margin">
    <div class="feed-wrapper" v-if="excursions">
      <h3>Подбери <span class="text-orange">событие</span> на свой вкус</h3>
      <div class="feed-actions">
        <n-input
          v-model:value="searchQuery"
          placeholder="Найти событие"
          round
          clearable
          @keydown.enter="sendSearch"
          class="search"
        >
          <template #prefix>
            <n-icon :component="SearchOutline" />
          </template>
        </n-input>
        <div class="feed-setting">
          <div class="sorting">
            <DropDown
              v-model="sortByTitle"
              :options="[
                { label: 'От А до Я', value: 'title' },
                { label: 'От Я до А', value: '-title' }
              ]"
              title="По названию"
              name="sort-by-name"
              @update:modelValue="handleTitleSortChange"
            />
            <DropDown
              v-model="sortByPrice"
              :options="[
                { label: 'По возрастанию', value: 'price' },
                { label: 'По убыванию', value: '-price' },
              ]"
              title="По цене"
              name="sort-by-price"
              @update:modelValue="handleTitleSortChange"
            />
          </div>
          <div class="sorting-mobile">
            <IconButton class="sort--btn" @click="openSorting"><img src="/icon/filter/sorting.svg" alt=""></IconButton>
          </div>
          <div class="filter">
            <IconButton class="sort--btn" text="Фильтры" @click="openFilter"><img src="/icon/filter/filter.svg" alt=""></IconButton>
          </div>
        </div>
      </div>
      <div class="feed">
        <!-- <div class="event-count">
          <p v-if="excursions.excursions.length">{{ excursions.excursions.length }} предложения</p>
        </div> -->
        <div class="events">
          <EventCard
            v-for="(excursion, i) in excursions['excursions']"
            :key="i"
            :excursion="excursion"
          />
        </div>
      </div>
    </div>
    <Filter
    :class="{ 'filter-open': isFilterOpen }"
    @close="closeAll"/>
    <!-- <Sorting
    :class="{ 'sorting-open': isSortingOpen }"
    @close="closeAll"/> -->
    <DropMenu
    :class="{ 'drop-open': isSortingOpen }"
    @close="closeAll">
      <!-- Сортировка по цене -->
      <div class="sort-group">
        <h3 class="sort-title">Цена</h3>
        <div class="radio-group">
          <label class="radio-label">
            <input
              type="radio"
              name="priceSort"
              value="price"
              v-model="sortByPrice"
              class="radio-input"
            >
            <span class="radio-custom"></span>
            <span class="radio-text">По возрастанию</span>
          </label>
          <label class="radio-label">
            <input
              type="radio"
              name="priceSort"
              value="-price"
              v-model="sortByPrice"
              class="radio-input"
            >
            <span class="radio-custom"></span>
            <span class="radio-text">По убыванию</span>
          </label>
        </div>
      </div>
      <!-- Сортировка по названию -->
      <div class="sort-group">
        <h3 class="sort-title">Название</h3>
        <div class="radio-group">
          <label class="radio-label">
            <input
              type="radio"
              name="titleSort"
              value="title"
              v-model="sortByTitle"
              class="radio-input"
            >
            <span class="radio-custom"></span>
            <span class="radio-text">От А до Я</span>
          </label>
          <label class="radio-label">
            <input
              type="radio"
              name="titleSort"
              value="-title"
              v-model="sortByTitle"
              class="radio-input"
            >
            <span class="radio-custom"></span>
            <span class="radio-text">От Я до А</span>
          </label>
        </div>
      </div>
      <BaseButton class="sendButton" text="Сохранить" @click="sendSort"/>
    </DropMenu>
  </div>
  <div class="filter-open-wrapper" v-if="isFilterOpen || isSortingOpen" @click="closeAll"></div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { NInput, NIcon } from 'naive-ui';
import { SearchOutline } from "@vicons/ionicons5";
import IconButton from '@/components/UI/button/IconButton.vue';
import DropDown from '@/components/UI/dropDown/dropDown.vue';
import BaseButton from '@/components/UI/button/BaseButton.vue';
import EventCard from './components/event-card.vue';
import Filter from './components/filter.vue';
import Sorting from './components/sorting.vue';
import { useDataStore } from '@/stores/counter';
import DropMenu from '@/components/shared/dropMenu.vue';

const store = useDataStore();

const searchQuery = ref('');
const sortByTitle = ref('');
const sortByPrice = ref('');
const isFilterOpen = ref(false);
const isSortingOpen = ref(false);
// const { excursions } = storeToRefs(store);
const excursions = computed(() => store.getExcursions )
console.log(excursions.value)



onMounted(async () => {
  try {
    await store.FetchExcursions();
  } catch (error) {
    console.error('Ошибка при загрузке экскурсий:', error);
  }
});

function openFilter() {
  document.body.classList.add('body-no-scroll');
  isFilterOpen.value = true;
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  });
}

function openSorting(){
  document.body.classList.add('body-no-scroll');
  isSortingOpen.value = true;
}

function closeAll(){
  document.body.classList.remove('body-no-scroll');
  isFilterOpen.value = false;
  isSortingOpen.value = false;
}

const handleTitleSortChange = (value) => {
  console.log('Выбрана сортировка:', value);
  sendSort();
};

const sendSort = async () => {
  const params = new URLSearchParams();
  const sortValues = [];

  if (sortByPrice.value) {
    sortValues.push(sortByPrice.value);
  }

  if (sortByTitle.value) {
    sortValues.push(sortByTitle.value);
  }

  if (sortValues.length > 0) {
    params.append('sort', sortValues.join(','));
  }
  console.log(sortValues)
  try {
    await store.GetFilterExcursions(params.toString());
  } catch (error) {
    console.error('Ошибка при загрузке экскурсий:', error);
  }
}

const sendSearch = async () => {
  const params = new URLSearchParams();
  params.append('title', searchQuery.value);
  const queryString = params.toString();
  try {
    await store.GetFilterExcursions(queryString);
  } catch (error) {
    console.error('Ошибка при загрузке экскурсий:', error);
  }
}
</script>


<style scoped>
.page-wrapper {
  display: flex;
  justify-content: center;
  position: relative;
  /* min-height: 100vh; */
  padding-top: 40px;
}

.filter-open {
  right: 0;
}

.drop-open{
  bottom: 0;
  opacity: 1;
}

.sort--btn{
  background: none;
  border: 1px solid #E2E2E2;
  color: #333;
}

.sort--btn:hover{
  background-color: rgb(202, 202, 202);
}

.sort--btn:active{
  background-color: rgb(230, 230, 230);
}

.filter-open-wrapper{
  display: block;
  content: '';
  width: 100%;
  height: 100vh;
  position: fixed;
  top: 0;
  overflow: hidden;
  background-color: rgba(128, 128, 128, 0.459);
  z-index: 99;
}

.feed-wrapper {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 1400px;
  position: relative;
}

h3{
  margin-bottom: 30px;
}

.text-orange{
  color: #F25C03;
}

.feed-setting{
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.sorting{
  display: flex;
  gap: 20px;
}

:deep(.sort--btn > .slot-content){
  display: flex;
  align-items: center;
  margin-left: 15px;
}

.feed{
  display: flex;
  flex-direction: column;
  gap: 30px;
  margin-top: 30px;
}

.events{
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-start;
  gap: 20px;
}

.event-count{
  font-size: 20px;
  font-weight: 700;
}

@media (min-width: 768px) {
  .sorting-mobile{
    display: none;
  }
}

@media (max-width: 768px) {
  .feed-actions{
    display: flex;
    align-items: center;
    flex-direction: row;
    gap: 5px;
  }
  .feed-setting{
    margin: 0;
  }
  .feed{
    margin-top: 20px;
  }
  .sorting{
    display: none;
  }
  .sort--btn{
    padding: 11px 9px;
  }
  :deep(.sort--btn span){
    display: none;
  }
  :deep(.sort--btn .slot-content){
    margin: 0;
  }
  .search, .sort--btn{
    height: 37px;
  }
  .event-count{
    display: none;
  }
  .sort--btn{
    background: none;
    border: 1px solid #E2E2E2;
  }
  .filter-open-wrapper{
    z-index: 1000;
  }
}




.sort-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.sort-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.radio-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 5px 0;
  user-select: none;
}

.radio-input {
  display: none;
}

.radio-custom {
  width: 18px;
  height: 18px;
  border: 2px solid #ddd;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.radio-custom::after {
  content: '';
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #F25C03;
  opacity: 0;
  transition: opacity 0.2s;
}

.radio-input:checked + .radio-custom {
  border-color: #F25C03;
}

.radio-input:checked + .radio-custom::after {
  opacity: 1;
}

.radio-text {
  font-size: 14px;
  color: #555;
}

.radio-label:hover .radio-custom {
  border-color: #F25C03;
}

.radio-label:hover .radio-text {
  color: #333;
}

.sendButton{
  font-size: 16px;
}
</style>
