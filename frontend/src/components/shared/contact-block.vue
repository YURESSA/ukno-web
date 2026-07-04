<template>
    <div class="contact-wrapper">
      <div class="contact-container" id="contact">
        <h3>Контакты</h3>
        <p>Улица 8 Марта, 203, Екатеринбург, Свердловская область, 620085</p>
        <p>Режим работы: ежедневно с 10:00 до 21:00</p>
        <p>E-mail: bureau@ukno.ru</p>
        <p><a href="tel:+79905679522"></a>+7(990)567-95-22</p>
        <ul>
            <li><a href="tel:+79905679522"><img src="/icon/header/phone.svg" alt=""></a></li>
            <li><a href=""><img src="/icon/header/vk.svg" alt=""></a></li>
            <li><a href=""><img src="/icon/header/tg.svg" alt=""></a></li>
        </ul>
        <div class="map">
          <div class="map-radius">
            <slot class="yand-map"></slot>
          </div>
          <div class="info">
            <h4 v-if="!$isMobile()">Загляните к нам!</h4>
            <div class="info-block">
              <img src="/icon/footer/city.svg" alt="">
              <div class="text">
                <h3 class="green">15 минут</h3>
                <p>от метро Ботаническая</p>
              </div>
            </div>
            <div class="info-block">
              <img src="/icon/footer/bus.svg" alt="">
              <div class="text">
                <h3 class="violet">3 минуты</h3>
                <p>от ближайшей остановки  </p>
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
  background-color: white;
}

.map-radius{
  width: 100%;
  max-width: 1000px;
  border-radius: 40px;
  overflow: hidden;
}

.map{
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 70px;
}

.info{
  display: flex;
  flex-direction: column;
  gap: 45px;
  min-width: max-content;
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

@media (max-width: 768px) {
  .contact-container{
    gap: 20px;
  }
  h3{
    margin-bottom: 6px;
  }
  li img{
    width: 26px;
    height: 26px;
  }
  .map{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 20px;
  }
  .map-radius{
    width: 100%;
    border-radius: 40px;
    overflow: hidden;
  }
}
</style>
