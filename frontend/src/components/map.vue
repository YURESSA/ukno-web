<template>
  <div class="interactive-map-container">
    <div class="map-wrapper">
      <!-- Основное изображение карты -->
      <img
        ref="mapImage"
        src="/assets/map.jpg"
        alt="План помещения"
        class="map-image"
        @load="onImageLoad"
      />

      <!-- SVG overlay для полигонов -->
      <svg
        v-if="imageSize.width > 0"
        class="hotspots-overlay"
        :viewBox="`0 0 ${imageSize.naturalWidth} ${imageSize.naturalHeight}`"
        :style="{
          width: imageSize.width + 'px',
          height: imageSize.height + 'px'
        }"
      >
        <!-- Полигоны -->
        <polygon
          v-for="area in polyAreas"
          :key="area.id"
          :points="area.coords.join(',')"
          class="hotspot-polygon"
          :class="{ 'hotspot-hovered': hoveredArea === area.id }"
          @mouseover="handleAreaHover(area.id)"
          @mouseout="handleAreaOut"
          @click="handleAreaClick(area.id)"
        />
      </svg>

      <!-- Rect области поверх SVG -->
      <div
        v-for="area in rectAreas"
        :key="area.id"
        class="hotspot-rect"
        :class="{ 'hotspot-hovered': hoveredArea === area.id }"
        :style="getRectStyle(area)"
        @mouseover="handleAreaHover(area.id)"
        @mouseout="handleAreaOut"
        @click="handleAreaClick(area.id)"
      ></div>

      <!-- Всплывающая подсказка -->
      <div
        v-if="tooltip.visible && hoveredArea"
        class="tooltip"
        :style="{
          left: tooltip.x + 'px',
          top: tooltip.y + 'px'
        }"
      >
        {{ getAreaTitle(hoveredArea) }}
      </div>
    </div>

    <!-- Панель информации о выбранной зоне -->
    <div v-if="selectedArea" class="info-panel">
      <h3>Информация о помещении</h3>
      <div class="info-content">
        <h4>{{ selectedArea.title }}</h4>
        <p v-if="selectedArea.description">{{ selectedArea.description }}</p>
        <p v-if="selectedArea.area"><strong>Площадь:</strong> {{ selectedArea.area }} м²</p>
        <p v-if="selectedArea.capacity"><strong>Вместимость:</strong> {{ selectedArea.capacity }} чел.</p>
        <p v-if="selectedArea.equipment"><strong>Оборудование:</strong> {{ selectedArea.equipment }}</p>
      </div>
      <button @click="selectedArea = null" class="close-btn">Закрыть</button>
    </div>
  </div>
  <Footer></Footer>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue';
import Footer from './shared/footer.vue';

// Состояния
const hoveredArea = ref(null);
const selectedArea = ref(null);
const debugMode = ref(true);
const mapImage = ref(null);

// Размеры изображения
const imageSize = reactive({
  width: 0,
  height: 0,
  naturalWidth: 0,
  naturalHeight: 0
});

// Данные для тултипа
const tooltip = reactive({
  visible: false,
  x: 0,
  y: 0
});

// Оригинальные координаты
const originalAreas = ref([
  {
    id: 'event_hall',
    shape: 'poly',
    coords: [406,434,678,426,677,318,596,313,596,229,402,232,403,290],
    title: 'Событийный зал',
    description: 'Многофункциональный зал оборудованный мультимедийной техникой',
    area: 120,
    capacity: 80,
    equipment: 'Проектор, экран, звуковая система'
  },
  {
    id: 'children',
    shape: 'poly',
    coords: [159,232,156,99,305,94,310,233,160,233],
    title: 'Абонемент для детей',
    description: 'Игровая комната',
    area: 45,
    capacity: 20,
    equipment: 'Игры, книги, развивающие материалы'
  },
  {
    id: 'wardrobe',
    shape: 'poly',
    coords: [159,294,158,242,219,241,220,294,192,295],
    title: 'Гардеробная',
    description: 'Место для хранения вашей верхней одежды',
    area: 15,
    capacity: 50,
    equipment: 'Вешалки, полки'
  },
  {
    id: 'subscription',
    shape: 'poly',
    coords: [323,227,319,97,594,98,595,225,322,231],
    title: 'Абонемент',
    description: 'Загадочное пространство, приходи и узнай сам!',
    area: 85,
    capacity: 25,
    equipment: 'Компьютеры, принтер'
  },
  {
    id: 'reading_hall',
    shape: 'poly',
    coords: [322,235,397,234,403,431,324,434],
    title: 'Читальный зал',
    description: 'Пространство для чтения, стилизованное под вагон поезда',
    area: 65,
    capacity: 30,
    equipment: 'Столы, стулья, книги'
  },
  {
    id: 'books_room',
    shape: 'rect',
    coords: [611,259,682,299],
    title: 'Хранилище книг',
    description: 'Спальная комната книг, просьба беспокоить как можно чаще!',
    area: 25,
    capacity: 5,
    equipment: 'Стеллажи, книги'
  },
  {
    id: 'youth_room',
    shape: 'rect',
    coords: [694,258,924,433],
    title: 'Молодёжный зал',
    description: 'Многофункциональный зал с амфитеатром',
    area: 150,
    capacity: 60,
    equipment: 'Амфитеатр, мультимедиа'
  },
  {
    id: 'arts_room',
    shape: 'rect',
    coords: [692,139,924,247],
    title: 'Зал искусств',
    description: 'Арт-галерея, многофункциональное пространство',
    area: 120,
    capacity: 40,
    equipment: 'Выставочное пространство'
  },
  {
    id: 'media',
    shape: 'rect',
    coords: [693,50,784,133],
    title: 'Медиа среда',
    description: 'Здесь создаются инфо поводы!',
    area: 35,
    capacity: 10,
    equipment: 'Компьютеры, фотоаппаратура'
  },
  {
    id: 'project_office',
    shape: 'rect',
    coords: [792,52,921,132],
    title: 'Проектный офис',
    description: 'Место где идея становиться реальностью!',
    area: 40,
    capacity: 8,
    equipment: 'Столы, доска для планирования'
  }
]);

// Разделяем области на полигоны и прямоугольники
const polyAreas = computed(() => {
  return originalAreas.value.filter(area => area.shape === 'poly');
});

const rectAreas = computed(() => {
  return originalAreas.value.filter(area => area.shape === 'rect');
});

// Стили для прямоугольников
const getRectStyle = (area) => {
  if (!imageSize.naturalWidth || !imageSize.naturalHeight) return {};

  const scaleX = imageSize.width / imageSize.naturalWidth;
  const scaleY = imageSize.height / imageSize.naturalHeight;

  const [x1, y1, x2, y2] = area.coords;

  return {
    left: Math.round(x1 * scaleX) + 'px',
    top: Math.round(y1 * scaleY) + 'px',
    width: Math.round((x2 - x1) * scaleX) + 'px',
    height: Math.round((y2 - y1) * scaleY) + 'px'
  };
};

// Получение заголовка зоны
const getAreaTitle = (areaId) => {
  const area = originalAreas.value.find(a => a.id === areaId);
  return area ? area.title : '';
};

// Обработчики событий
const handleAreaHover = (areaId) => {
  hoveredArea.value = areaId;
  tooltip.visible = true;
};

const handleAreaOut = () => {
  tooltip.visible = false;
  hoveredArea.value = null;
};

const handleAreaClick = (areaId) => {
  const area = originalAreas.value.find(a => a.id === areaId);
  if (area) {
    selectedArea.value = area;
    console.log('Выбрана область:', area.title);
  }
};

// Отслеживание движения курсора для тултипа
const handleMouseMove = (event) => {
  if (tooltip.visible) {
    tooltip.x = event.clientX + 15;
    tooltip.y = event.clientY - 30;
  }
};

// Когда изображение загружено
const onImageLoad = () => {
  if (mapImage.value) {
    imageSize.width = mapImage.value.offsetWidth;
    imageSize.height = mapImage.value.offsetHeight;
    imageSize.naturalWidth = mapImage.value.naturalWidth;
    imageSize.naturalHeight = mapImage.value.naturalHeight;

    console.log('✅ Изображение загружено');
    console.log('📏 Текущий размер:', imageSize.width, 'x', imageSize.height);
    console.log('📐 Оригинальный размер:', imageSize.naturalWidth, 'x', imageSize.naturalHeight);
    console.log('📍 Полигоны:', polyAreas.value.length);
    console.log('📍 Прямоугольники:', rectAreas.value.length);
  }
};

// Переключение режима отладки
const toggleDebug = () => {
  debugMode.value = !debugMode.value;
};

// Инициализация
onMounted(() => {
  document.addEventListener('mousemove', handleMouseMove);
});
</script>

<style scoped>
.interactive-map-container {
  display: flex;
  gap: 20px;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.map-wrapper {
  position: relative;
  flex: 3;
}

.map-image {
  width: 100%;
  height: auto;
  border: 2px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  display: block;
}

/* SVG overlay для полигонов */
.hotspots-overlay {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
}

.hotspots-overlay * {
  pointer-events: all;
}

/* Стили для полигонов в SVG */
.hotspot-polygon {
  fill: transparent;
  stroke: transparent;
  cursor: pointer;
  transition: all 0.3s ease;
}

.hotspot-polygon:hover {
  fill: rgba(33, 150, 243, 0.3);
  stroke: #2196F3;
  stroke-width: 2;
}

.hotspot-polygon.hotspot-hovered {
  fill: rgba(33, 150, 243, 0.5) !important;
  stroke: #2196F3 !important;
  stroke-width: 2 !important;
}

/* Стили для прямоугольников */
.hotspot-rect {
  position: absolute;
  background: transparent;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.3s ease;
  pointer-events: all;
}

.hotspot-rect:hover {
  background: rgba(33, 150, 243, 0.3);
  border-color: #2196F3;
}

.hotspot-rect.hotspot-hovered {
  background: rgba(33, 150, 243, 0.5) !important;
  border-color: #2196F3 !important;
}

/* Стили для тултипа */
.tooltip {
  position: fixed;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 14px;
  pointer-events: none;
  z-index: 1000;
  white-space: nowrap;
}

/* Панель информации */
.info-panel {
  flex: 1;
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
  border: 1px solid #ddd;
  min-width: 250px;
}

.info-content h4 {
  margin: 0 0 10px 0;
  color: #333;
}

.info-content p {
  margin: 5px 0;
  font-size: 14px;
  color: #666;
}

.close-btn {
  margin-top: 15px;
  padding: 8px 16px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.close-btn:hover {
  background: #0056b3;
}

/* Медиа-запросы для мобильных устройств */
@media (max-width: 768px) {
  .interactive-map-container {
    flex-direction: column;
  }

  .info-panel {
    min-width: auto;
  }

  .debug-info {
    position: relative;
    bottom: auto;
    left: auto;
    margin-top: 20px;
  }
}
</style>
