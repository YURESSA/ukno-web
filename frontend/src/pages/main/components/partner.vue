<template>
  <div class="container">
    <h3>Партнёры</h3>

    <div class="partners-block">
      <a
        v-for="partner in sortedPartners"
        :key="partner.id"
        :href="partner.link"
        target="_blank"
        rel="noopener noreferrer"
        class="partner-link"
      >
        <img :src="baseUrl + partner.photo" :alt="partner.name">
      </a>
    </div>
  </div>
</template>

<script setup>
import { baseUrl } from '@/stores/counter';
import { computed } from 'vue';

const props = defineProps({
  partners: {
    type: Array,
    default: () => []
  }
})

const sortedPartners = computed(() => {
  if (!props.partners.length) return [];
  return [...props.partners].sort((a, b) => a.order_index - b.order_index);
})
</script>

<style scoped>
.partners-block {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 70px;
  border-radius: 36px;
  padding: 45px 0;
}

.partner-link {
  display: block;
  transition: opacity 0.3s;
}

.partner-link:hover {
  opacity: 0.8;
}

.partners-block img {
  width: 241px;
  height: 88px;
  object-fit: contain;
}

.container {
  margin: 0 auto;
  max-width: 1800px;
}

h3 {
  margin-bottom: 30px;
}

@media (max-width: 756px) {
  h3 {
    margin-bottom: 20px;
  }
  .partners-block img {
    width: 68px;
    height: 57px;
  }
  .partners-block {
    gap: 24px;
    padding: 20px 0;
  }
}
</style>
