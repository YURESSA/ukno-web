<template>
  <div class="not-found-wrapper">
    <div class="not-found-img">
      <img src="/NotFound.png" alt="">
    </div>
    <h2>404</h2>
    <h4>{{ description }}</h4>
    <BaseButton class="to-main--bth" :text="actionLabel" @click="router.push(to)"/>
    <div class="top-semicircle"></div>
    <div class="bottom-semicircle"></div>
  </div>
</template>

<script setup>
import { inject, onMounted, onUnmounted } from 'vue';
import router from '@/router';
import BaseButton from '../ui/button/BaseButton.vue';

defineProps({
  description: { type: String, default: 'такой страницы не существует' },
  actionLabel: { type: String, default: 'На главную' },
  to: { type: String, default: '/' },
});

const setMainHeaderAndFooterHidden = inject('set-main-header-and-footer-hidden', null);

if (setMainHeaderAndFooterHidden) {
  onMounted(() => setMainHeaderAndFooterHidden(true));
  onUnmounted(() => setMainHeaderAndFooterHidden(false));
}
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

.not-found-wrapper > h2,
.not-found-wrapper > h4,
.not-found-img,
.to-main--bth {
  z-index: 1;
}

h4 {
  text-align: center;
  padding-inline: 16px;
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
