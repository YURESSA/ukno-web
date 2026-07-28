<template>
  <div class="not-found-wrapper">
    <div class="not-found-img">
      <img src="/NotFound.png" alt="">
    </div>
    <h2>404</h2>
    <h4>такой страницы не существует</h4>
    <BaseButton class="to-main--bth" text="На главную" @click="router.push('/')"/>
    <div class="top-semicircle"></div>
    <div class="bottom-semicircle"></div>
  </div>
</template>

<script setup>
import router from '@/router';
import BaseButton from '../UI/button/BaseButton.vue';

</script>

<style scoped>
.not-found-wrapper{
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 100vw;
  height: 100vh;
  position: relative;
  overflow: hidden;
  background-color: white;
  z-index: 999;
}

.loading-wrapper > h2, .loading-wrapper > h4 {
  z-index: 99;
}

.to-main--bth {
  margin-top: 25px;
}

.top-semicircle{
  content: '';
  width: 676px;
  height: 340px;
  background-image: url('/loading/semicircles.svg');
  position: absolute;
  top: 0px;
  right: -20px;
  background-repeat: no-repeat;
}

.bottom-semicircle{
  content: '';
  width: 676px;
  height: 340px;
  background-image: url('/loading/semicircles.svg');
  position: absolute;
  bottom: 0px;
  left: -20px;
  transform: rotate(180deg);
  background-repeat: no-repeat;
}

@media (max-width: 768px) {
  .loading-wrapper{
    position: fixed;
    top: 0;
  }

  h4{
    font-size: 28px;
    text-align: center;
  }
  .top-semicircle{
    width: 338px;
    height: 170px;
    background-size: 100% 100%;
    top: 0px;
  }

  .bottom-semicircle{
    content: '';
    width: 338px;
    height: 170px;
    background-image: url('/loading/semicircles.svg');
    background-size: 100% 100%;
    background-position: center;
    position: absolute;
    bottom: 0px;
    left: -10px;
    transform: rotate(180deg);
    background-repeat: no-repeat;
  }
  .to-main--bth {
    font-size: 16px;
  }
}
</style>
