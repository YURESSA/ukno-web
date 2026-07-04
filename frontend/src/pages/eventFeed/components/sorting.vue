<template>
  <div class="sorting-wrapper">
    <div class="sort-filters">
      <button class="close__button"><img src="/icon/filter/close.svg" alt="Закрыть" @click="emit('close')"></button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useDataStore } from '@/stores/counter';
import BaseButton from '@/components/UI/button/BaseButton.vue';

const store = useDataStore();

const sortByTitle = ref('');
const sortByPrice = ref('');

const emit = defineEmits(['close']);

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

  try {
    await store.GetFilterExcursions(params.toString());
    emit('close');
  } catch (error) {
    console.error('Ошибка при загрузке экскурсий:', error);
  }
}
</script>

<style scoped>
.close__button{
  position: absolute;
  right: 25px;
  top: 20px;
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

.sorting-wrapper{
  position: fixed;
  bottom: -500px;
  opacity: 0;
  width: 100%;
  z-index: 1001;
  transition: all 0.5s ease;
}

.sort-filters {
  display: flex;
  flex-direction: column;
  position: relative;
  gap: 20px;
  padding: 15px;
  background: #fff;
  border-radius: 21px 21px 0 0;
  padding: 30px 24px 38px 24px;
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
