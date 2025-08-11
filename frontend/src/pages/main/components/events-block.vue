<template>
  <div class="page-wrapper" id="events">
    <div class="container">
      <div class="events-list">
        <div class="four-event">
          <div class="event-type">
            <div class="title">
              <h3>События</h3>
            </div>
            <div class="event-content">
              <p>Молодёжное бюро представляет культурные мероприятия нового формата — от музыкальных вечеров до театральных перформансов в уникальном пространстве бывшего хлебозавода</p>
            </div>
          </div>
          <div class="event-type border-left">
            <div class="title">
              <h3>Экскурсии</h3>
            </div>
            <div class="event-content">
              <p>Авторские маршруты по промышленным локациям и скрытым достопримечательностям города с акцентом на историю и современное искусство</p>
            </div>
          </div>
          <div class="event-type border-top">
            <div class="title">
              <h3>Выставки</h3>
            </div>
            <div class="event-content">
              <p>Проекты, объединяющие работы молодых художников, фотографов и digital-авторов в индустриальном интерьере</p>
            </div>
          </div>
          <div class="event-type orange-block">
            <div class="title">
              <h3>Воркшопы</h3>
            </div>
            <div class="event-content">
              <p>Практические занятия по творческим направлениям: от графического дизайна до звукозаписи </p>
            </div>
          </div>
        </div>
        <div class="event-wrapper">
          <div class="one-event">
            <div class="title">
              <h3>Лекции</h3>
              <p class="bold">
                Говорят те, кто создает <br> будущее
              </p>
            </div>
            <div class="event-content">
              Экспертные выступления о современной культуре, урбанистике и технологиях в рамках открытого лектория на пятой этаже
            </div>
          </div>
        </div>
      </div>
    </div>
    <IconButton @click="router.push('/events')" class="button" text="записаться"><img src="/icon/arrow.svg" alt=""></IconButton>
  </div>
</template>

<script setup>
import IconButton from '@/components/UI/button/IconButton.vue';
import { useRouter } from 'vue-router';

const router = useRouter();
</script>

<style scoped>
.page-wrapper{
  padding: 0 30px;
  /* width: 100%; */
  margin: 0 auto;
  margin-top: -150px;
  max-width: 1800px;
  padding: 0px 30px;
}

span{
  color: #F25C03;
}

.button{
  width: 100%;
  height: 53px;
  background-color: #ff6c36;
  color: white;
  margin-bottom: 65px;
  border: none;
}

.button * img{
  filter: invert(1) brightness(1.5);
}

h3{
  font-weight: 500;
}

.container{
  max-width: 1800px;
  border: 2px solid #F25C03;
  border-radius: 14px;
  margin-bottom: 30px;
}

.events-list{
  display: flex;
}

.four-event{
  display: flex;
  flex-wrap: wrap;
  width: 66%;
}

.event-type{
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  width: calc(50% - 51px);
  height: 310px;
  padding: 30px 20px 30px 30px;
}

.one-event{
  display: flex;
  height: calc(100% - 55px);
  flex-direction: column;
  justify-content: space-between;
  padding: 30px 60px 25px 40px;
  border-left: 2px solid #f25c03;
  border-radius: 14px;
  background-color: white;
}

.one-event > .title{
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.border-left{
  border-left: 2px solid #F25C03;
  border-radius: 14 0 0 0px;
}

.border-top{
  border-top: 2px solid #F25C03;
  border-radius: 14px 0 0 0;
}

.orange-block{
  background-color: #FF6C36;
  color: #FFFFFF;
  border: 2px solid #F25C03;
  border-right: none;
  border-bottom: none;
  background-image: url(/icon/main/event-ear.svg);
  background-repeat: no-repeat;
  background-position: bottom right -50px;
  /* background-size: 90%; */
}

.event-wrapper{
  width: 35%;
  border-radius: 10px 10px 10px 0;
  background-color: #FF6C36;
}
</style>
