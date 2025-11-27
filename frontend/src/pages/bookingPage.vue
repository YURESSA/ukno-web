<template>
  <div class="page-wrapper">
    <div class="header">
      <iconBtn><img src="../../public/assets/icon/icon-arrow-black.svg" class="img"></img></iconBtn>
      <h1>Бронирование</h1>
    </div>
    <div class="main">

    </div>
    <div class="search">
        <NInput placeholder="Поиск"></NInput>
        <ul>
          <addressSelect></addressSelect>
          <addressSelect></addressSelect>
          <addressSelect></addressSelect>
          <addressSelect></addressSelect>

        </ul>
    </div>
    <div  class="booking">
      <NButton type="primary" @click="booking"><p>Забронировать</p></NButton>
    </div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import iconBtn from '@/components/ui/icon-btn.vue';
import { NInput, NButton } from 'naive-ui';
import addressSelect from '@/components/shared/addressSelect.vue';
import { computed, onMounted } from 'vue';
import { useDataStore } from '@/stores/counter';
import router from '@/router';

const route = useRoute();
const store = useDataStore();
const bookId = route.params.id;

const booksCopy = computed(() => store.сopiesBook)

onMounted(async () => {
  await store.GetCopiesBook(bookId)
})

async function booking(){
  console.log(booksCopy.value)
  try{
    await store.PostOrder(booksCopy.value[0].id)
    router.push('/account')
  } catch {
    console.error('Ошибка')
  }
}
</script>

<style scoped>
.booking {
  display: flex;
  justify-content: center;
  margin-bottom: 90px;
}
.page-wrapper {
  display: flex;
  flex-direction: column;
  gap: 27px;
}
ul {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding-top: 20px;
}

.search {
  padding-top: 20px;
  border-radius: 50%;
}

.main {
  background-image: url('../../public/assets/icon/map.PNG');
  padding-bottom: 400px;
}

.header {
  display: flex;
  flex-direction: row;
  text-align: center;
}
.header {
  padding-top: 15px;
}
h1 {
  width: 100%;
}

.img{
  width: 15px;
  height: 15px;
}
</style>


