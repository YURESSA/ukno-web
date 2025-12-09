<template>
  <div class="header-wrapper">
    <nav class="nav-wrapper">
      <ul class="nav-list">
        <li class="project">
          Проекты
          <ul class="project-list">
            <li>Психологический клуб</li>
            <li>Репетиторский клуб</li>
            <li>Музейное пространство</li>
          </ul>
        </li>
        <li><RouterLink to="/events">События</RouterLink></li>
        <li>
          <div class="logo">
            <RouterLink to="/"><img src="/logo/logo.svg" alt=""></RouterLink>
          </div>
        </li>
        <li><RouterLink to="/news">Новости</RouterLink></li>
        <li><RouterLink :to="{ path: '/ukno'}" replace >О нас</RouterLink></li>
      </ul>
      <div class="profile">
        <RouterLink to="/login" v-if="hasToken">
          <button>
            <img src="/icon/header/profile-fill.svg" alt="">
          </button>
        </RouterLink>
        <RouterLink to="/profile" v-else-if="!hasToken & role === 'user'">
          <button>
            <h4>{{ profileData.full_name[0].toUpperCase() }}</h4>
          </button>
        </RouterLink>
        <RouterLink to="/resident-profile" v-else-if="!hasToken & role === 'resident'">
          <button>
            <h4>{{ profileData.full_name[0].toUpperCase() }}</h4>
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

const profileData = computed(() => store.getProfileData)

</script>

<style scoped>

.header-wrapper{
  width: calc(100% - 90px);
  position: fixed;
  padding: 28px 45px;
  backdrop-filter: blur(28.399999618530273px);
  background: rgba(255, 255, 255, 0.7);
  z-index: 900;
}

.nav-wrapper{
  position: relative;
}

.nav-list{
  width: 80%;
  margin: 0 auto;
  justify-content: space-around;
  align-items: center;
  /* transform: translateX(28px); */
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
  width: 48px;
  height: 48px;
  justify-content: center;
  background-color: #FFD4C4;
  border-radius: 300px;
  color: #FF8C5B;
}

button > img {
  margin-right: -1px;
}

.project{
  position: relative;
  display: flex;
  align-items: center;
}

.project-list{
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0px;
  left: 0;
  transform: translateX(-25%);
  top: 70px;
  background-color: white;
  box-shadow: 0 4px 10px 0 rgba(0, 0, 0, 0.04);
  border-radius: 8px;
  opacity: 0;
  visibility: hidden;
  transition: all 0.5s ease;
}

.project:hover > .project-list{
  visibility: visible;
  opacity: 1;
}

.project:hover{
  height: 70px;
}

.project-list > li{
  padding: 6px 12px;
  width: 260px;
  transition: all 0.3s ease;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
}

.project-list > li:hover{
  background-color: #EBEBEB;
}
</style>
