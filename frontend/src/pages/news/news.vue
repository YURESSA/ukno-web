<template>
  <div class="page-wrapper page--margin" v-if="load">
    <div class="news-wrapper">
      <span><RouterLink to="/">Главная</RouterLink> / Новости</span>
      <news-content
        v-for="(news, i) in news.news"
        :key="i"
        :news="news"
      />
    </div>
    <div class="img-wrapper top-right-asterisk"></div>
    <div class="img-wrapper bottom-right-asterisk"></div>
    <div class="img-wrapper top-left-asterisk"></div>
    <div class="img-wrapper bottom-left-asterisk"></div>
  </div>
  <LoadingAnimation v-else/>
</template>

<script setup>
import NewsContent from './components/newsContent.vue';
import { ref, onMounted, computed, watch, nextTick } from 'vue';
import { useDataStore } from '@/stores/counter';
import { useRoute } from 'vue-router';
import LoadingAnimation from '@/components/shared/loading-animation.vue';

const store = useDataStore();
const load = ref(false);
const route = useRoute();
const news = computed(() => store.getNews);

const scrollToNews = (attempt = 0) => {
  if (!route.hash || attempt > 3) return;

  nextTick(() => {
    const element = document.querySelector(route.hash);
    if (element) {
      const offset = 140;
      const elementPosition = element.getBoundingClientRect().top + window.scrollY;

      window.scrollTo({
        top: elementPosition - offset,
        behavior: 'smooth'
      });
    } else {
      setTimeout(() => scrollToNews(attempt + 1), 300);
    }
  });
};

onMounted(async () => {
  document.body.classList.add('body-no-scroll');
  try {
    await store.FetchNews();

    nextTick(() => {
      setTimeout(() => {
        load.value = true
        document.body.classList.remove('body-no-scroll');
      }, 1000)

      scrollToNews();

      setTimeout(scrollToNews, 500);
    });
  } catch (error) {
    console.error('Ошибка при загрузке новостей:', error);
    document.body.classList.remove('body-no-scroll');
  }
});

watch(() => route.hash, () => {
  if (load.value) scrollToNews();
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
  overflow: hidden;
}

.img-wrapper{
  display: inline;
  position: absolute;
  content: '';
  width: 355px;
  height: 343px;
  background-image: url(/icon/news/asterisk.svg);
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
  color: #525252;
}

a{
  color: #525252;
}

a:hover{
  color: #333333;
}

@media (max-width: 768px) {
  .header-wrapper[data-v-d588c1b3] {
    width: calc(100vw - 48px);
    position: relative;
    padding: 56px 24px 20px 24px;
    margin-bottom: 20px;
  }
  .page-wrapper{
    padding-top: 0px;
  }
  .img-wrapper{
    width: 188px;
    height: 182px;
    background-size: 100%;
  }
  .top-right-asterisk{
    top: 0px;
    right: -75px;
  }

  .top-left-asterisk{
    top: 300px;
    left: -75px;
  }

  .bottom-right-asterisk{
    top: 650px;
    right: -75px;
    transform: rotate(-16deg);
  }

  .bottom-left-asterisk{
    top: 1066px;
    left: -75px;
    transform: rotate(-16deg);
  }
}
</style>
