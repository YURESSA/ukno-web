<template>
  <div class="page-wrapper">
    <div class="navigation">
      <div class="logo">
        <RouterLink to="/"><img src="/logo/footer_logo.svg" alt=""></RouterLink>
      </div>
      <nav>
      <ul class="nav-list">
        <li><RouterLink :to="{ path: '/ukno'}">О НАС</RouterLink></li>
        <li><RouterLink to="/events">СОБЫТИЯ</RouterLink></li>
        <li><RouterLink :to="{ path: '/news'}">НОВОСТИ</RouterLink></li>
        <li><RouterLink :to="{ path: '/', hash: '#contact' }">КОНТАКТЫ</RouterLink></li>
        <li><RouterLink :to="{ path: '/requesits'}">РЕКВИЗИТЫ</RouterLink></li>
      </ul>
      </nav>
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
  gap: 150px;
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
