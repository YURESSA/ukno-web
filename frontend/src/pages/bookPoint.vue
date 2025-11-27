<template>
  <div class="page-wrapper">
    <div class="header"><h1>BookPoint</h1></div>
    <div class="reki">

      <h4>Рекомендуем к прочтению</h4>
      <!-- <ul>
        <bookCard></bookCard>
        <bookCard></bookCard>
      </ul> -->
    </div>
    <div class="coworking">
      <h4>Наш коворкинг</h4>
      <ul>
        <li>
          <img src="../../public/assets/coworking.svg"></img>
        </li>
        <li>
          <img src="../../public/assets/coworking2.svg"></img>
        </li>
        <li>
          <img src="../../public/assets/coworking3.svg"></img>
        </li>
        <li>
          <img src="../../public/assets/coworking4.svg"></img>
        </li>
      </ul>
      <NButton type="primary">Забронировать</NButton>
    </div>
    <div class="event">
      <div class="event-card">
        <h3>Встреча с писателем</h3>
        <p>Приглашаем на встречу с новым русским писателем Иваном Марковым! <br>
        На этой встрече Автор расскажет о начале своё пути, где берёт вдохновение и ответ на все интересующие вас вопросы!</p>
        <span>03.12 в 12:00. По адресу Свердлова 25</span>
        <NButton type="primary" class="event-btn">Записаться</NButton>
      </div>
    </div>
    <Footer></Footer>
  </div>
</template>

<script setup>
import { NButton } from 'naive-ui';
import bookCard from '@/components/shared/bookCard.vue';
import Footer from '@/components/shared/footer.vue';
</script>

<style scoped>
.event{
  background-color: #F3F3F3;
  padding: 15px 10px;
  margin-bottom: 105px;
  border-radius: 10px;
}

.event-btn {
  width: 100%;
}

.event-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
}

.reki {
  display: flex;
  flex-direction: column;
  gap: 10px;
  background-color: #F3F3F3;
  border-radius: 20px;
}
ul {
  display: flex;
  overflow-x: scroll;
  scroll-snap-type: x mandatory;
  scrollbar-width: none;
  -ms-overflow-style: none;

}

li {
  list-style-type: none;
  scroll-snap-align: center;
  flex: 0 0 10px;
}

li img {
  width: 100vw;
}

.page-wrapper{
  display: flex;
  flex-direction: column;
  gap: 25px;
}

h1 {
  width: 100%;
  text-align: center;
}


h4 {
  padding: 10px 0 0 10px;
}

.coworking {
  display: flex;
  flex-direction: column;
  gap: 10px;
  background-color: #F3F3F3;
  border-radius: 20px;
  padding: 10px;
}



</style>
