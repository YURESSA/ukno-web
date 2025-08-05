<template>
  <div class="result-wrapper">
    <div class="title">
      <h3>Ваше культурное пространство — это</h3>
    </div>
    <div class="result-list text-l">
      <ul>
        <li>
          <div class="content solo text-orange">
            <p>Выставки</p>
          </div>
        </li>
        <li>
          <div class="content">
            <p>Развитие</p>
          </div>
          <div class="content">
            <p >240 м² возможностей</p>
          </div>
        </li>
        <li>
          <div class="content">
            <p>Сообщество мечтателей</p>
          </div>
          <div class="content">
            <p>Арт-пространство для всех</p>
          </div>
        </li>
        <li>
          <div class="content">
            <p>История с 1978 года</p>
          </div>
          <div class="content">
            <p>Творчество без границ</p>
          </div>
          <div class="content">
            <p>Новое в старом</p>
          </div>
        </li>
        <li>
          <div class="content">
            <p>Мастер-классы будущего</p>
          </div>
          <div class="content">
            <p>Экскурсии в прошлое</p>
          </div>
          <div class="content custom">
            <p>90 м² уюта</p>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import eventsBlock from './events-block.vue';

</script>

<style scoped>
.result-wrapper{
  background-color: white;
  border-radius: 38px 38px 0px 0px;
  padding: 80px 50px;
  padding-bottom: 230px;
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

.text-orange{
  color: #F25C03;
  border-color: #F25C03;
}

.custom{
  width: 280px;
}
</style>
