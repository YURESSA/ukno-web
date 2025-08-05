<template>
  <div class="page-wrapper page--margin">
    <div class="news-wrapper" v-if="load">
      <span><RouterLink to="/">Главная</RouterLink> / Новости</span>
      <news-content
        v-for="(news, i) in news.news"
        :key="i"
        :news="news"
      />
    </div>
    <h3 v-else>Загрузка данных...</h3>
    <div class="img-wrapper top-right-asterisk"></div>
    <div class="img-wrapper bottom-right-asterisk"></div>
    <div class="img-wrapper top-left-asterisk"></div>
    <div class="img-wrapper bottom-left-asterisk"></div>
  </div>
</template>

<script setup>
import NewsContent from './components/newsContent.vue';
import { ref, onMounted, computed  } from 'vue';
import { useDataStore } from '@/stores/counter';

const store = useDataStore();
const load = ref(false)

const news = computed(() => store.getNews);

onMounted(async () => {
  try {
    await store.FetchNews();
    setTimeout(() => {
      load.value = true
    }, 1000)
  } catch (error) {
    console.error('Ошибка при загрузке новостей:', error);
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
  position: relative;
  overflow-x: hidden;
}

.img-wrapper{
  display: inline;
  position: absolute;
  content: '';
  width: 355px;
  height: 343px;
  background-image: url(/public/icon/news/asterisk.svg);
  z-index: -1;
}

.top-right-asterisk{
  top: 0px;
  right: -145px;
}

.top-left-asterisk{
  top: 300px;
  left: -145px;
}

.bottom-right-asterisk{
  top: 650px;
  right: -145px;
  transform: rotate(-16deg);
}

.bottom-left-asterisk{
  top: 1066px;
  left: -145px;
  transform: rotate(-16deg);
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
