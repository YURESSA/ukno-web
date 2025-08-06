<template>
  <div class="modal-wrapper" @click="$emit('close')">
    <div class="modal" @click.stop>
      <div class="header-modal">
        <h4>Все ваши события</h4>
        <IconButton @click="$emit('close')" class="action--btn"><img src="/icon/maki_cross.svg" alt=""></IconButton>
      </div>
      <div class="card-wrapper" v-if="events != ''">
        <div class="card" v-for="(excursions, i) in events.excursions" :key="i">
          <div class="card-header">
            <div class="left">
              <p class="text-l bold">{{ excursions.title }}</p>
            </div>
            <div class="card-btn">
              <IconButton class="action--btn"><img src="/icon/pencil.svg" alt="" @click="router.push(`/change-event/${excursions.excursion_id}`)"></IconButton>
              <IconButton @click="deletEvent(excursions.excursion_id)" class="action--btn"><img src="/icon/basket.svg" alt=""></IconButton>
            </div>
          </div>
          <div class="content">
            <p>{{ excursions.description }}</p>
            <p v-if="excursions.sessions.length != 0 ">{{ formattedDate(excursions.sessions[0]) }} | {{ formattedTime(excursions.sessions[0]) }} | {{ excursions.category.category_name }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import IconButton from '@/components/UI/button/IconButton.vue';
import router from '@/router';
import { useDataStore } from '@/stores/counter';
import { computed, onMounted, ref } from 'vue';

const store = useDataStore();
const events = computed(() => store.getResidentEvents);
const emit = defineEmits(['close']);

onMounted(async () => {
  try {
    await store.FetchResidentEvents();
  } catch (error) {
    console.error('Ошибка при загрузке экскурсий:', error);
  }
});

const formattedDate = (nearestSession) => {
  console.log(nearestSession)
  console.log(events.value)
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

async function deletEvent(EventId){
  try {
    await store.DeletEvent(EventId);
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
  align-items: center;
  margin-bottom: 20px;
}

.card-wrapper{
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 30px;
}

.card{
  min-width: 100%;
  padding: 40px 30px;
  border-radius: 14px;
  border: 1px solid #DEDEDE
}

.content{
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-right: 23px;
  margin-top: 20px;
}

.card-header{
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-btn{
  display: flex;
  gap: 15px;
}

.left{
  display: flex;
  gap: 30px;
  align-items: center;
}

.modal{
  position: absolute;
  width: 660px;
  max-height: 600px;
  overflow-y: scroll;
  background-color: #FFFFFF;
  box-shadow: 0px 0px 12.7px 0px #0000002E;
  border-radius: 26px;
  padding: 40px 80px 80px 80px;
  top: 50%;
  left: 50%;
  transform: translateY(-42%) translateX(-50%);
}

.action--btn{
  height: max-content;
  padding: 4px;
  border-radius: 5px;
  border: none;
  background-color: #EDEDED8A;
}
</style>
