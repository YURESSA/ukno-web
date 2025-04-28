<template>
  <div class="filter-wrapper">
    <div class="filter-header">
      <div class="title">
        <h4>Формат</h4>
      </div>
      <div>
        <button class="close__button"><img src="/icon/filter/close.svg" alt="Закрыть"></button>
      </div>
    </div>
    <div class="filter-main">
      <div class="filter-component">
        <h5>Формат</h5>
        {{ format }}
        <n-checkbox-group v-model:value="format">
          <n-space class="checkbox-group" item-style="display: flex;">
            <n-checkbox size="large" value="Все варианты" label="Все варианты" />
            <n-checkbox size="large" value="Экскурсии" label="Экскурсии" />
            <n-checkbox size="large" value="Мастер-классы" label="Мастер-классы" />
            <n-checkbox size="large" value="Воркшопы" label="Воркшопы" />
            <n-checkbox size="large" value="Выставки" label="Выставки" />
            <n-checkbox size="large" value="Концерты" label="Концерты" />
          </n-space>
        </n-checkbox-group>
      </div>
      <div class="filter-component">
        <h5>Тип экскурсии</h5>
        {{ type }}
        <n-checkbox-group v-model:value="type">
          <n-space class="checkbox-group" item-style="display: flex;">
            <n-checkbox size="large" value="Индивидуальная">
              Индивидуальная<br>
              <span class="type-descript">Личная встреча для вас или для вашей компании</span>
            </n-checkbox>
            <n-checkbox size="large" value="Групповая">
              Групповая<br>
              <span class="type-descript">Вы будете на экскурсии в группе с другими участниками</span>
            </n-checkbox>
            <n-checkbox size="large" value="Мини-группа">
              Мини-группа<br>
              <span class="type-descript">До 10 человек</span>
            </n-checkbox>
          </n-space>
        </n-checkbox-group>
      </div>
      <div class="filter-component">
        <h5>Цена за событие, ₽</h5>
        {{ priceRange }}
        <n-space class="price-slider" vertical>
          <n-space class="price-input">
            <n-input-number v-model:value="priceRange[0]" :step="100" placeholder="Сумма от" size="small" :show-button="false" />
            <n-input-number class="right-input" v-model:value="priceRange[1]" :step="100" placeholder="Сумма до" size="small" :show-button="false" />
          </n-space>
          <n-slider v-model:value="priceRange" range :step="100" :min="0" :max="2000" />
        </n-space>
      </div>
      <div class="filter-component">
        <h5>Возрастная категория</h5>
        {{ AgeCategory }}
        <n-checkbox-group v-model:value="AgeCategory">
          <n-space class="checkbox-group" item-style="display: flex;">
            <n-checkbox size="large" value="Для детей (0-6 лет)">
              Для детей (0-6 лет)
            </n-checkbox>
            <n-checkbox size="large" value="Для школьников (7-17 лет)">
              Для школьников (7-17 лет)
            </n-checkbox>
            <n-checkbox size="large" value="Для взрослых (18+)">
              Для взрослых (18+)
            </n-checkbox>
            <n-checkbox size="large" value="Для всех возрастов (семейные)">
              Для всех возрастов (семейные)
            </n-checkbox>
          </n-space>
        </n-checkbox-group>
      </div>
    </div>
    <div class="interact-button">
      <BaseButton text="Показать"/>
      <DefaultButton class="reset-button" text="Сбросить" icon="" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { NCheckbox, NCheckboxGroup, NSpace, NInputNumber, NSlider } from 'naive-ui'
import BaseButton from '../UI/button/BaseButton.vue'
import DefaultButton from '../UI/button/DefaultButton.vue'

const format = ref(null);
const type = ref(null);
const priceRange = ref([0, 2000])
const AgeCategory = ref(null);
</script>


<style scoped>
.filter-wrapper{
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  max-width: 450px;
  background-color: #FFFFFF;
  padding: 40px 45px;
  box-shadow: 0px 4px 13px 0px #00000040;
  border-radius: 38px;
}

.filter-header{
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  border-bottom: 2px solid #7A797873;
  padding-bottom: 20px;
  margin-bottom: 20px;
}

.filter-main{
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 40px;
}

.filter-component{
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
}

.close__button{
  padding: 6px 6px;
  border-radius: 100%;
  background-color: #EDEDED8A;
}

.close__button:hover{
  background-color: #afaeae8a;
}

.close__button:active{
  background-color: #e7e4e4b7;
}

.checkbox-group{
  flex-direction: column!important;
  gap: 10px!important;
}

.type-descript{
  color: #8C8C8C;
}

.price-slider{
  display: flex;
  flex-direction: column;
  margin: 0 auto;
  width: 350px;
}

.price-input{
  display: flex;
  justify-content: center!important;
  gap: 0!important;
  border-radius: 0 0 0 0!important;
  margin-bottom: 20px;
}

.interact-button{
  display: flex;
  justify-content: space-between;
  width: 100%;
  margin-top: 40px;
}

.reset-button{
  width: 226;
  height: 45;
  border-radius: 15px;
  padding: 10px 50px;
  color: #000000;
  font-weight: 400;
  font-size: 20px;
}

:deep(.n-checkbox__label){
  font-weight: 600;
  font-size: 20px;
}

:deep(.n-slider-rail__fill){
  --n-fill-color: #F25C03;
  --n-fill-color-hover: #F25C03;
  --n-fill-color-focus: #F25C03;
}

:deep(.n-slider-handle){
  border: 7px solid #F25C03;
}

:deep(.n-input-number){
  width: 175px;
}

:deep(.n-input-wrapper){
  height: 52px;
  display: flex;
  justify-content: center;
  align-items: center;
}

:deep(.n-input){
  border-radius: 0px;
  --n-border: 1px solid #BABABA;
  --n-border-hover: 2px solid #F25C03 !important;
  --n-border-focus: 2px solid #F25C03 !important;
  --n-box-shadow-focus: none!important;
  --n-font-size: 20px!important;
  transition: all 0.25s ease;
}

:deep(.n-input__input-el){
  font-weight: 600;
  text-align: center;
}

:deep(.n-checkbox-box){
  --n-color-checked: #F25C03;
}
</style>
