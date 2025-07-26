<template>
  <div class="header-wrapper">
    <nav class="nav-wrapper">
      <ul class="nav-list">
        <li><RouterLink :to="{ path: '/', hash: '#news' }" replace >О НАС</RouterLink></li>
        <li><RouterLink to="/events">СОБЫТИЯ</RouterLink></li>
        <li>
          <div class="logo">
            <RouterLink to="/"><img src="/logo/logo.svg" alt=""></RouterLink>
          </div>
        </li>
        <li><RouterLink to="/news">НОВОСТИ</RouterLink></li>
        <li><RouterLink :to="{ path: '/', hash: '#contact' }" replace >КОНТАКТЫ</RouterLink></li>
      </ul>
      <div class="profile">
        <RouterLink to="/login" v-if="hasToken">
          <button>
            <img src="/icon/header/profile-fill.svg" alt="">
          </button>
        </RouterLink>
        <RouterLink to="/profile" v-else-if="!hasToken & role === 'user'">
          <button>
            <img src="/icon/header/profile-fill.svg" alt="">
          </button>
        </RouterLink>
        <RouterLink to="/resident-profile" v-else-if="!hasToken & role === 'resident'">
          <button>
            <img src="/icon/header/profile-fill.svg" alt="">
          </button>
        </RouterLink>
      </div>
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

const role = computed(() => {
  return store.role;
});

</script>

<style scoped>

.header-wrapper{
  width: calc(100% - 90px);
  position: fixed;
  padding: 28px 45px;
  backdrop-filter: blur(28.399999618530273px);
  background: rgba(255, 255, 255, 0.7);
  z-index: 99999999;
}

.nav-wrapper{
  position: relative;
}

.nav-list{
  width: 80%;
  margin: 0 auto;
  justify-content: space-around;
  align-items: center;
  transform: translateX(28px);
}

.profile{
  position: absolute;
  right: 45px;
  top: 50%;
  transform: translateY(-50%);
}

button{
  display: flex;
  align-items: center;
  padding: 0;
  justify-content: end;
  gap: 15px;
  background-color: #FFD4C4;
  border-radius: 300px;
}

button > img {
  margin-right: -1px;
}
</style>
