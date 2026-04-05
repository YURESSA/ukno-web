<template>
  <div class="event-view">
    <h3>Место сбора: {{ eventAddress }}</h3>
    <input type="text" style="width: 500px;"  v-model="eventAddress">
    <button @click="init">поиск</button>
    <div id="event-map" class="map-view"></div>
    <div class="test">
      {{ q1 }}
      {{ q2 }}
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';

// Эмуляция данных из вашей БД
const eventAddress = ref("Екатеринбург, улица 40-летия Комсомола, 35/4");
const q1 = ref();
const q2 = ref();
const q3 = ref();
const q4 = ref();
const q5 = ref();

onMounted(() => {
  if (typeof ymaps !== 'undefined') {
    ymaps.ready(init);
  }
});

function init() {
    const myMap = new ymaps.Map("event-map", {
        center: [59.9386, 30.3141], // Центр города по умолчанию
        zoom: 15
    });

    // Поиск координат по сохраненному адресу (Геокодирование)
    ymaps.geocode(eventAddress.value, {
        results: 1 // Нам нужен только один самый точный результат
    }).then(function (res) {
        const firstGeoObject = res.geoObjects.get(0);
        const coords = firstGeoObject.geometry.getCoordinates();

        // Добавляем метку на карту
        const placemark = new ymaps.Placemark(coords, {
            balloonContent: `Место сбора: ${eventAddress.value}`
        }, {
            preset: 'islands#dotIcon',
            iconColor: '#ff0000'
        });

        myMap.geoObjects.add(placemark);

        // Центрируем карту на найденной точке
        myMap.setCenter(coords);
        q2.value = coords
    });
}
</script>

<style scoped>
.map-view {
  width: 100%;
  height: 400px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
</style>
