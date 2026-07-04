<template>
  <n-collapse arrow-placement="right">
    <n-collapse-item :title="title" name="1">
      <div
        v-for="(option, index) in options"
        :key="index"
        class="collapse-content"
      >
        <input
          type="radio"
          :name="name"
          :id="`${name}-${index}`"
          :value="option.value"
          :checked="modelValue === option.value"
          @change="$emit('update:modelValue', option.value)"
          class="radio-input"
        >
        <label :for="`${name}-${index}`" class="radio-label">
          {{ option.label }}
        </label>
      </div>
    </n-collapse-item>
  </n-collapse>
</template>

<script setup>
import { NCollapseItem, NCollapse } from 'naive-ui';
import { ref } from 'vue';

defineProps({
  options: {
    type: Array,
    required: true,
    validator: (value) => value.every(item => item.label && item.value)
  },
  title: String,
  name: {
    type: String,
    required: true
  },
  modelValue: {
    type: String,
    default: null
  }
});

defineEmits(['update:modelValue']);
</script>

<style scoped>
button{
  display: flex;
  justify-content: center;
  align-items: center;
  width: max-content;
  border-radius: 15px;
  padding: 15px 20px;
  color: #333333;
  font-size: 20px;
  background: none;
  border: 1px solid #333333;
}

button:hover{
  background: rgb(226, 223, 223);
}

button:active{
  background-color: rgb(212, 195, 195);
}

.text {
  flex-grow: 1;
  text-align: center;
}

.slot-content{
  max-width: max-content;
  max-height: max-content;
  display: flex;
  align-items: center;
}

input, label{
  cursor: pointer;
}

/* Скрываем стандартный радио-инпут */
.radio-input {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

/* Кастомный стиль для радио-кнопки */
.radio-label {
  position: relative;
  padding-left: 28px;
  cursor: pointer;

  font-size: 20px;
}

/* Создаем кастомный кружок */
.radio-label::before {
  content: "";
  position: absolute;
  left: -15px;
  top: 50%;
  transform: translateY(-50%);
  width: 21px;
  height: 21px;
  border: 2px solid #DFDFDF;
  border-radius: 50%;
  background: white;
  transition: all 0.3s;
}

/* Стиль при выборе (активном состоянии) */
.radio-input:checked + .radio-label::before {
  background: #F25C03;
  border-color: #F25C03;
  box-shadow: inset 0 0 0 3px white; /* Белая точка внутри */
}

.collapse-content{
  min-width: max-content;
  padding: 20px 30px 20px 45px;
  border-radius: 14px;
  box-shadow: 0px 1px 13.8px 0px #00000040;
}

.collapse-content:not(:last-of-type){
  margin-bottom: 20px;
}
</style>
