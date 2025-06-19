<template>
  <div class="modal-wrapper" @click="$emit('close')">
    <div class="modal" @click.stop>
      <div class="header-modal">
        <h4>Все ваши события</h4>
        <IconButton @click="$emit('close')" class="action--btn"><img src="/icon/maki_cross.svg" alt=""></IconButton>
      </div>
      <div class="card-wrapper" v-if="events != ''">
        <div class="card" v-for="(excursion, i) in events.excursions" :key="i">
          <div class="card-header">
            <div class="left">
              <!-- <IconButton class="action--btn"><img src="/icon/pencil.svg" alt=""></IconButton> -->
              <p class="text-l bold">{{ excursion.title }}</p>
            </div>
            <IconButton @click="deletEvent(excursion.excursion_id, excursion.sessions[0].session_id)" class="action--btn"><img src="/icon/basket.svg" alt=""></IconButton>
          </div>
          <div class="content">
            <p>{{ excursion.description }}</p>
            <p>{{ formattedDate(excursion.sessions[0]) }} | {{ formattedTime(excursion.sessions[0]) }} | {{ excursion.category.category_name }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import IconButton from '@/components/UI/button/IconButton.vue';
import { useDataStore } from '@/stores/counter';
import { computed, onMounted } from 'vue';

const store = useDataStore();
const emit = defineEmits(['close']);

const formattedDate = (nearestSession) => {
  const date = new Date(nearestSession.start_datetime);
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  });
}

const formattedTime = (nearestSession) =>{
  const date = new Date(nearestSession.start_datetime);
  return date.toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit'
  });
}

onMounted(async () => {
  try {
    await store.FetchResidentEvents();
  } catch (error) {
    console.error('Ошибка при загрузке экскурсий:', error);
  }
});
const events = computed(() => store.getResidentEvents);

async function deletEvent(EventId, SId){
  try {
    await store.DeletSession(EventId, SId);
    alert('Событие успешно удалено')
    store.deletEvent();
    emit('close')
  } catch (error) {
    console.error('Ошибка при загрузке экскурсий:', error);
  }
}
</script>

<style scoped>
.modal-wrapper{
  display: block;
  content: '';
  width: 100%;
  height: 100vh;
  position: fixed;
  top: 0;
  overflow: hidden;
  background-color: rgba(128, 128, 128, 0.459);
  z-index: 99;
}

.header-modal{
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.card{
  padding: 40px 30px;
  border-radius: 14px;
  border: 1px solid #DEDEDE
}

.content{
  margin-right: 23px;
  margin-top: 20px;
}

.card-header{
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.left{
  display: flex;
  gap: 30px;
  align-items: center;
}

.modal{
  position: absolute;
  width: 660px;
  background-color: #FFFFFF;
  box-shadow: 0px 0px 12.7px 0px #0000002E;
  border-radius: 26px;
  padding: 40px 80px 80px 80px;
  top: 50%;
  left: 50%;
  transform: translateY(-50%) translateX(-50%);
}

.action--btn{
  width: 23px;
  height: 23px;
  padding: 4px;
  border-radius: 5px;
  border: none;
  background-color: #EDEDED8A;
}
</style>
