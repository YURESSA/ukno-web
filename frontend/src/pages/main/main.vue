<template>
  <Welcome />
  <Alert/>
  <about-us :culturalData="culturalSpace"></about-us>
  <Events v-if="!$isMobile()"/>
  <div class="events-mobile page-wrapper" v-if="$isMobile()">
    <div class="title text-orange">
      <h3>Наше культурное пространство — это</h3>
    </div>
    <div class="content">
      <div class="info-mobile-card">

        <div class="card-mobile card-mobile--orange">
          <div class="title">
            <h3>События</h3>
          </div>
          <div class="content">
            <p>Молодёжное бюро представляет культурные мероприятия нового формата — от музыкальных вечеров до театральных перформансов в уникальном пространстве бывшего хлебозавода</p>
          </div>
          <img src="/about-us/icon/mobile-union.svg" class="union-mobile" alt="">
        </div>

        <div class="card-mobile">
          <div class="title">
            <h3>Экскурсии</h3>
          </div>
          <div class="content">
            <p>Молодёжное бюро представляет культурные мероприятия нового формата — от музыкальных вечеров до театральных перформансов в уникальном пространстве бывшего хлебозавода</p>
          </div>
          <img src="/about-us/icon/mobile-wave.svg" class="wave-mobile" alt="">
        </div>

        <div class="card-mobile">
          <div class="title">
            <h3>Выставки </h3>
          </div>
          <div class="content">
            <p>Проекты, объединяющие работы молодых художников, фотографов и digital-авторов в индустриальном интерьере</p>
          </div>
          <img src="/about-us/icon/mobile-flower.svg" class="mobile-flower" alt="">
        </div>

        <div class="card-mobile card-mobile--orange">
          <div class="title">
            <h3>Воркшопы</h3>
          </div>
          <div class="content">
            <p>Практические занятия по творческим направлениям: от графического дизайна до звукозаписи </p>
          </div>
          <img src="/about-us/icon/mobile-leaf.svg" class="leaf-mobile-left" alt="">
          <img src="/about-us/icon/mobile-leaf.svg" class="leaf-mobile-right" alt="">
        </div>

        <div class="card-mobile">
          <div class="title">
            <h3>Лекции</h3>
          </div>
          <div class="content">
            <p>Экспертные выступления о современной культуре, урбанистике и технологиях в рамках открытого лектория на пятой этаже</p>
          </div>
          <img src="/about-us/icon/mobile-circles.svg" class="circle-mobile" alt="">
        </div>

      </div>
      <IconButton @click="router.push('/events')" class="button" text="записаться"><img src="/icon/white-arrow.svg" alt=""></IconButton>
    </div>
  </div>
  <div class="page-wrapper dark-wrapper">
    <News :news="news.news"/>
    <!-- <History/> -->
    <Partner/>
  </div>
  <Contact class="page-wrapper">
    <iframe
    src="https://yandex.ru/map-widget/v1/?um=constructor%3A467ac6eb77e4af971eecb9575ed4f0203a9875b769906a7e184a781db5718a65&amp;source=constructor"
    width="100%"
    height="462"
    frameborder="0"
    class="yand-map"
    ></iframe>
  </Contact>
</template>

<script setup>
import { onMounted, watch, computed  } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useDataStore } from '@/stores/counter';
import Welcome from './components/welcome-block.vue';
import AboutUs from './components/about-us.vue';
import Events from './components/events-block.vue';
import News from './components/news-block.vue';
import History from './components/history-block.vue';
import Partner from './components/partner.vue';
import Contact from '../../components/shared/contact-block.vue';
import Alert from '@/components/UI/alert.vue';
import IconButton from '@/components/UI/button/IconButton.vue';

const router = useRouter();
const route = useRoute();
const store = useDataStore();

const scrollToHash = () => {
  if (route.hash) {
    setTimeout(() => {
      const offset = 100; //отступт от элемента
      const element = document.querySelector(route.hash);
      if (element) {
        window.scrollTo({
          top: element.offsetTop - offset,
          behavior: 'smooth'
        });
      }
    }, 100);
  }
};

const news = computed(() => store.getNews);
const culturalSpace = computed(() => store.getCulturalSpace);

onMounted(async () => {
  scrollToHash
  try {
    await store.FetchNews();
    await store.FetchCulturalSpace();
  } catch (error) {
    console.error('Ошибка при загрузке новостей:', error);
  }
});

watch(() => route.hash, scrollToHash);
</script>


<style scoped>
.dark-wrapper{
  color: white;
  background-color: #333333;
  /* background-image: url('/backgroung/news-block.png'); */
  background-size: cover;
  background-repeat: no-repeat;
  background-position: top -500px right;
  /* padding-bottom: 450px; */
  border-radius: 45px 45px 0 0;
}


@media (max-width: 768px) {
  .yand-map{
    width: 100%;
    height: 242px;
  }
  .dark-wrapper {
    border-radius: 22px;
  }
  .button {
    width: 100%;
    margin-top: 24px;
  }
}

.info-mobile-card{
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin-top: 20px;
}

.card-mobile {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: space-between;
  padding: 24px;
  padding-top: 40px;
  border-radius: 14px;
  gap: 30px;
  border: 2px solid #f25c03;
  overflow: hidden;
}

.card-mobile > .title, .card-mobile > .content{
  z-index: 2;
}

.card-mobile--orange {
  background-color: #FF6C36;
  color: white;
}

.wave-mobile{
  position: absolute;
  top: 0;
  right: 0;
  height: 100%;
  z-index: 1;
}

.union-mobile{
  position: absolute;
  top: 0;
  right: 0;
  height: 100%;
  z-index: 1;
}

.circle-mobile{
  position: absolute;
  top: 0;
  right: 0;
  height: 100%;
  z-index: 1;
}

.leaf-mobile-left {
  position: absolute;
  bottom: 0;
  right: 80px;
  z-index: 1;
}

.leaf-mobile-right {
  position: absolute;
  bottom: 0;
  right: -15px;
  z-index: 1;
  transform: scaleX(-1);
}

.mobile-flower {
  position: absolute;
  top: 0;
  right: 0;
  z-index: 1;
}
</style>
