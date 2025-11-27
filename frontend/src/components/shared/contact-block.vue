<template>
    <div class="contact-wrapper">
      <div class="contact-container" id="contact">
        <h3>Контакты</h3>
        <p>Улица 8 Марта, 203, Екатеринбург, Свердловская область, 620085</p>
        <p>Режим работы: ежедневно с 10:00 до 21:00</p>
        <p>E-mail: mb@mail.ru</p>
        <p><a href="tel:+79905679522"></a>+7(990)567-95-22</p>
        <ul>
            <li><a href="tel:+79905679522"><img src="/icon/header/phone.svg" alt=""></a></li>
            <li><a href=""><img src="/icon/header/vk.svg" alt=""></a></li>
            <li><a href=""><img src="/icon/header/tg.svg" alt=""></a></li>
          </ul>
        <div class="map">
          <slot class="yand-map"></slot>
          <div class="info">
            <h4>Загляните к нам!</h4>
            <div class="info-block">
              <img src="/icon/footer/city.svg" alt="">
              <div class="text">
                <h3 class="green">6 км</h3>
                <p>от центра города</p>
              </div>
            </div>
            <div class="info-block">
              <img src="/icon/footer/bus.svg" alt="">
              <div class="text">
                <h3 class="violet">7 мин</h3>
                <p>от  ближайшей остановки</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
</template>

<script setup>

</script>

<style scoped>
.contact-wrapper{
  max-width: 1800px;
  margin: 0 auto;
}

h3{
  margin-bottom: 10px;
}

h4{
  margin-bottom: 5px;
}

.contact-container{
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 30px;
  width: 100%;

  padding: 70px;
  border-radius: 38px;
  background-color: white;
}

.yand-map{
  border-radius: 38px;
}

.map{
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 100px;
}

.info{
  display: flex;
  flex-direction: column;
  gap: 45px;
}

.info-block{
  display: flex;
  gap: 20px;
}

.green{
  color: #79A800;
}

.violet{
  color: #46278D;
}
</style>
