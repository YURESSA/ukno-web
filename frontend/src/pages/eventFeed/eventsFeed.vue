<template>
  <div class="page-wrapper">
    <div class="feed-wrapper">
      <h3>Подбери <span class="orange">событие</span> на свой вкус</h3>
      <div class="feed-actions">
        <n-input
          v-model:value="searchQuery"
          placeholder="Найти событие"
          round
          clearable
        >
          <template #prefix>
            <n-icon :component="SearchOutline" />
          </template>
        </n-input>
        <div class="feed-setting">
          <div class="sorting">
            <IconButton class="sort--btn" text="По названию"><img src="/icon/downArrow.svg" alt=""></IconButton>
            <IconButton class="sort--btn" text="По цене"><img src="/icon/downArrow.svg" alt=""></IconButton>
          </div>
          <div class="filter">
            <IconButton class="sort--btn" text="Фильрты" @click="openFilter"><img src="/icon/filter/filter.svg" alt=""></IconButton>
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
import { ref, onMounted, computed } from 'vue';
import { NInput, NIcon } from 'naive-ui';
import { SearchOutline } from "@vicons/ionicons5";
import IconButton from '@/components/UI/button/IconButton.vue';
import EventCard from './components/event-card.vue';
import Filter from './components/filter.vue';
import { useDataStore } from '@/stores/counter';

const store = useDataStore();

const searchQuery = ref('');
const filterStatus = ref(false);
const isFilterOpen = ref(false);
const excursions = computed(() => store.getExcursions);
console.log(excursions.value)

onMounted(async () => {
  try {
    await store.FetchExcursions();
  } catch (error) {
    console.error('Ошибка при загрузке экскурсий:', error);
  }
});

function openFilter() {
  const feedWrapper = document.querySelector('.feed-wrapper');
  document.body.style.overflow = 'hidden'
  isFilterOpen.value = true;
  feedWrapper.scrollIntoView({
          behavior: 'smooth',  // Плавная прокрутка
          block: 'start'      // Выравнивание по верхнему краю
        });
}

function closeFilter(){
  document.body.style.overflow = 'auto'
  isFilterOpen.value = false;
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

.page-wrapper::before {
  content: '';
  position: absolute;
  top: -120px;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('/backgroung/eventsFeed.png') no-repeat;
  background-size: 100% auto;
  z-index: -1;
}

.feed-wrapper {
  display: flex;
  flex-direction: column;
  max-width: 1400px;
  position: relative;
}

h3{
  margin-bottom: 30px;
}

.orange{
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
