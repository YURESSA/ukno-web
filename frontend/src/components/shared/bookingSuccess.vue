<template>
  <div class="success-wrapper">
    <h4>Благодарим за бронь!</h4>
    <p>Ваша заявка под номером ID #12345 принята. При обновлении статуса заявки, вам будет отправлено письмо.</p>

    <p>Если сообщение не пришло - напишите в поддержку.</p>
    <div>
      <NButton type="primary"><p>На главную</p></NButton>
    </div>
  </div>
</template>

<script setup>
import { NButton } from 'naive-ui';
</script>

<style scoped>
  .success-wrapper {
    text-align: center;
    display: flex;
    flex-direction: column;
    width: 81%;
    gap: 15px;
    border-radius: 20px;
    box-shadow: 2px 2px 2px 2px rgba(34, 60, 80, 0.2);
    padding: 15px;
    margin: 0 auto;
  }

  button {
    width: 60%;
  }
</style>
