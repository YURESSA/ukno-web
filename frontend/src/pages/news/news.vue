<template>
  <div class="page-wrapper page--margin">
    <div class="news-wrapper" >
      <span><RouterLink to="/">Главная</RouterLink> / Новости</span>
      <news-content/>
    </div>
  </div>
</template>

<script setup>
import NewsContent from './components/newsContent.vue';
import { ref, onMounted } from 'vue';
import { useDataStore } from '@/stores/counter';

const store = useDataStore();
const load = ref(false)

onMounted(async () => {
  try {
    await store.FetchNews();
    setTimeout(() => {
      load.value = true
    }, 1000)
  } catch (error) {
    console.error('Ошибка при загрузке экскурсий:', error);
    alert('Произошла ошибка, попробуйте ещё раз')
  }
});
</script>


<style scoped>
.page-wrapper {
  display: flex;
  flex-direction: column;
  /* align-items: center; */
  position: relative;
  padding-top: 40px;
  min-height: 100vh;
}

span{
  font-family: var(--font-family);
  font-weight: 400;
  font-size: 16px;
  line-height: 150%;
  text-align: center;
  color: #525252;
}

a{
  color: #525252;
}

a:hover{
  color: #333333;
}
</style>
