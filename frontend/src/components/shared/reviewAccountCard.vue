<template>
  <div class="review-wrapper">
    <div class="info">
      <div><img class="photo-book" src='../../../public/assets/book1.svg'></img></div>
      <div>
        <p class="name">Подарок на Новый год под ёлку от Маши Рупасовой / 3 книги...</p>
        <div class="score">
          <img src='../../../public/assets/icon/feather.svg'></img>
          <img src='../../../public/assets/icon/feather.svg'></img>
          <img src='../../../public/assets/icon/feather.svg'></img>
          <img src='../../../public/assets/icon/feather.svg'></img>
          <img src='../../../public/assets/icon/feather.svg'></img>
        </div>
        <p class="date">30.11.2023</p>
      </div>
    </div>
      <div class="text">
        <p>Очень доступно и интересно говорится о самом важном в жизни. Замечательно иллюстрирована. Интересна и взрослым. Нужна каждой семье. Рекомендую.</p>
        <button>Редактировать</button>
      </div>
  </div>
</template>

<style scoped>
.photo-book {
  width: 55px;
  height: 75px;
}
.info{
  display: flex;
  flex-direction: row;
  gap: 18px;
}
.text {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.text button {
  border: none;
  display: flex;
  align-items: flex-start;
  padding: 0;
  color: #F7742A;
}
.date {
  font-size: 9px;
}
.review-wrapper {
  padding: 19px;
  background-color: #F3F3F3;
  border-radius: 10px;
  display: flex;
  gap: 6px;
  flex-direction: column;
  box-shadow: 2px 2px 4px 0px rgba(34, 60, 80, 0.2);
}
</style>
