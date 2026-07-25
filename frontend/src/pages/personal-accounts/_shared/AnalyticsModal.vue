<template>
  <div class="modal-wrapper" @click="$emit('close')">
    <div class="modal" @click.stop>
      <div class="header-modal">
        <h4>Статистика событий</h4>
        <IconButton @click="$emit('close')" class="action--btn"><img src="/icon/maki_cross.svg" alt=""></IconButton>
      </div>

      <div v-if="loading" class="loading-state">
        <p>Сбор аналитики...</p>
      </div>

      <div class="content-wrapper" v-else-if="analytics">
        <!-- Сводная статистика сверху -->
        <div class="summary-cards">
          <div class="summary-card">
            <span class="summary-title">Всего событий</span>
            <span class="summary-value">{{ analytics.total_excursions }}</span>
          </div>
          <div class="summary-card">
            <span class="summary-title">Всего участников</span>
            <span class="summary-value text-green">{{ analytics.total_visitors }}</span>
          </div>
        </div>

        <div class="popular-card" v-if="analytics.most_popular_excursion">
          <span class="summary-title">Самое популярное событие</span>
          <p class="popular-title">{{ analytics.most_popular_excursion.title }}</p>
          <span class="popular-stats">{{ analytics.most_popular_excursion.total_participants }} участников</span>
        </div>

        <h5 class="list-title">Детализация по событиям</h5>
        <div class="cards">
          <div class="card-wrapper" v-if="analytics.details && analytics.details.length > 0">
            <div class="card" v-for="item in analytics.details" :key="item.excursion_id">
              <div class="card-header">
                <p class="text-l bold">{{ item.title }}</p>
              </div>
              <div class="content">
                <div class="stat-row">
                  <span class="stat-label">Проведено сессий:</span>
                  <span class="stat-val">{{ item.session_count }}</span>
                </div>
                <div class="stat-row">
                  <span class="stat-label">Участников:</span>
                  <span class="stat-val">{{ item.total_participants }}</span>
                </div>
              </div>
            </div>
          </div>
          <p v-else class="empty-state">Нет данных для отображения</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import IconButton from '@/components/ui/button/IconButton.vue';
import { useDataStore } from '@/stores/counter';
import { computed, onMounted, ref } from 'vue';

const store = useDataStore();
const analytics = computed(() => store.getResidentAnalytics);
const emit = defineEmits(['close']);
const loading = ref(true);

onMounted(async () => {
  try {
    await store.FetchResidentAnalytics();
  } catch (error) {
    console.error('Ошибка при загрузке аналитики:', error);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.modal-wrapper{
  display: block;
  content: '';
  width: 100%;
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  overflow: hidden;
  background-color: rgba(128, 128, 128, 0.459);
  z-index: 9999;
}

h4 {
  text-align: center;
  margin-top: 20px;
  font-size: 24px;
}

.header-modal{
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.modal{
  position: absolute;
  width: 660px;
  max-height: 80vh;
  background-color: #FFFFFF;
  box-shadow: 0px 0px 12.7px 0px #0000002E;
  border-radius: 26px;
  padding: 40px 70px 60px 70px;
  top: 50%;
  left: 50%;
  transform: translateY(-50%) translateX(-50%);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.content-wrapper {
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 10px;
  scrollbar-width: thin;
}

.summary-cards {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.summary-card {
  flex: 1;
  background-color: #F8F9FA;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 1px solid #E9ECEF;
}

.popular-card {
  background-color: #FFF5EF;
  border: 2px solid #FFD6BD;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 30px;
  text-align: center;
}

.summary-title {
  font-size: 14px;
  color: #6C757D;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}

.summary-value {
  font-size: 32px;
  font-weight: 800;
  color: #212529;
}

.text-green {
  color: #20C997;
}

.popular-title {
  font-size: 20px;
  font-weight: 700;
  color: #F25C03;
  margin: 5px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.popular-stats {
  font-size: 16px;
  font-weight: 600;
  color: #495057;
}

.list-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 15px;
  text-align: left;
}

.card-wrapper{
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.card{
  max-width: 100%;
  padding: 20px;
  border-radius: 14px;
  border: 1px solid #DEDEDE;
  background-color: #fff;
}

.card-header{
  margin-bottom: 15px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
  max-width: 100%;
  overflow: hidden;
}

.card-header p {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.content{
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  color: #6c757d;
  font-size: 14px;
}

.stat-val {
  font-weight: 600;
  font-size: 16px;
}

.empty-state {
  text-align: center;
  color: #9E9E9E;
  margin-top: 20px;
}

.action--btn{
  height: max-content;
  padding: 4px;
  border-radius: 5px;
  border: none;
  background-color: #EDEDED8A;
}

.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 0;
  color: #9E9E9E;
  font-family: 'Manrope', sans-serif;
}

@media (max-width: 768px) {
  .modal {
    width: 90%;
    padding: 30px 20px;
  }

  .summary-cards {
    flex-direction: column;
  }
}
</style>
