<template>
  <div class="result-wrapper">
    <div class="title text-orange">
      <h3>Наше культурное пространство — это</h3>
    </div>
    <!-- <div class="result-list text-l">
      <ul>
        <li>
          <div class="content solo text-orange">
            <p>Выставки</p>
          </div>
        </li>
        <li>
          <div class="content">
            <p>Развитие</p>
          </div>
          <div class="content">
            <p >240 м² возможностей</p>
          </div>
        </li>
        <li>
          <div class="content">
            <p>Сообщество мечтателей</p>
          </div>
          <div class="content">
            <p>Арт-пространство для всех</p>
          </div>
        </li>
        <li>
          <div class="content">
            <p>История с 1978 года</p>
          </div>
          <div class="content">
            <p>Творчество без границ</p>
          </div>
          <div class="content">
            <p>Новое в старом</p>
          </div>
        </li>
        <li>
          <div class="content">
            <p>Мастер-классы будущего</p>
          </div>
          <div class="content">
            <p>Экскурсии в прошлое</p>
          </div>
          <div class="content custom">
            <p>90 м² уюта</p>
          </div>
        </li>
      </ul>
    </div> -->
    <n-carousel
      show-arrow
      :space-between="50"
      style="margin: 50px 0px; height: calc(100% + 50px);"
    >
      <template #arrow="{ prev, next }">
        <div class="custom-arrow">
          <button type="button" class="custom-arrow--left" @click="prev">
            <img src="/icon/weui_arrow-outlined.svg" alt="">
          </button>
          <button type="button" class="custom-arrow--right" @click="next">
            <img src="/icon/weui_arrow-outlined.svg" alt="" style="transform: rotate(180deg);">
          </button>
        </div>
      </template>
      <div class="carousel-item">
        <img
          class="carousel-img"
          src="/public/img/result-test-img.png"
        >
        <div class="content-description">
          <p class="text-standart medium">
            С 2025 года мы открыли новое пространство для молодежных инициатив.
          </p>
        </div>
      </div>
      <div class="carousel-item">
        <img
          class="carousel-img"
          src="/public/img/result-test-img.png"
        >
        <div class="content-description">
          <p class="text-standart medium">
            С 2025 года мы открыли новое пространство для молодежных инициатив.
          </p>
        </div>
      </div>
      <div class="carousel-item">
        <img
          class="carousel-img"
          src="/public/img/result-test-img.png"
        >
        <div class="content-description">
          <p class="text-standart medium">
            С 2025 года мы открыли новое пространство для молодежных инициатив.
          </p>
        </div>
      </div>
      <div class="carousel-item">
        <img
          class="carousel-img"
          src="/public/img/result-test-img.png"
        >
        <div class="content-description">
          <p class="text-standart medium">
            С 2025 года мы открыли новое пространство для молодежных инициатив.
          </p>
        </div>
      </div>
      <!-- <img
        class="carousel-img"
        src="https://naive-ui.oss-cn-beijing.aliyuncs.com/carousel-img/carousel2.jpeg"
      >
      <img
        class="carousel-img"
        src="https://naive-ui.oss-cn-beijing.aliyuncs.com/carousel-img/carousel3.jpeg"
      >
      <img
        class="carousel-img"
        src="https://naive-ui.oss-cn-beijing.aliyuncs.com/carousel-img/carousel4.jpeg"
      > -->
    </n-carousel>
  </div>
</template>

<script setup>
// import eventsBlock from './events-block.vue';
import { ref } from "vue";
import { NCarousel, NIcon } from "naive-ui";
</script>

<style scoped>
.result-wrapper{
  background-color: white;
  border-radius: 38px 38px 0px 0px;
  padding: 80px 50px;
  padding-bottom: 230px;
}

h3{
  text-align: center;
}

ul{
  flex-direction: column;
  align-items: center;
  gap: 30px;
}

li{
  display: flex;
  gap: 10px;
}

.result-list{
  margin-top: 80px;
}

.content{
  display: flex;
  justify-content: center;
  padding: 20px 40px;
  border: 2px solid #333333;
  border-radius: 30px;
}

.solo{
  width: 220px;
}

.text-orange{
  color: #F25C03;
  border-color: #F25C03;
}

.custom{
  width: 280px;
}

.carousel-item{
  min-width: 960px;
  max-width: 1280px;
  position: relative;
  flex: 1;
}

.carousel-img {
  width: 100%;
  /* object-fit: cover; */
  border-radius: 31px;
}

.content-description{
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 22px 35px;
  border-radius: 34px;
  width: 272px;
  backdrop-filter: blur(11.199999809265137px);
  background: rgba(255, 255, 255, 0.65);
  position: absolute;
  bottom: 20px;
  right: 20px;
}

.content-description > p{
  text-align: center;
}

:deep(.n-carousel__dots){
  position: absolute!important;
  transform: translateX(-25%)!important;
  bottom: -30px!important;
  left: 50%!important;
}

:deep(.n-carousel){
  position: relative;
  overflow: visible;
  overflow-x: clip!important;
}

:deep(.n-carousel__dot){
  width: 15px!important;
  height: 15px!important;
  border-radius: 100%!important;
  background-color: #ffd6bd!important;
}

:deep(.n-carousel__dot--active){
  background-color: #f25c03!important;
}

:deep(.n-carousel__slide){
  display: flex;
  justify-content: center;
}

.custom-arrow{
  display: flex;
  justify-content: space-between;
  width: 100%;
  position: absolute;
  top: 50%;
  transform: translateY(-25%);
}

.custom-arrow > button{
  background: none;
}

.custom-arrow > button:hover{
  background: #33333357;
}

.custom-arrow > button:active{
  background: #F25C03;
}
</style>
