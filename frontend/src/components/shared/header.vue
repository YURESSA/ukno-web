<template>
  <div class="header-wrapper">
    <div class="header">
      <div class="logo">
        <RouterLink to="/"><img src="/logo/logo.svg" alt=""></RouterLink>
      </div>
      <div class="profile">
        <RouterLink to="/login" v-if="hasToken">
          <button>
            Личный кабинет
            <img src="/icon/header/iconamoon_profile-fill.svg" alt="">
          </button>
        </RouterLink>
        <RouterLink to="/profile" v-if="!hasToken">
          <button>
            Личный кабинет
            <img src="/icon/header/iconamoon_profile-fill.svg" alt="">
          </button>
        </RouterLink>
      </div>
    </div>
    <nav>
      <ul class="nav-list">
        <li><RouterLink :to="{ path: '/', hash: '#news' }" replace >О НАС</RouterLink></li>
        <li><RouterLink to="/events">СОБЫТИЯ</RouterLink></li>
        <li><RouterLink :to="{ path: '/', hash: '#news' }" replace >НОВОСТИ</RouterLink></li>
        <li><RouterLink :to="{ path: '/', hash: '#contact' }" replace >КОНТАКТЫ</RouterLink></li>
      </ul>
    </nav>
  </div>
</template>


<script setup>
import { computed } from 'vue';
import { useDataStore } from '@/stores/counter';

const store = useDataStore();

const hasToken = computed(() => {
  return !store.auth_key;
});



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

button{
  display: flex;
  align-items: center;
  padding: 0;
  padding-left: 30px;
  justify-content: end;
  gap: 15px;
  background: none;
  border: 1px solid #333333;
  border-radius: 300px;
}

button > img {
  margin-right: -1px;
}
</style>
