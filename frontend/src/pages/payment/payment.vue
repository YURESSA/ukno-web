  <template>
    <div class="page-wrapper">
      <div class="payment-wrapper">
        <Header :title="excursion.title"/>
        <div class="booked-form">
          <div class="person-info">
            <form @submit.prevent="handleSubmit">
              <h5>Введите информацию для бронирования билета</h5>
              <input
                type="name"
                name="full_name"
                placeholder="Имя и фамилия"
                v-model="formData.full_name"
                autocomplete="name"
                @input="clearError('full_name')"
              >
              <span class="error-message">{{ errors.full_name }}</span>
              <input
                type="tel"
                name="phone_number"
                placeholder="Номер телефона"
                v-model="formData.phone_number"
                autocomplete="off"
                @input="clearError('phone_number')"
              >
              <span class="error-message">{{ errors.phone_number }}</span>
              <input
                type="email"
                name="email"
                placeholder="e-mail"
                v-model="formData.email"
                autocomplete="off"
                @input="clearError('email')"
              >
              <span class="error-message">{{ errors.email }}</span>
              <div class="participants-input">
                <span>Количество участников</span>
                <div class="participants">
                  <IconButton class="participants--btn left--btn" type="button" @click="minusParticipants" text="-"/>
                  <input v-model="formData.participants_count" @input="validateParticipants"/>
                  <IconButton class="participants--btn right--btn" type="button" @click="plusParticipants" text="+"/>
                </div>
              </div>
              <h5>Итого к оплате: {{ formData.participants_count * excursion.sessions[0].cost }}</h5>
              <BaseButton type="submit" class="sumbit--btn" text="Забронировать"/>
              <span class="offer">Нажимая «Забронировать», вы соглашаетесь с условиями приобретения и офертой</span>
            </form>
          </div>
        </div>
      </div>
    </div>
  </template>

  <script setup>
  import Header from './components/header.vue';
  import BaseButton from '@/components/UI/button/BaseButton.vue';
  import IconButton from '@/components/UI/button/IconButton.vue';
  import { useDataStore } from '@/stores/counter';
  import { onMounted, computed, ref } from 'vue';
  import { useRoute, useRouter } from 'vue-router';

  const store = useDataStore();
  const route = useRoute();
  const router = useRouter();

  const excursion = computed(() => store.getExcursionDetail);
  const userData = computed(() => store.getProfileData);

  const showErrors = ref(false);

  const formData = ref({
    session_id: route.params.id,
    full_name: userData.value.full_name,
    phone_number: userData.value.phone,
    email: userData.value.email,
    participants_count: 1,
  });

  const errors = ref({
    full_name: '',
    phone_number: '',
    email: '',
  });

  const load = ref(false)

  onMounted(async () => {
    try {
      await store.FetchExcursionDetail(route.query.excursion_id);
      setTimeout(() => {
        load.value = true
      }, 1000)
      console.log(excursion.value)
    } catch (error) {
      console.error('Ошибка при загрузке экскурсий:', error);
      alert('Произошла ошибка, попробуйте ещё раз')
    }
  });

  function validateParticipants(){
    if(formData.value.participants_count < 1){
      formData.value.participants_count = 1
    }
  }

  function minusParticipants(){
    if (formData.value.participants_count > 1){
      formData.value.participants_count -= 1;
    }
  }

  function plusParticipants(){
    formData.value.participants_count += 1;
  }


  const clearError = (field) => {
    errors.value[field] = '';
  };

  // Валидация ФИО
  const validateName = () =>{
    if(formData.value.full_name < 3){
      errors.value.full_name = 'Введите корректные ФИО';
    } else{
      errors.value.full_name = ''
    }
  }

  // Валидация email
  const validateEmail = () => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.value.email)) {
      errors.value.email = 'Введите корректный email';
    } else {
      errors.value.email = '';
    }
  };

  // Валидация телефона
  const validatePhone = () => {
    const phoneRegex = /^(\+7|8)[0-9]{10}$/;
    const cleanPhone = formData.value.phone_number.replace(/[^\d+]/g, '');

    if (!phoneRegex.test(cleanPhone)) {
      errors.value.phone_number = 'Введите корректный номер телефона';
    } else {
      errors.value.phone_number = '';
    }
    formData.value.phone_number = cleanPhone;
  };

  const handleSubmit = async () => {
    showErrors.value = true;

    // Проверяем все поля перед отправкой
    validateName();
    validateEmail();
    validatePhone();

    // Проверяем наличие ошибок
    const hasErrors = Object.values(errors.value).some(error => error !== '');

    if (hasErrors) {
      return;
    }
    console.log(JSON.stringify(formData.value))
    try {
      await store.PostReservation(JSON.stringify(formData.value));
      alert('Бронирование прошло успешно!');
      router.push('/profile');
    } catch (error) {
      console.error('Ошибка бронировании', error);
    }
  };
  </script>

  <style scoped>
  .page-wrapper {
    display: flex;
    justify-content: center;
    position: relative;
    min-height: calc(100vh - 100px);
  }

  .payment-wrapper{
    width: 100%;
    max-width: 1800px;
  }

  .booked-form{
    margin-top: 30px;
  }

  .person-info {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    max-width: 1800px;
    position: relative;
  }

  h5{
    margin-bottom: 40px;
  }

  form {
    display: flex;
    flex-direction: column;
    min-width: 300px;
    max-width: 400px;
    margin-bottom: 30px;
  }

  input {
    font-size: 16px;
    padding: 15px 0;
    border: 2px solid #2C2C2C24;
    border-radius: 8px;
    padding-left: 20px;
    transition: all 0.5s ease;
  }

  input:focus {
    outline: none;
    background-color: #F3F3F3;
  }

  .participants-input{
    display: flex;
    flex-direction: column;
    gap: 10px;
    color: #9E9E9E;
  }

  .participants{
    display: flex;
    max-width: 150px;
    margin-bottom: 40px;
  }

  .participants > input {
    width: 45px;
    padding: 0;
    border: none;
    text-align: center;
    border: 2px solid #E2E2E2;
    border-width: 2px 0;
    border-radius: 0;
  }

  .participants--btn{
    border: 2px solid #E2E2E2;
    padding: 10px 16px;
    border-radius: 12px 0 0 12px;
  }

  .left--btn{
    border-radius: 12px 0 0 12px;
  }

  .right--btn{
    border-radius: 0 12px 12px 0;
  }

  .text-orange{
    color: #F25C03;
  }

  .error-message {
    color: red;
    height: 30px;
    font-size: 20px;
    margin: 5px;
    font-weight: 700;
    display: block;
  }

  .sumbit--btn{
    margin-bottom: 15px;
  }

  .offer{
    color: #A9A9A9;
  }
  </style>
