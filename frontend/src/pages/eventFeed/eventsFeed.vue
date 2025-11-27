<template>
  <div class="page-wrapper page--margin">
    <div class="feed-wrapper">
      <h3>Подбери <span class="text-orange">событие</span> на свой вкус</h3>
      <div class="feed-actions">
        <n-input
          v-model:value="searchQuery"
          placeholder="Найти событие"
          round
          clearable
          @keydown.enter="sendSearch"
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
          <div class="filter">
            <IconButton class="sort--btn" text="Фильтры" @click="openFilter"><img src="/icon/filter/filter.svg" alt=""></IconButton>
          </div>
        </div>
      </div>
      <div class="feed">
        <div class="event-count">
          <p v-if="excursions.length">{{ excursions.length }} предложения</p>
        </div>
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
    @close="closeFilter"/>
  </div>
  <div class="filter-open-wrapper" v-if="isFilterOpen" @click="closeFilter"></div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { NInput, NIcon } from 'naive-ui';
import { SearchOutline } from "@vicons/ionicons5";
import { storeToRefs } from 'pinia';
import IconButton from '@/components/UI/button/IconButton.vue';
import DropDown from '@/components/UI/dropDown/dropDown.vue';
import EventCard from './components/event-card.vue';
import Filter from './components/filter.vue';
import { useDataStore } from '@/stores/counter';

const store = useDataStore();

const searchQuery = ref('');
const sortByTitle = ref('');
const sortByPrice = ref('');
const filterStatus = ref(false);
const isFilterOpen = ref(false);
const { excursions } = storeToRefs(store);
console.log(excursions.value)

// Отслеживаем изменения excursions
watch(excursions, (newVal) => {
  console.log('Экскурсии обновились:', newVal);
}, { deep: true });

onMounted(async () => {
  try {
    await store.FetchExcursions();
  } catch (error) {
    console.error('Ошибка при загрузке экскурсий:', error);
  }
});

function openFilter() {
  document.body.style.overflow = 'hidden'
  isFilterOpen.value = true;
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  });
}

function closeFilter(){
  document.body.style.overflow = 'auto'
  isFilterOpen.value = false;
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
</style>
