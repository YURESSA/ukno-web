<template>
  <s-header />
  <div class="page--margin login-layout">
    <div class="icon-wrapper">
      <div class="piano"></div>
      <div class="flower"></div>
    </div>
    <router-view />
    <div class="sprout"></div>
    <div class="geometric-flower"></div>
  </div>
  <s-footer />
</template>

<script setup>
import { SHeader, SFooter } from '@shared';
</script>

<style scoped>
.login-layout{
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  height: calc(100vh - 186px);
  min-height: 900px;
  max-height: 1000px;
  overflow: hidden;
}

.icon-wrapper{
  position: absolute;
  width: 688px;
  height: 510px;
  max-width: 1280px;
  top: 50%;
  transform: translateY(-60%);
}

.sprout{
  content: '';
  width: 240px;
  height: 360px;
  background-image: url('/icon/login/sprout.svg');
  position: absolute;
  left: -75px;
  top: -10px;
  background-position: center;
}

.flower{
  content: '';
  width: 435px;
  height: 435px;
  background-image: url('/icon/login/flower.svg');
  position: absolute;
  left: -280px;
  bottom: -200px;
  background-position: center;
  z-index: 90;
}

.piano{
  content: '';
  width: 435px;
  height: 435px;
  background-image: url('/icon/login/piano.svg');
  position: absolute;
  right: -267px;
  top: -100px;
  background-position: center;
}

.geometric-flower{
  content: '';
  width: 300px;
  height: 300px;
  background-image: url('/icon/login/geometric-flower.svg');
  position: absolute;
  right: -50px;
  bottom: 190px;
  background-position: center;
}
</style>
