<template>
  <div class="result-wrapper">
    <div class="title">
      <h3>Наш результат — ваше вдохновение</h3>
    </div>
    <div class="result-list">
      <ul>
        <li>
          <div class="content solo orange">
            <p class="large-text">Выставки</p>
          </div>
        </li>
        <li>
          <div class="content">
            <p class="large-text">Развитие</p>
          </div>
          <div class="content">
            <p class="large-text">240 м² возможностей</p>
          </div>
        </li>
        <li>
          <div class="content">
            <p class="large-text">Сообщество мечтателей</p>
          </div>
          <div class="content">
            <p class="large-text">Арт-пространство для всех</p>
          </div>
        </li>
        <li>
          <div class="content">
            <p class="large-text">История с 1978 года</p>
          </div>
          <div class="content">
            <p class="large-text">Творчество без границ</p>
          </div>
          <div class="content">
            <p class="large-text">Новое в старом</p>
          </div>
        </li>
        <li>
          <div class="content">
            <p class="large-text">Мастер-классы будущего</p>
          </div>
          <div class="content">
            <p class="large-text">Экскурсии в прошлое</p>
          </div>
          <div class="content custom">
            <p class="large-text">90 м² уюта</p>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>

</script>

<style scoped>
.result-wrapper{
  background-color: white;
  border-radius: 38px 38px 0px 0px;
  padding: 80px 50px;
}

h3{
  text-align: center;
}

ul{
  flex-direction: column;
  align-items: center;
  gap: 30px;
}

li{
  display: flex;
  gap: 10px;
}

.result-list{
  margin-top: 80px;
}

.content{
  display: flex;
  justify-content: center;
  padding: 20px 40px;
  border: 2px solid #333333;
  border-radius: 30px;
}


.solo{
  width: 220px;
}

.orange{
  color: #F25C03;
  border-color: #F25C03;
}

.custom{
  width: 280px;
}
</style>
