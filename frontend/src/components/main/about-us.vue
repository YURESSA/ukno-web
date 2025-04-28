<template>
  <div class="page-wrapper" id="about">
    <div class="title">
      <h3>Молодежное бюро 5 этаж -</h3>
    </div>
    <div class="about-content">
      <div class="content-wrapper">
        <div class="content right-border">
          <p>Пространство для молодежи, креативных <br>
            идей, вдохновения и развития.</p>
        </div>
        <div class="content">
          <p>Мы находимся на территории бывшего <br>
            хлебозавода №6, который работал с 1978 года. <br>
            Сегодня мы сохраняем дух прошлого, создавая <br> новое будущее.</p>
        </div>
      </div>
      <div class="content-wrapper">
        <div class="content">
        </div>
        <div class="content border">
          <p>С 2024 года мы открыли новое <br> пространство для молодежных инициатив, <br> образовательных мероприятий и <br> творческих проектов.</p>
        </div>
        <div class="content">
        </div>
      </div>
    </div>
    <UsResult></UsResult>
  </div>
</template>

<script setup>
import UsResult from './us-result.vue';
</script>

<style scoped>
.page-wrapper{
  background-color: #FFD6BD;
  padding-bottom: 0;
}

.about-content{
  margin-top: 40px;
  margin-bottom: 120px;
}

.content-wrapper{
  display: flex;
  width: 100%;
  border-top: 1px solid white;
  border-bottom: 1px solid white;
}

.content-wrapper > .content{
  display: flex;
  align-items: center;
  text-align: left;
  width: 50%;
  height: 150px;
  padding-left: 30px;
}

.right-border{
  display: flex;
  border-right: 1px solid white ;
}

.border{
  border-right: 1px solid white ;
  border-left: 1px solid white ;
}
</style>
