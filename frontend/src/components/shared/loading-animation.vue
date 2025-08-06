<template>
  <div class="loading-wrapper">
    <div class="mill-wrapper">
      <div class="mill"></div>
      <div class="blades"></div>
    </div>
    <h4>Создаём пространство...</h4>
    <div class="top-semicircle"></div>
    <div class="bottom-semicircle"></div>
  </div>
</template>

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
</style>
