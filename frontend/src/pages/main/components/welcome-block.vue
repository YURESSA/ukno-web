<template>
  <div class="welcom-wrapper page--margin">
    <div class="welcom-img"></div>
    <h1 class="text-orange">Молодежное бюро <span v-if="$isMobile()">5 этаж</span></h1>
    <p class="text-grey">Культурно-образовательный центр, где <br>
      история встречает современность, а творчество  <br>
      и  саморазвитие вдохновляют</p>
      <div class="sprout" v-if="!$isMobile()"></div>
      <div class="ear" v-if="!$isMobile()"></div>
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
  z-index: -1;
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
  z-index: -1;
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
  background-size: cover;
  background-position: center;
  z-index: 10;
  /* max-width: 1035px; */
}

@media (max-width: 768px) {
  h2{
  order: 1;
  }
  p{
    order: 2;
    text-align: left;
    color: #333333;
  }
  .welcom-img {
    order: 3;
    width: 100%;
    height: 232px;
    border-radius: 12px;
    background-size: cover;
    background-position: center bottom; /* Фокус на нижней части */
    background-repeat: no-repeat;
  }
  .welcom-wrapper{
    margin-top: 36px!important;
    padding: 0 24px;
  }
}

</style>
