<template>
  <div class="page-wrapper">
    <div class="login-wrapper">
      <form @submit.prevent="handleSubmit" autocomplete="off">
        <h3>Регистрация</h3>
        <input
          type="text"
          name="full_name"
          placeholder="Фамилия Имя *"
          class="text-l text-medium"
          v-model="formData.full_name"
          required
          autocomplete="off"
          @input="clearError('full_name')"
        >
        <span class="error-message" v-if="showErrors && errors.full_name">{{ errors.full_name }}</span>
        <input
          type="tel"
          name="phone"
          placeholder="+7 (___) ___-__-__"
          class="text-l text-medium"
          v-model="formData.phone"
          required
          autocomplete="off"
          @input="formatPhoneInput"
          @blur="validatePhone"
        >
        <span class="error-message" v-if="showErrors && errors.phone">{{ errors.phone }}</span>

        <input
          type="email"
          name="email"
          placeholder="E-mail *"
          class="text-l text-medium"
          v-model="formData.email"
          required
          autocomplete="off"
          @input="clearError('email')"
        >
        <span class="error-message" v-if="showErrors && errors.email">{{ errors.email }}</span>

        <input
          type="password"
          name="password"
          placeholder="Пароль *"
          class="text-l text-medium"
          v-model="formData.password"
          required
          autocomplete="new-password"
          @input="clearError('password')"
          minlength="5"
        >
        <span class="error-message" v-if="showErrors && errors.password">{{ errors.password }}</span>

        <input
          type="password"
          name="passwordConfirmation"
          placeholder="Повторите пароль *"
          class="text-l text-medium"
          v-model="formData.passwordConfirmation"
          required
          autocomplete="new-password"
          @input="clearError('passwordConfirmation')"
        >
        <span class="error-message" v-if="showErrors && errors.passwordConfirmation">{{ errors.passwordConfirmation }}</span>

        <DefaultButton type="submit" class="sumbit--btn" text="Зарегистрироваться"/>
        <span>Нажимая кнопку „Зарегистрироваться“, вы соглашаетесь с
          <span class="text-orange">
            <a
              :href="baseUrl+requisites[0].file"
              class="text-orange"
              target="blank"
              v-if="personalDataFile">
                обработкой персональных данных
              </a>
            <a
              href="https://ukno.ru/wp-content/uploads/2024/10/politika_v_otnoshenii_obrabotki_personalnyh_dannyh_ukno.pdf"
              class="text-orange"
              target="blank"
              v-else>
                обработкой персональных данных
            </a>
          </span>
        </span>
        <span class="bold">У ВАС УЖЕ ЕСТЬ АККАУНТ? <RouterLink to="login"><span class="text-orange">ВОЙТИ</span></RouterLink></span>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import DefaultButton from '@/components/ui/button/DefaultButton.vue';
import { useDataStore, baseUrl } from '@/stores/counter';
import router from '@/router';
import { notification } from '@/utils/notification'

const store = useDataStore();
const showErrors = ref(false);
const requisites = computed(() => store.getRequisites);

const personalDataFile = computed(() => {
  if (Array.isArray(requisites.value)) {
    return requisites.value.find(item => item.title === "Обработка персональных данных");
  }
  return null;
});

onMounted(() => {
  store.FetchRequisites()
})

const formData = ref({
  phone: '',
  email: '',
  password: '',
  full_name: '',
  role_name: 'user'
});

const errors = ref({
  phone: '',
  email: '',
  password: '',
  passwordConfirmation: ''
});

const clearError = (field) => {
  errors.value[field] = '';
};

const validateName = () =>{
  if(formData.value.full_name < 3){
    errors.value.full_name = 'Введите корректные ФИО';
  } else{
    errors.value.full_name = ''
  }
}

const validateEmail = () => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(formData.value.email)) {
    errors.value.email = 'Введите корректный email';
  } else {
    errors.value.email = '';
  }
};

const formatPhoneInput = (event) => {
  let value = event.target.value.replace(/\D/g, '');

  if (value.startsWith('7') || value.startsWith('8')) {
    value = '+7' + value.substring(1);
  } else if (!value.startsWith('+7')) {
    value = '+7' + value;
  }

  let formatted = value;
  if (value.length > 2) {
    formatted = value.substring(0, 2) + ' ' + value.substring(2, 5);
  }
  if (value.length > 5) {
    formatted += ' ' + value.substring(5, 8);
  }
  if (value.length > 8) {
    formatted += '-' + value.substring(8, 10);
  }
  if (value.length > 10) {
    formatted += '-' + value.substring(10, 12);
  }

  formData.value.phone = formatted;
  clearError('phone');
};

const validatePhone = () => {
  const cleanPhone = formData.value.phone.replace(/[\s\-()]/g, '');
  const phoneRegex = /^(\+7|8)[0-9]{10}$/;

  if (!phoneRegex.test(cleanPhone)) {
    errors.value.phone = 'Введите корректный номер телефона (+7 XXX XXX-XX-XX)';
  } else {
    errors.value.phone = '';
  }
};

const validatePassword = () => {
  if (formData.value.password.length < 5) {
    errors.value.password = 'Пароль должен быть не менее 5 символов';
  } else {
    errors.value.password = '';
  }
  validatePasswordConfirmation();
};

const validatePasswordConfirmation = () => {
  if (formData.value.password !== formData.value.passwordConfirmation) {
    errors.value.passwordConfirmation = 'Пароли не совпадают';
  } else {
    errors.value.passwordConfirmation = '';
  }
};

const handleSubmit = async () => {
  showErrors.value = true;

  validateName();
  validateEmail();
  validatePhone();
  validatePassword();
  validatePasswordConfirmation();

  const hasErrors = Object.values(errors.value).some(error => error !== '');

  if (hasErrors) {
    return;
  }

  try {
    await store.PostNewUser(JSON.stringify(formData.value));
    await notification('Регистрация прошла успешно!', 'positive');
    router.push('/login');
  } catch (error) {
    if (error.response?.status === 409) {
      await notification('Пользователь с таким email уже существует', 'negative');
    } else {
      await notification('Произошла ошибка при регистрации', 'negative');
    }
    console.error('Ошибка регистрации', error);
  }
};
</script>

<style scoped>
.page-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  height: 100%;
  padding: 0px;
  margin-top: 20px;
}

.login-wrapper {
  display: flex;
  flex-direction: column;
  justify-content: center;
  max-width: 1800px;
  max-height: max-content;
  position: relative;
  z-index: 99;
}

form {
  display: flex;
  flex-direction: column;
  gap: 30px;
  width: 624px;
  border: 2px solid #f25c03;
  border-radius: 38px;
  padding: 40px 30px 30px 30px;
  backdrop-filter: blur(16.5px);
  background: rgba(255, 255, 255, 0.52);
}

input {
  padding: 15px 0;
  border: none;
  border-bottom: 1px solid #0000008C;
  transition: all 0.5s ease;
  margin-bottom: 20px;
  background: rgba(255, 255, 255, 0);
}

input:focus {
  outline: none;
}

.sumbit--btn{
  width: 100%;
  padding: 20px;
  font-size: 24px;
  border-radius: 30px;
  border: 2px solid #333333;
  background-color: rgba(255, 255, 255, 0);
  margin-top: 10px;
  cursor: pointer;
}

.text-orange{
  color: #F25C03;
}

.error-message {
  color: red;
  font-size: 20px;
  margin-top: -20px;
  font-weight: 700;
  display: block;
}

span{
  text-align: center;
}

@media (max-width: 768px) {
  .page-wrapper {
    margin: 0;
    padding: 0px 24px;
    justify-content: flex-start;
    align-items: flex-start;
    margin-bottom: 182px;
  }

  .login-wrapper {
    width: 100%;
    max-width: 100%;
    /* margin-top: 119px; */
  }

  form {
    width: calc(100% - 48px);
    padding: 30px 20px;
    border-radius: 24px;
    gap: 20px;
    transform: translateY(0);
    border-width: 1.5px;
    backdrop-filter: blur(18px);
    background: rgba(253, 253, 253, 0.18);
  }

  input {
    padding: 14px 0;
    margin-bottom: 16px;
    font-size: 16px;
  }

  .sumbit--btn {
    padding: 18px;
    font-size: 16px;
    margin-top: 20px;
  }

  .error-message {
    font-size: 16px;
    margin-top: -10px;
  }
}
</style>
