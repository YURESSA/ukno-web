<template>
  <div class="loading-wrapper">
    <div class="mill-wrapper">
      <div class="mill"></div>
      <div class="blades"></div>
    </div>
    <h4>{{ text }}</h4>
  </div>
</template>

<script setup>
  defineProps({
    text: Text
  })
</script>

<style scoped>
.loading-wrapper{
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

.mill-wrapper{
  content: '';
  height: 170px;
  width: 170px;
  position: relative;
}

.mill{
  content: '';
  width: 170px;
  height: 170px;
  background-image: url('/loading/mill.svg');
  position: absolute;
  background-repeat: no-repeat;
}

@keyframes spin-clockwise {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.blades{
  content: '';
  width: 170px;
  height: 170px;
  background-image: url('/loading/blades.svg');
  position: absolute;
  top: -50px;
  left: -3px;
  will-change: transform;
  animation: spin-clockwise 2.5s linear infinite;
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
}
</style>
