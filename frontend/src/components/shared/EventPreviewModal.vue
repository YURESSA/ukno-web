<template>
  <n-modal :show="show" preset="card" title="Предпросмотр события" class="event-preview-modal"
    style="width: min(1180px, calc(100vw - 32px)); max-height: calc(100dvh - 32px)"
    :content-style="{ overflowY: 'auto', minHeight: '0' }" @update:show="value => emit('update:show', value)">
    <p class="preview-notice">Показаны текущие правки. Предпросмотр ничего не сохраняет и не публикует. Запись на событие недоступна.</p>
    <EventPage v-if="show" :preview-event="previewEvent" />
  </n-modal>
</template>

<script setup>
import { computed } from 'vue'
import { NModal } from 'naive-ui'
import EventPage from '@/pages/eventPage/eventPage.vue'
const props = defineProps({ show: Boolean, event: { type: Object, required: true } })
const emit = defineEmits(['update:show'])
const previewEvent = computed(() => ({
  ...props.event,
  title: props.event.title || 'Название события',
  description: props.event.description || '',
  duration: props.event.duration || 0,
  category: props.event.category || { category_name: 'Категория не выбрана' },
  format_type: props.event.format_type || { format_type_name: 'Формат не выбран' },
  age_category: props.event.age_category || { age_category_name: 'Возраст не указан' },
  photos: props.event.photos || [],
  sessions: (props.event.sessions || []).map((session, index) => ({
    ...session,
    session_id: session.session_id ?? `preview-${index}`,
    available: session.available ?? Math.max(0, (session.max_participants || 0) - (session.booked || 0)),
  })),
}))
</script>

<style scoped>
.preview-notice { padding: 12px 16px; border-radius: 10px; background: #f5f5f5; color: #666; font-size: 13px; line-height: 1.5; }
</style>
