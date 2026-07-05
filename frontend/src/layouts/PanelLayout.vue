<template>
  <n-config-provider :theme-overrides="themeOverrides" :locale="ruRU" :date-locale="dateRuRU">
    <div class="admin-layout">
      <header class="main-header">
        <div class="title-container">
          <div class="icon">
            <RouterLink to="/">
              <img src="/logo/mobile-logo.svg" alt="Logo">
            </RouterLink>
          </div>
          <div class="title">
            <h5>Админ панель</h5>
            <p>Управление системой</p>
          </div>
        </div>

        <div class="section-header">
          <h3>{{ currentSectionTitle }}</h3>
          <BaseButton
            v-if="showAddButton"
            class="add--btn"
            text="+ Создать запись"
            @click="triggerAddAction"
          />
        </div>
      </header>

      <aside class="left-sidebar">
        <nav class="nav-section">
          <RouterLink
            v-for="item in menuItems"
            :key="item.path"
            :to="item.path"
            custom
            v-slot="{ navigate, isActive }"
          >
            <BaseButton
              class="nav-button"
              :class="{ active: isActive }"
              @click="navigate"
              :text="item.label"
            />
          </RouterLink>
        </nav>
      </aside>

      <main class="main-content">
        <n-message-provider>
          <n-dialog-provider>
            <router-view></router-view>
          </n-dialog-provider>
        </n-message-provider>
      </main>
    </div>
  </n-config-provider>
</template>

<script setup>
import { computed, provide, ref } from 'vue';
import { useRoute } from 'vue-router';
import { NConfigProvider, ruRU, dateRuRU, NMessageProvider, NDialogProvider } from 'naive-ui';
import BaseButton from '@/components/UI/button/BaseButton.vue';

const route = useRoute();
const addEventCounter = ref(0);
provide('admin-add-event', addEventCounter);

// Массив для меню, чтобы не дублировать RouterLink в шаблоне
const menuItems = [
  { path: '/panel/users', label: 'Пользователи', name: 'AdminUsers' },
  { path: '/panel/categories', label: 'Категории', name: 'AdminCategories' },
  { path: '/panel/formats', label: 'Типы форматов', name: 'AdminFormats' },
  { path: '/panel/age-categories', label: 'Возрастные категории', name: 'AdminAge' },
  { path: '/panel/events', label: 'События', name: 'AdminEvents' },
  { path: '/panel/news', label: 'Новости', name: 'AdminNews' },
  { path: '/panel/reservations', label: 'Брони', name: 'AdminReservations' },
  { path: '/panel/team', label: 'Команда', name: 'AdminTeam' },
  { path: '/panel/cultural-space', label: 'Культурное пространство', name: 'CulturalSpace' },
  { path: '/panel/project', label: 'Проекты', name: 'AdminProject' },
  { path: '/panel/history', label: 'История', name: 'AdminHistory' },
  { path: '/panel/partner', label: 'Партнёры', name: 'AdminParther' },
  { path: '/panel/requisites', label: 'Резвизиты', name: 'AdminRequisites' },
  { path: '/panel/merch', label: '🛍 Магазин', name: 'AdminMerch' },
];

const currentSectionTitle = computed(() => route.meta.title || 'Управление');

const showAddButton = computed(() => {
  const hideOn = ['AdminReservations'];
  return !hideOn.includes(route.name);
});

const themeOverrides = {
  common: {
    primaryColor: '#FF6C36',
    primaryColorHover: '#DD5827',
    primaryColorPressed: '#FFA280',
    primaryColorSuppl: '#FF6C36'
  }
};

function triggerAddAction() {
  addEventCounter.value++; // Просто увеличиваем счетчик кликов
}
</script>

<style scoped>
.admin-layout {
  display: grid;
  grid-template-columns: 322px 1fr;
  grid-template-rows: 116px 1fr;
  grid-template-areas:
    "header header"
    "sidebar main";
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.main-header {
  grid-area: header;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 40px;
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
  z-index: 10;
}

.left-sidebar {
  grid-area: sidebar;
  background: #fff;
  border-right: 1px solid #e2e8f0;
  padding: 25px 0;
  overflow-y: auto;
}

.nav-section {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.main-content {
  grid-area: main;
  background-color: #f9fafb;
  padding: 25px;
  overflow-y: auto;
}


.title-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
}

.title{
  width: max-content;
}

.section-header{
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-left: 9px;
  padding-left: 25px;
  height: calc(100% + 50px);
  width: 100%;
  border-left: 1px solid #e2e8f0;
}

.nav-button {
  width: 100%;
  background: none;
  color: #333333;
  font-weight: 500;
  font-size: 20px;
}

.nav-button:hover {
  background-color: #FF895D;
}

.nav-button.active {
  background-color: #FF6C36;
  color: white;
}

main{
  height: 100%;
}
</style>
