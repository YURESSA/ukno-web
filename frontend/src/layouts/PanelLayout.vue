<template>
  <n-config-provider :theme-overrides="themeOverrides" :locale="ruRU" :date-locale="dateRuRU">
    <div class="admin-layout">
      <!-- Затемнение фона на мобильных при открытом меню -->
      <Transition name="fade">
        <div
          v-if="isSidebarOpen"
          class="sidebar-overlay"
          @click="isSidebarOpen = false"
        ></div>
      </Transition>

      <header class="main-header">
        <div class="header-left">
          <button class="burger-btn" @click="isSidebarOpen = true" aria-label="Открыть меню">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="3" y1="6" x2="21" y2="6"></line>
              <line x1="3" y1="12" x2="21" y2="12"></line>
              <line x1="3" y1="18" x2="21" y2="18"></line>
            </svg>
          </button>

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
        </div>

        <div class="section-header">
          <h3>{{ currentSectionTitle }}</h3>
          <BaseButton
            v-if="showAddButton"
            class="add--btn"
            text="+ Создать"
            @click="triggerAddAction"
          />
        </div>
      </header>

      <aside class="left-sidebar" :class="{ open: isSidebarOpen }">
        <div class="sidebar-header-mobile">
          <span>Разделы админки</span>
          <button class="close-btn" @click="isSidebarOpen = false" aria-label="Закрыть меню">✕</button>
        </div>
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
              @click="() => { navigate(); isSidebarOpen = false; }"
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
import BaseButton from '@/components/ui/button/BaseButton.vue';

const route = useRoute();
const addEventCounter = ref(0);
const isSidebarOpen = ref(false);
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

.burger-btn {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  color: #333;
  padding: 6px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sidebar-header-mobile {
  display: none;
}

.sidebar-overlay {
  display: none;
}

main {
  height: 100%;
}

@media (max-width: 992px) {
  .admin-layout {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;
    grid-template-areas:
      "header"
      "main";
    height: 100vh;
    width: 100vw;
  }

  .main-header {
    padding: 12px 16px;
    height: auto;
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .header-left {
    justify-content: space-between;
    width: 100%;
  }

  .burger-btn {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .title-container {
    gap: 10px;
  }

  .title h5 {
    font-size: 16px;
  }

  .title p {
    font-size: 11px;
  }

  .section-header {
    margin-left: 0;
    padding: 10px 0 0 0;
    height: auto;
    border-left: none;
    border-top: 1px solid #e2e8f0;
    width: 100%;
    justify-content: space-between;
  }

  .section-header h3 {
    font-size: 18px;
  }

  :deep(.add--btn) {
    font-size: 13px;
    padding: 6px 12px;
    white-space: nowrap;
  }

  .left-sidebar {
    position: fixed;
    top: 0;
    left: -320px;
    width: 280px;
    height: 100vh;
    z-index: 2000;
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.2);
    transition: left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    background: #fff;
    padding: 0;
  }

  .left-sidebar.open {
    left: 0;
  }

  .sidebar-header-mobile {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 20px;
    border-bottom: 1px solid #e2e8f0;
    font-weight: 700;
    font-size: 18px;
    color: #333;
    margin-bottom: 10px;
  }

  .close-btn {
    background: none;
    border: none;
    font-size: 20px;
    cursor: pointer;
    color: #666;
  }

  .sidebar-overlay {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.4);
    z-index: 1900;
    backdrop-filter: blur(2px);
  }

  .main-content {
    padding: 14px;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  /* Автоматический горизонтальный скролл таблиц на мобильных */
  :deep(.n-data-table-wrapper) {
    overflow-x: auto !important;
  }

  :deep(.n-data-table-table) {
    min-width: 680px;
  }

  /* Модальные окна на весь экран или по ширине телефона */
  :deep(.n-card),
  :deep(.n-modal) {
    max-width: 96vw !important;
    margin: 10px auto !important;
  }
}
</style>
