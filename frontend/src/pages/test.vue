<template>
  <div class="event-view">
    <div class="search-section">
      <div class="search-box">
        <div class="input-wrapper">
          <input
            type="text"
            v-model="eventAddress"
            @input="handleInput"
            placeholder="Введите адрес в Свердловской области..."
            autocomplete="off"
            :class="{ 'has-suggestions': suggestions.length }"
          >
          <transition name="fade">
            <ul v-if="suggestions.length" class="custom-suggest">
              <li
                v-for="(s, index) in suggestions"
                :key="index"
                @click="selectSuggestion(s.value)"
              >
                {{ s.displayName }}
              </li>
            </ul>
          </transition>
        </div>
        <button @click="geocodeByText" :disabled="!isMapInitialized" class="btn-primary">
          Найти
        </button>
      </div>
      <button @click="saveEvent" :disabled="!coords" class="btn-save">
        Сохранить локацию
      </button>
    </div>

    <div class="map-wrapper">
      <div id="map-container" class="map-view"></div>
      <div v-if="!isMapInitialized" class="map-overlay">
        <div class="spinner"></div>
        <p>{{ loadingStatus }}</p>
      </div>
    </div>

    <div class="status-panel" v-if="coords">
      <div class="status-item">
        <span class="label">Адрес:</span>
        <span class="value">{{ eventAddress }}</span>
      </div>
      <div class="status-item">
        <span class="label">Координаты:</span>
        <span class="value">{{ coords[0].toFixed(6) }}, {{ coords[1].toFixed(6) }}</span>
      </div>
    </div>
  </div>
  {{ suggestions }}
</template>

<script setup>
/* global ymaps */
import { useDataStore } from '@/stores/counter';
import { onMounted, ref, shallowRef, onUnmounted } from 'vue';

const store = useDataStore();

// --- Состояние ---
const eventAddress = ref("");
const coords = ref(null);
const suggestions = ref([]);
const isMapInitialized = ref(false);
const loadingStatus = ref("Загрузка карты...");

const myMap = shallowRef(null);
const myPlacemark = shallowRef(null);

let debounceTimer = null;

// --- Конфигурация ---
const API_KEY = import.meta.env.VITE_YANDEX_API_KEY;
const BACKEND_URL = import.meta.env.VITE_FRONTEND_URL;

onMounted(() => {
  // Инициализация глобального колбэка для скрипта Яндекса
  window.initYandexMapCallback = () => {
    initMap();
  };

  if (window.ymaps && window.ymaps.Map) {
    initMap();
    return;
  }

  const script = document.createElement('script');
  script.type = 'text/javascript';
  // Загружаем только графическое ядро API
  script.src = `https://api-maps.yandex.ru/2.1/?apikey=${API_KEY}&lang=ru_RU&load=package.full&onload=initYandexMapCallback`;
  script.onerror = () => {
    loadingStatus.value = "Ошибка загрузки карты. Проверьте API ключ.";
  };
  document.head.appendChild(script);
});

// Инициализация карты
function initMap() {
  const container = document.getElementById('map-container');
  if (!container) return;

  try {
    myMap.value = new ymaps.Map(container, {
      center: [56.8389, 60.6057], // Екатеринбург
      zoom: 13,
      controls: ['zoomControl']
    }, {
      // ПРИМЕНЯЕМ СТИЛИЗАЦИЮ
      // Мы используем фильтры, чтобы подогнать карту под твою палитру
      yandexMapDisablePoiInteractivity: true, // Отключаем лишние клики по иконкам
    });

    // Добавляем слой стилизации через CSS-фильтры на контейнер карты
    // Это самый надежный способ для версии 2.1 быстро сменить гамму
    const mapCanvas = container.querySelector('ymaps[class$="-map"]');
    if (mapCanvas) {
      // Немного тонируем карту в сторону твоего фонового цвета #FFD6BD
      container.style.backgroundColor = '#e5e5e5';
    }

    myMap.value.events.add('click', (e) => {
      const clickCoords = e.get('coords');
      updateMarker(clickCoords);
      reverseGeocode(clickCoords);
    });

    isMapInitialized.value = true;
  } catch (e) {
    console.error("Ошибка при создании карты:", e);
    loadingStatus.value = "Ошибка: " + e.message;
  }
}

// Поиск подсказок через твой БЭКЕНД
function handleInput() {
  clearTimeout(debounceTimer);
  suggestions.value = [];

  if (eventAddress.value.length < 3) return;

  debounceTimer = setTimeout(async () => {
    // Обращаемся к твоему новому эндпоинту в core/services
    console.log(eventAddress)
    const url = `${BACKEND_URL}api/yandex/map-helper?suggest=${encodeURIComponent(eventAddress.value)}`;
    console.log(url)
    try {
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${store.auth_key}`,
          'Content-Type': 'application/json'
        }
      });
      if (!response.ok) throw new Error('Backend error');

      const data = await response.json();

      if (data.results) {
        suggestions.value = data.results.map(item => ({
          displayName: item.title.text + (item.subtitle ? ', ' + item.subtitle.text : ''),
          value: item.title.text + (item.subtitle ? ', ' + item.subtitle.text : '')
        }));
      }
    } catch (e) {
      console.error("Ошибка Suggest API через бэкенд:", e);
    }
  }, 800); // Задержка 800мс для комфортного ввода
}

// Выбор подсказки и поиск координат на ФРОНТЕНДЕ
function selectSuggestion(val) {
  eventAddress.value = val;
  suggestions.value = [];

  if (window.ymaps && ymaps.geocode) {
    ymaps.geocode(val, { results: 1 }).then((res) => {
      const obj = res.geoObjects.get(0);
      if (obj) {
        const foundCoords = obj.geometry.getCoordinates();
        updateMarker(foundCoords);
        myMap.value.setCenter(foundCoords, 16);
      }
    });
  }
}

// Геокодирование текста (по кнопке "Найти")
function geocodeByText() {
  if (!eventAddress.value || !window.ymaps) return;

  ymaps.geocode(eventAddress.value, { boundedBy: SV_BOUNDS, results: 1 }).then((res) => {
    const obj = res.geoObjects.get(0);
    if (obj) {
      const foundCoords = obj.geometry.getCoordinates();
      updateMarker(foundCoords);
      myMap.value.setCenter(foundCoords, 16);
    }
  });
}

// Обратное геокодирование (Координаты -> Адрес)
function reverseGeocode(c) {
  ymaps.geocode(c).then((res) => {
    const obj = res.geoObjects.get(0);
    if (obj) {
      eventAddress.value = obj.getAddressLine();
    }
  });
}

// Обновление позиции маркера
function updateMarker(newCoords) {
  coords.value = newCoords;
  if (myPlacemark.value) {
    myPlacemark.value.geometry.setCoordinates(newCoords);
  } else {
    myPlacemark.value = new ymaps.Placemark(newCoords, {
      balloonContent: 'Место проведения мероприятия'
    }, {
      // Используем кастомный цвет иконки
      iconColor: '#F25C03', // Твой основной оранжевый!
      preset: 'islands#dotIcon',
      hasHint: false
    });

    myMap.value.geoObjects.add(myPlacemark.value);
  }
}

function saveEvent() {
  console.log("Сохранение локации:", {
    address: eventAddress.value,
    lat_lon: coords.value
  });
  alert("Данные сохранены (проверьте консоль)!");
}

onUnmounted(() => {
  if (myMap.value) {
    myMap.value.destroy();
  }
  delete window.initYandexMapCallback;
});
</script>

<style scoped>
/* Основные цвета проекта */
:root {
  --primary-color: #F25C03;
  --bg-secondary: #FFD6BD;
  --text-main: #333333;
}

.event-view {
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
  color: #333333;
  font-family: 'Inter', sans-serif;
}

/* Секция поиска */
.search-section {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  align-items: flex-start;
}

.search-box {
  position: relative;
  flex: 1;
  display: flex;
  gap: 10px;
}

.input-wrapper {
  position: relative;
  flex: 1;
}

input {
  width: 100%;
  padding: 14px 18px;
  border: 2px solid var(--bg-secondary);
  border-radius: 12px;
  font-size: 15px;
  outline: none;
  background-color: #fff;
  transition: all 0.3s ease;
  color: #333333;
}

input:focus {
  border-color: #F25C03;
  box-shadow: 0 0 0 4px rgba(242, 92, 3, 0.1);
}

/* Кнопки */
.btn-primary {
  background-color: #F25C03;
  color: white;
  border: none;
  padding: 0 25px;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background-color: #d14d02;
}

.btn-save {
  background-color: #333333;
  color: #FFD6BD;
  border: none;
  padding: 14px 25px;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  transition: opacity 0.2s;
}

.btn-save:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* Список подсказок */
.custom-suggest {
  display: flex;
  flex-direction: column;
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  background: white;
  border: 1px solid var(--bg-secondary);
  z-index: 1000;
  list-style: none;
  padding: 8px 0;
  margin: 0;
  border-radius: 12px;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.1);
  max-height: 250px;
  overflow-y: auto;
}

.custom-suggest li {
  padding: 12px 20px;
  cursor: pointer;
  font-size: 14px;
  border-bottom: 1px solid #fff5ef;
  transition: background 0.2s;
}

.custom-suggest li:hover {
  background: #FFD6BD;
  color: #F25C03;
}

.city-prefix {
  font-size: 11px;
  text-transform: uppercase;
  color: #F25C03;
  font-weight: bold;
  margin-right: 5px;
}

/* Карта */
.map-wrapper {
  position: relative;
  border-radius: 20px;
  overflow: hidden;
  border: 4px solid var(--bg-secondary);
}

.map-view {
  width: 100%;
  height: 480px;
  background: #fdfdfd;
}

.map-overlay {
  position: absolute;
  inset: 0;
  background: #FFD6BD;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 10;
}

/* Инфо-панель */
.status-panel {
  margin-top: 20px;
  padding: 20px;
  background-color: var(--bg-secondary);
  border-radius: 15px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  border-bottom: 1px solid rgba(242, 92, 3, 0.2);
  padding-bottom: 8px;
}

.label {
  font-weight: 700;
  color: #F25C03;
  font-size: 13px;
  text-transform: uppercase;
}

.value {
  color: #333333;
  font-weight: 500;
}

/* Анимации */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }


/* Убираем синюю рамку фокуса с карты */
:deep(.ymaps-2-1-79-map) {
  outline: none !important;
}

/* Стилизуем полосу прокрутки в подсказках под бренд */
.custom-suggest::-webkit-scrollbar {
  width: 6px;
}
.custom-suggest::-webkit-scrollbar-track {
  background: #FFD6BD;
}
.custom-suggest::-webkit-scrollbar-thumb {
  background: #F25C03;
  border-radius: 10px;
}
</style>
