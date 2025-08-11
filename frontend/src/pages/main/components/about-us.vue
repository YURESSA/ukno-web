<template>
  <div class="page-wrapper" id="about">
    <div class="container text-medium">
      <div class="design-img">
        <!-- <img class="absolut--img left-ear" src="/icon/main/leftEar.png" alt=""> -->
        <!-- <img class="absolut--img bottom-ear" src="/icon/main/bottomEar.png" alt=""> -->
      </div>
      <div class="title">
        <h3>Кто мы такие?</h3>
        <img class="absolut--img flower-big" src="/icon/main/flower-big.png" alt="">
      </div>
      <div class="about-content">
        <div class="content-wrapper">
          <div class="content right-border">
            <p>Пространство для молодежи, креативных <br>
              идей, вдохновения и развития.</p>
          </div>
          <div class="content">
            <img class="absolut--img flower-small" src="/icon/main/flower-small.png" alt="">
            <p>Мы находимся на территории бывшего <br>
              хлебозавода №6, который работал с 1978 года. <br>
              Сегодня мы сохраняем дух прошлого, создавая <br> новое будущее.</p>
          </div>
        </div>
        <div class="content-wrapper">
          <div class="content">
            <!-- <img class="absolut--img mouse" src="/icon/main/mouse.png" alt=""> -->
            <img class="absolut--img ear" src="/icon/main/ear.png" alt="">
          </div>
          <div class="content border">
            <p>С 2024 года мы открыли новое <br> пространство для молодежных инициатив, <br> образовательных мероприятий и <br> творческих проектов.</p>
          </div>
          <div class="content">
            <img class="absolut--img bread" src="/icon/main/bread1.png" alt="">
          </div>
        </div>
      </div>
      <UsResult></UsResult>
    </div>
  </div>
</template>

<script setup>
import UsResult from './us-result.vue';
</script>

<style scoped>
.page-wrapper{
  background-color: #FFD6BD;
  padding-bottom: 0;
  height: calc(100% + 150px);
}

.title{
  position: relative;
}

.absolut--img{
  position: absolute;
}

.ear{
  bottom: -200px;
  right: 0;
  transform: rotate(-30deg) scaleX(-1);

}

.flower-big{
  top: -130px;
  right: 10px;
}

.flower-small{
  bottom: 0px;
  right: 20px;
}

.bread{
  bottom: -250px;
  left: -120px;
}

/* .left-ear{
  z-index: -1;
  left: 0px;
}

.bottom-ear{
  z-index: -1;
  bottom: -230px;
} */

.container{
  margin: 0 auto;
  max-width: 1800px;
}

.about-content{
  margin-top: 40px;
  margin-bottom: 120px;
}

.content-wrapper{
  display: flex;
  width: 100%;
  border-top: 1px solid white;
}

.content-wrapper > .content{
  display: flex;
  align-items: center;
  text-align: left;
  width: 50%;
  height: 220px;
  padding-left: 30px;
  position: relative;
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
