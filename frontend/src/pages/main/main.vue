<template>
  <Welcome />
  <about-us></about-us>
  <!-- <Events/>  компонент событий (нет финальной версии) -->
  <div class="page-wrapper dark-wrapper">
    <News/>
    <History/>
    <Partner/>
  </div>
  <Contact class="map">
    <iframe
    src="https://yandex.ru/map-widget/v1/?um=constructor%3A467ac6eb77e4af971eecb9575ed4f0203a9875b769906a7e184a781db5718a65&amp;source=constructor"
    width="629"
    height="462"
    frameborder="0"
    class="yand-map"
    ></iframe>
  </Contact>
</template>

<script setup>
import { onMounted, watch  } from 'vue';
import { useRoute } from 'vue-router';
import Welcome from './components/welcome-block.vue';
import AboutUs from './components/about-us.vue';
// import Events from './components/events-block.vue';
import News from './components/news-block.vue';
import History from './components/history-block.vue';
import Partner from './components/partner.vue';
import Contact from '../../components/shared/contact-block.vue';

const route = useRoute();

const scrollToHash = () => {
  if (route.hash) {
    setTimeout(() => {
      const offset = 0; //отступт от элемента
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

onMounted(scrollToHash);

watch(() => route.hash, scrollToHash);
</script>


<style scoped>
.dark-wrapper{
  color: white;
  background-color: #333333;
  background-image: url('/backgroung/news-block.png');
  background-size: cover;
  background-repeat: no-repeat;
  background-position: top -500px right;
  padding-bottom: 450px;
}

.map{
  margin-top: -400px;
}
</style>
