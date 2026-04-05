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
          <li><RouterLink :to="{ path: '/requesits'}">РЕКВИЗИТЫ ОГРАНИЗАЦИИ</RouterLink></li>
        </ul>
      </nav>
    </div>

    <div class="developers">
      <ul class="dev-list">
        <li><a href="https://t.me/alllinag" target="_blank">Дизайн</a></li>
        <li><a href="https://github.com/Anton787" target="_blank">Фронтенд</a></li>
        <li><a href="https://github.com/YURESSA" target="_blank">Бэкенд</a></li>
        <li><a href="https://t.me/Wnpks" target="_blank">Аналитика</a></li>
      </ul>
    </div>

  </div>
</template>

<script setup>
</script>

<style scoped>
.page-wrapper {
  background-color: #333333;
}

.navigation {
  display: flex;
  justify-content: space-between;
  gap: 150px;
  margin-bottom: 105px;
}

.nav-list {
  display: flex;
  flex: 1;
  justify-content: space-between;
  list-style: none;
  padding: 0;
  margin: 0;
}

a {
  color: white;
  text-decoration: none;
}

nav {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 10px 20px;
}

.developers {
  display: flex;
  justify-content: center;
}

.dev-list {
  display: flex;
  align-items: center;
  list-style: none;
  padding: 0;
  margin: 0;
  gap: 0;
}

.dev-list li {
  display: flex;
  align-items: center;
}

.dev-list a {
  color: #c4c4c4;
  font-size: 20px;
}

.dev-list li:not(:last-child)::after {
  content: '|';
  margin: 0 25px;
  color: #c4c4c4;
  font-weight: 300;
}

@media (max-width: 768px) {
  .navigation{
    flex-direction: column;
    gap: 30px;
    align-items: center;
    margin-bottom: 52px;
  }
  .nav-list{
    flex-direction: column;
    align-items: center;
  }

  .dev-list {
    flex-direction: column;
    gap: 7px;
    font-size: 14px;
  }

  .dev-list a {
    font-size: 16px;
  }

  .dev-list li:not(:last-child)::after {
    all: unset;
  }

  .dev-list li:not(:last-child)::after {
    margin: 0 10px;
  }
}
</style>
