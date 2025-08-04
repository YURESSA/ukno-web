<template>
  <div class="welcom-wrapper page--margin">
    <div class="welcom-img"></div>
    <h1 class="text-orange">Молодежное бюро</h1>
    <p class="text-grey">Культурно-образовательный центр, где <br>
      история встречает современность, а творчество  <br>
      и  саморазвитие вдохновляют</p>
      <div class="sprout"></div>
      <div class="ear"></div>
  </div>
</template>

<script setup>

</script>

<style scoped>
.welcom-wrapper{
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
  margin-top: 180px!important;
  position: relative;
  overflow: hidden;
}

.sprout{
  content: '';
  width: 240px;
  height: 360px;
  background-image: url('/icon/main/sprout.png');
  position: absolute;
  left: -55px;
  bottom: 40px;
  background-position: center;
}

.ear{
  content: '';
  width: 270px;
  height: 320px;
  background-image: url('/icon/main/welcom-ear.png');
  position: absolute;
  right: -80px;
  bottom: -10px;
  background-position: center;
  background-repeat: no-repeat;
}

h2{
  text-align: center;
}

p{
  font-size: 24px;
  text-align: center;
}

.welcom-img{
  content: '';
  width: 80%;
  height: 475px;
  border-radius: 48px;
  background-image: url('/img/welcom.png');
  background-repeat: no-repeat;
  background-size: cover; /* Заполняет весь контейнер, сохраняя пропорции */
  background-position: center; /* Центрирует изображение */
  z-index: 10;
  /* max-width: 1035px; */
}

</style>
