<template>
  <div class="review-wrapper">
    <div class="review-score">
      <div class="score">
        <img src="../../../public/assets/icon/feather.svg" alt="Перо"></img>
        <img src="../../../public/assets/icon/feather.svg" alt="Перо"></img>
        <img src="../../../public/assets/icon/feather.svg" alt="Перо"></img>
        <img src="../../../public/assets/icon/feather.svg" alt="Перо"></img>
        <img src="../../../public/assets/icon/feather.svg" alt="Перо"></img>
      </div>
      <div class="date">
        <p>30.11.2023</p>
      </div>
    </div>
    <div class="review-user">
      <p>Марина П.</p>
      <p>Очень доступно и интересно говорится о самом важном в жизни. Замечательно иллюстрирована. Интересна и взрослым. Нужна каждой семье. Рекомендую.</p>
    </div>
  </div>
</template>

<script setup>

</script>

<style scoped>
.review-wrapper {
  width: 100%;
  background-color: #F3F3F3;
  border-radius: 10px;
  padding: 6px;
  display: flex;
  justify-content: space-between;
  box-shadow: 2px 2px 4px 0px rgba(34, 60, 80, 0.2);
}

.review-score {
  width: 30%;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.review-user {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

p {
  margin: 0;
  padding: 0;
  font-size: 9px;
}

.score img{
  width: 10px;
  height: 10px;
}

.score {
  display: flex;
  gap: 3px;

}

.date {
  color: #121212;
}
</style>
