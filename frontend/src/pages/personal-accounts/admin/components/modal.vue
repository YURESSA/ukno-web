<template>
  <n-modal v-model:show="showModel" :mask-closable="maskClosable">
    <n-card class="modal-card" :bordered="false" size="large">
      <template #header>
        <div class="modal-title">
          <div class="modal-title-left">
            <n-icon v-if="icon" :size="22">
              <component :is="icon" />
            </n-icon>
            <span>{{ title }}</span>
          </div>

          <n-button quaternary circle @click="showModel = false">
            <n-icon :size="18"><component :is="CloseIcon" /></n-icon>
          </n-button>
        </div>
      </template>

      <!-- сюда родитель вставит форму -->
      <slot></slot>

      <template #footer>
        <!-- можно переопределить футер полностью -->
        <slot name="footer">
          <div class="modal-footer">
            <n-button @click="showModel = false">Отмена</n-button>
            <n-button type="primary" @click="$emit('submit')">Сохранить</n-button>
          </div>
        </slot>
      </template>
    </n-card>
  </n-modal>
</template>

<script setup>
import { computed } from 'vue'
import { defineEmits } from 'vue'
import { NModal, NCard, NButton, NIcon } from 'naive-ui'
import { CloseOutline as CloseIcon } from '@vicons/ionicons5'

const props = defineProps({
  show: Boolean,                 // v-model:show
  title: { type: String, default: '' },
  icon: { type: [Object, Function], default: null }, // компонент иконки
  maskClosable: { type: Boolean, default: false },
  width: { type: [Number, String], default: 900 }
})

// defineEmits(['update:show', 'submit'])

const showModel = computed({
  get: () => props.show,
  set: (v) => emit('update:show', v)
})

const emit = defineEmits(['update:show', 'submit'])
</script>

<style scoped>
.modal-card {
  width: v-bind(width);
  max-width: calc(100vw - 32px);
}
.modal-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.modal-title-left {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
}
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
