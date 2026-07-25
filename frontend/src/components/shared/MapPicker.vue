<template>
  <div class="map-picker">
    <!-- Поиск по адресу -->
    <div class="map-search-row">
      <div class="map-input-wrapper">
        <input
          type="text"
          v-model="eventAddress"
          @input="handleInput"
          placeholder="Введите адрес..."
          autocomplete="off"
          :class="{ 'has-suggestions': suggestions.length }"
        />
        <transition name="fade">
          <ul v-if="suggestions.length" class="map-suggest">
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
      <button type="button" @click="geocodeByText" :disabled="!isMapInitialized" class="map-btn-search">
        Найти
      </button>
    </div>

    <!-- Подсказка -->
    <p class="map-hint">
      <span v-if="coords">
        📍 {{ eventAddress || 'Адрес не определён' }}
        &nbsp;·&nbsp;
        {{ coords[0].toFixed(5) }}, {{ coords[1].toFixed(5) }}
      </span>
      <span v-else>Кликните по карте или найдите адрес, чтобы выбрать место</span>
    </p>

    <!-- Контейнер карты -->
    <div class="map-wrapper">
      <div :id="mapId" class="map-view"></div>
      <div v-if="!isMapInitialized" class="map-overlay">
        <div class="map-spinner"></div>
        <p>{{ loadingStatus }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
/* global ymaps */
import { onMounted, onUnmounted, ref, shallowRef, watch } from 'vue';
import { useDataStore } from '@/stores/counter';

const props = defineProps({
  /** Начальные координаты [lat, lon] — для режима редактирования */
  initialCoords: {
    type: Array,
    default: null,
  },
  /** Уникальный id контейнера карты (нужен если несколько MapPicker на странице) */
  mapId: {
    type: String,
    default: 'map-picker-container',
  },
});

const emit = defineEmits(['update:coords']);

const store = useDataStore();

const eventAddress = ref('');
const coords = ref(null);
const suggestions = ref([]);
const isMapInitialized = ref(false);
const loadingStatus = ref('Загрузка карты...');

const myMap = shallowRef(null);
const myPlacemark = shallowRef(null);

let debounceTimer = null;

const API_KEY = import.meta.env.VITE_YANDEX_API_KEY;
const BACKEND_URL = import.meta.env.VITE_FRONTEND_URL;

onMounted(() => {
  window.initYandexMapCallback = initMap;

  if (window.ymaps && window.ymaps.Map) {
    // ymaps уже загружен другой страницей — просто инициализируем
    initMap();
    return;
  }

  if (document.querySelector('script[src*="api-maps.yandex.ru"]')) {
    // Скрипт уже добавлен, ждём колбэк
    return;
  }

  const script = document.createElement('script');
  script.type = 'text/javascript';
  script.src = `https://api-maps.yandex.ru/2.1/?apikey=${API_KEY}&lang=ru_RU&load=package.full&onload=initYandexMapCallback`;
  script.onerror = () => {
    loadingStatus.value = 'Ошибка загрузки карты. Проверьте API ключ.';
  };
  document.head.appendChild(script);
});

function initMap() {
  const container = document.getElementById(props.mapId);
  if (!container) return;

  try {
    myMap.value = new ymaps.Map(
      container,
      {
        center: props.initialCoords ?? [56.8389, 60.6057], // Екатеринбург по умолчанию
        zoom: props.initialCoords ? 16 : 13,
        controls: ['zoomControl'],
      },
      { yandexMapDisablePoiInteractivity: true }
    );

    // Если переданы начальные координаты — сразу поставить маркер
    if (props.initialCoords) {
      updateMarker(props.initialCoords, false);
      reverseGeocode(props.initialCoords);
    }

    myMap.value.events.add('click', (e) => {
      const clickCoords = e.get('coords');
      updateMarker(clickCoords);
      reverseGeocode(clickCoords);
    });

    isMapInitialized.value = true;
  } catch (e) {
    console.error('Ошибка при создании карты:', e);
    loadingStatus.value = 'Ошибка: ' + e.message;
  }
}

function handleInput() {
  clearTimeout(debounceTimer);
  suggestions.value = [];
  if (eventAddress.value.length < 3) return;

  debounceTimer = setTimeout(async () => {
    const url = `${BACKEND_URL}api/yandex/map-helper?suggest=${encodeURIComponent(eventAddress.value)}`;
    try {
      const response = await fetch(url, {
        headers: {
          Authorization: `Bearer ${store.auth_key}`,
          'Content-Type': 'application/json',
        },
      });
      if (!response.ok) throw new Error('Backend error');
      const data = await response.json();
      if (data.results) {
        suggestions.value = data.results.map((item) => ({
          displayName:
            item.title.text + (item.subtitle ? ', ' + item.subtitle.text : ''),
          value:
            item.title.text + (item.subtitle ? ', ' + item.subtitle.text : ''),
        }));
      }
    } catch (e) {
      console.error('Ошибка Suggest API:', e);
    }
  }, 600);
}

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

function geocodeByText() {
  if (!eventAddress.value || !window.ymaps) return;
  ymaps.geocode(eventAddress.value, { results: 1 }).then((res) => {
    const obj = res.geoObjects.get(0);
    if (obj) {
      const foundCoords = obj.geometry.getCoordinates();
      updateMarker(foundCoords);
      myMap.value.setCenter(foundCoords, 16);
    }
  });
}

function reverseGeocode(c) {
  ymaps.geocode(c).then((res) => {
    const obj = res.geoObjects.get(0);
    if (obj) {
      eventAddress.value = obj.getAddressLine();
    }
  });
}

/**
 * @param {Array} newCoords  - [lat, lon]
 * @param {boolean} doEmit   - эмитить ли событие (false при начальной инициализации)
 */
function updateMarker(newCoords, doEmit = true) {
  coords.value = newCoords;

  if (myPlacemark.value) {
    myPlacemark.value.geometry.setCoordinates(newCoords);
  } else {
    myPlacemark.value = new ymaps.Placemark(
      newCoords,
      { balloonContent: 'Место проведения мероприятия' },
      {
        iconColor: '#F25C03',
        preset: 'islands#dotIcon',
        hasHint: false,
        draggable: true,
      }
    );

    // Перетаскивание маркера тоже обновляет координаты
    myPlacemark.value.events.add('dragend', () => {
      const draggedCoords = myPlacemark.value.geometry.getCoordinates();
      coords.value = draggedCoords;
      reverseGeocode(draggedCoords);
      emitCoords(draggedCoords);
    });

    myMap.value.geoObjects.add(myPlacemark.value);
  }

  if (doEmit) emitCoords(newCoords);
}

function emitCoords(c) {
  emit('update:coords', {
    latitude: c[0],
    longitude: c[1],
    address: eventAddress.value,
  });
}

onUnmounted(() => {
  if (myMap.value) myMap.value.destroy();
  delete window.initYandexMapCallback;
  clearTimeout(debounceTimer);
});
</script>

<style scoped>
.map-picker {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* Строка поиска */
.map-search-row {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.map-input-wrapper {
  position: relative;
  flex: 1;
}

.map-input-wrapper input {
  width: 100%;
  padding: 14px 18px;
  border: 2px solid #FFD6BD;
  border-radius: 10px;
  font-size: 14px;
  outline: none;
  font-family: 'Manrope', sans-serif;
  transition: border-color 0.3s, box-shadow 0.3s;
  color: #333;
  box-sizing: border-box;
}

.map-input-wrapper input:focus {
  border-color: #F25C03;
  box-shadow: 0 0 0 3px rgba(242, 92, 3, 0.12);
}

.map-btn-search {
  background-color: #F25C03;
  color: #fff;
  border: none;
  padding: 14px 24px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  font-family: 'Manrope', sans-serif;
  font-size: 14px;
  transition: background 0.2s;
  white-space: nowrap;
}

.map-btn-search:hover:not(:disabled) {
  background-color: #d14d02;
}

.map-btn-search:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

/* Подсказки */
.map-suggest {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  background: #fff;
  border: 1px solid #FFD6BD;
  z-index: 999;
  list-style: none;
  padding: 6px 0;
  margin: 0;
  border-radius: 10px;
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.09);
  max-height: 230px;
  overflow-y: auto;
}

.map-suggest li {
  padding: 11px 18px;
  cursor: pointer;
  font-size: 13px;
  font-family: 'Manrope', sans-serif;
  border-bottom: 1px solid #fff5ef;
  transition: background 0.15s;
  color: #333;
}

.map-suggest li:hover {
  background: #FFD6BD;
  color: #F25C03;
}

.map-suggest::-webkit-scrollbar { width: 5px; }
.map-suggest::-webkit-scrollbar-track { background: #FFD6BD; }
.map-suggest::-webkit-scrollbar-thumb { background: #F25C03; border-radius: 8px; }

/* Подсказка под строкой поиска */
.map-hint {
  font-size: 12px;
  color: #9E9E9E;
  margin: 0;
  font-family: 'Manrope', sans-serif;
  min-height: 18px;
}

/* Карта */
.map-wrapper {
  position: relative;
  border-radius: 14px;
  overflow: hidden;
  border: 2px solid #FFD6BD;
}

.map-view {
  width: 100%;
  height: 360px;
  background: #fdfdfd;
}

.map-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255, 214, 189, 0.75);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 10;
  gap: 12px;
  font-family: 'Manrope', sans-serif;
  color: #333;
}

.map-spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #FFD6BD;
  border-top-color: #F25C03;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Убираем синий outline фокуса с карты */
:deep([class*="-map"]) {
  outline: none !important;
}

/* Анимация списка подсказок */
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
