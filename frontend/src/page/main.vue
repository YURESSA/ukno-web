<template>
  <Header></Header>
  <Welcom/>
  <about-us></about-us>
  <Events/>
  <div class="page-wrapper dark-wrapper">
    <News/>
    <History/>
    <Partner/>
  </div>
  <Footer></Footer>
</template>

<script setup>
import Header from '@/components/header.vue'
import Welcom from '@/components/main/welcom-block.vue';
import AboutUs from '@/components/main/about-us.vue';
import Events from '@/components/main/events-block.vue';
import News from '@/components/main/news-block.vue';
import History from '@/components/main/history-block.vue';
import Partner from '@/components/main/partner.vue';
import Footer from '@/components/footer.vue';
</script>


<style scoped>
.dark-wrapper{
  color: white;
  background-color: #333333;
  background-image: url('/backgroung/news-block.png');
  background-size: cover;
  background-repeat: no-repeat;
  background-position: top -500px right;
}
</style>
