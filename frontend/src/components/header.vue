<template>
  <div class="header-wrapper">
    <div class="header">
      <div class="logo">
        <img src="/logo/logo.svg" alt="">
      </div>
      <div class="contact-list">
        <ul>
          <li><a href=""><img src="/icon/header/phone.svg" alt=""></a></li>
          <li><a href=""><img src="/icon/header/vk.svg" alt=""></a></li>
          <li><a href=""><img src="/icon/header/tg.svg" alt=""></a></li>
        </ul>
      </div>
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
</template>


<script setup>

</script>

<style scoped>

.header-wrapper{
  padding: 10px;
}

.header{
  display: flex;
  justify-content: space-between;
  padding: 0 30px;
}

.nav-list{
  justify-content: space-around;
}

nav{
  padding: 10px 30px;
  border-top: 1px solid #333333;
  border-bottom: 1px solid #333333;
}
</style>
