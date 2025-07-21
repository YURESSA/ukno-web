<template>
  <div class="box">
    <div class="box-header">
      <img src="/icon/main/subtract.svg" alt="Subtract icon" class="icon-subtract" />
      <img src="/icon/main/bread.png" alt="Bread icon" class="icon-bread" />
      <img src="/icon/main/fabric.svg" alt="Subtract icon" class="icon-fon" />
      <img src="/icon/main/border.png" alt="Subtract icon" class="icon-border" />
      <div class="main-content">
        <h2 class="box-title">КТО МЫ ТАКИЕ?</h2>

        <div class="content-block">
          <img src="/icon/main/Rectangle.png" alt="Указатель мышки" class="inline-img left" />
          <p>
            Резиденты кластера «Хлебзавод №6» <br />
            вместе с другими участниками проводим <br />
            экскурсии и создаем пространство <br />
            для креативных идей, вдохновения и развития
          </p>
        </div>

        <div class="content-block">
          <p>
            Мы находимся на территории бывшего <br />
            хлебозавода №6, который работал с 1978 года. <br />
            Сегодня мы сохраняем дух прошлого, <br />
            создавая новое будущее
          </p>
          <img src="/icon/main/ear.png" alt="Колос" class="inline-img right" />
        </div>

        <div class="content-block center-block">
          <img src="/icon/main/flower-small.png" alt="Маленький цветок" class="flower-small" />
          <img src="/icon/main/flower-big.png" alt="Большой цветок" class="flower-big" />

          <p>
            С 2025 года мы открыли новое <br />
            пространство для молодежных <br />
            инициатив, образовательных <br />
            мероприятий и творческих проектов
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup></script>

<style scoped>
.box {
  position: relative;
  overflow: visible;
}

.box-header {
  position: relative;
}

.icon-fon {
  position: absolute;
  top: -18vw;
  left: 0;
  width: 100%;
  height: auto;
  z-index: 10;
  pointer-events: none;
}

/* «Subtract» располагается поверх фона, чуть выезжает вверх */
.icon-subtract {
  position: absolute;
  top: -15.9vw; /* отступом вверх выезжает из контейнера */
  left: 7vw; /* относительный отступ слева */
  width: 60%; /* ширина относительно wrapper-а */
  height: auto;
  z-index: 11;
  pointer-events: none;
}

/* Прочие иконки остаются над ними */
.icon-bread {
  position: absolute;
  z-index: 11;
  top: -27.8vw;
  left: 14vw;
  width: 50%;
}

.icon-border {
  position: absolute;
  top: -16.1vw;
  left: 72.7vw;
  z-index: 11;
  width: 25%;
}

.box-title {
  position: absolute;
  font-family: 'C', Helvetica, sans-serif;
  font-size: 78px;
  color: #ff6c36;
  margin-top: 40px;
  text-align: center;
  z-index: 11;
  top: 40px;
  left: 30px;
  bottom: 40px;
}

.main-content {
  position: relative;
  gap: 40px;
}

.content-block {
  display: flex;
  position: relative;
  z-index: 11;
  padding-bottom: 140px;
}

.content-block p {
  font-family: 'Manrope', 'Inter Semi Bold', Helvetica, sans-serif;
  font-size: 20px;
  line-height: 1.4;
}

.box-header > div:nth-of-type(1) {
  padding-top: 220px;
  padding-left: 70px;
}

.content-block p:nth-of-type(1) {
  margin-left: 240px;
  padding-bottom: 140px;
}

.content-block p:nth-of-type(2) {
  margin-left: 130px;
  padding-bottom: 140px;
}

.content-block p:nth-of-type(3) {
  margin-left: 450px;
}

.left {
  position: absolute;
  top: 0;
}

.right {
  position: absolute;
  top: -20vw;
  left: 45vw;
}
</style>
