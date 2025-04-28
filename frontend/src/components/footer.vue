<template>
  <div class="page-wrapper">
    <div class="navigation">
      <div class="logo">
        <img src="/logo/footer_logo.svg" alt="">
      </div>
      <nav>
        <ul class="nav-list">
          <li><a href="#about">О НАС</a></li>
          <li><a href="#events">МЕРОПРИЯТИЯ</a></li>
          <li><a href="#news">НОВОСТИ</a></li>
          <li><a href="#history">ИСТОРИЯ УКНО</a></li>
          <li><a href="#profile">ПРОФИЛЬ</a></li>
          <li><a href="#contact">КОНТАКТЫ</a></li>
        </ul>
      </nav>
    </div>
    <div class="development-team">
      ТУТ ПРИДУМАТЬ КАК РАСПОЛОЖИТЬ НАС (ТЕХ, КТО СДЕЛАЛ)
    </div>
  </div>
</template>

<script setup>

</script>

<style scoped>
.page-wrapper{
  background-color: #333333;
}

.navigation{
  display: flex;
  justify-content: space-between;
  gap: 70px;
}

.nav-list{
  flex: 1;
  justify-content: space-between;
}

a{
  color: white;
}

nav{
  display: flex;
  align-items: center;
  width: 100%;
  padding: 10px 20px;
}

.development-team{
  margin-top: 100px;
  color: white;
}
</style>
