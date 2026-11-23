  <template>
    <div v-if="selectedSession" class="page-wrapper">
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
                @input="onPhoneInput" inputmode="tel" maxlength="32" @blur="validatePhoneField"
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

              <!-- Выбор сессии на странице оплаты -->
              <div class="sessions-section" v-if="excursion?.sessions?.length > 0">
                <span>Выбранная дата и время</span>
                <div class="sessions-list">
                  <button
                    v-for="session in excursion.sessions"
                    :key="session.session_id"
                    type="button"
                    class="session-card"
                    :class="{ 'session-card--active': formData.session_id === session.session_id, 'session-card--full': session.available <= 0 }"
                    :disabled="session.available <= 0"
                    @click="formData.session_id = session.session_id"
                  >
                    <span class="session-date">{{ formatSessionDate(session) }}</span>
                    <span class="session-time">{{ formatSessionTime(session) }}</span>
                    <span class="session-seats" :class="{ 'session-seats--low': session.available <= 3 && session.available > 0 }">
                      <template v-if="session.available > 0">{{ session.available }} мест{{ session.available === 1 ? 'о' : session.available < 5 ? 'а' : '' }}</template>
                      <template v-else>Мест нет</template>
                    </span>
                  </button>
                </div>
              </div>

              <div class="participants-input">
                <label for="participants-count">Количество участников</label>
                <div class="participants">
                  <IconButton class="participants--btn left--btn" type="button" @click="changeParticipants(-1)" text="-"/>
                  <input
                    id="participants-count"
                    type="text"
                    inputmode="numeric"
                    autocomplete="off"
                    :value="formData.participants_count"
                    :aria-invalid="showErrors && Boolean(participantsError)"
                    :aria-describedby="showErrors && participantsError ? 'participants-error' : undefined"
                    @input="onParticipantsInput"
                  >
                  <IconButton class="participants--btn right--btn" type="button" @click="changeParticipants(1)" text="+"/>
                </div>
                <p v-if="showErrors && participantsError" id="participants-error" class="booking-error" role="alert">
                  {{ participantsError }}
                </p>
              </div>
              <div v-if="selectedSession && !participantsError">
                <h5>Итого к оплате: {{ participantsCount * selectedSession.cost }} ₽</h5>
              </div>
              <BaseButton type="submit" class="sumbit--btn" text="Забронировать"/>
              <p v-if="bookingError" class="booking-error" role="alert">{{ bookingError }}</p>
              <span class="offer">Нажимая «Забронировать», вы соглашаетесь с условиями приобретения и офертой</span>
            </form>
          </div>
        </div>
      </div>
    </div>
    <NotFoundPage
      v-else-if="isBookingNotFound"
      description="Ссылка на бронирование недействительна"
      action-label="К списку событий"
      to="/events"
    />
    <div v-else-if="error" class="event-details-error">
      <p role="alert">{{ error }}</p>
      <BaseButton text="Повторить" @click="retry" />
    </div>
    <LoadingAnimation v-else />
  </template>

  <script setup>
import { sanitizePhoneInput } from '@/utils/adminValidation'
  import Header from './components/header.vue';
  import NotFoundPage from '@/components/shared/NotFoundPage.vue';
  import LoadingAnimation from '@/components/shared/loading-animation.vue';
  import { parseEventRouteId, useEventDetails } from '@/composables/useEventDetails';
  import BaseButton from '@/components/ui/button/BaseButton.vue';
  import IconButton from '@/components/ui/button/IconButton.vue';
  import { useDataStore } from '@/stores/counter';
  import { computed, ref, watch } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import { notification } from '@/utils/notification'
  import { getApiErrorMessage } from '@/utils/apiError'

  const onPhoneInput = event => {
    const value = sanitizePhoneInput(event.target.value)
    event.target.value = value
    formData.value.phone_number = value
    clearError('phone_number')
  }
  const validatePhoneField = () => {
    const phone = (formData.value.phone_number || '').replace(/[ ()-]/g, '')
    errors.value.phone_number = /^(\+7|8)[0-9]{10}$/.test(phone) ? '' : 'Введите корректный номер телефона'
  }

  const store = useDataStore();
  const route = useRoute();
  const router = useRouter();

  const routeSessionId = computed(() => parseEventRouteId(route.params.id));
  const { event: excursion, notFound, error, retry } = useEventDetails(
    () => route.query.excursion_id,
    () => routeSessionId.value !== null,
  );
  const userData = computed(() => store.getProfileData);

  const showErrors = ref(false);

  const formData = ref({
    session_id: routeSessionId.value,
    full_name: userData.value.full_name,
    phone_number: userData.value.phone,
    email: userData.value.email,
    participants_count: '1',
  });

  const errors = ref({
    full_name: '',
    phone_number: '',
    email: '',
  });

  const bookingError = ref('')
  const selectedSession = computed(() =>
    excursion.value?.sessions?.find(s => s.session_id === formData.value.session_id),
  );
  const isBookingNotFound = computed(() =>
    routeSessionId.value === null || notFound.value || Boolean(excursion.value && !selectedSession.value),
  );
  const participantsCount = computed(() => Number(formData.value.participants_count))
  const participantsError = computed(() => {
    const count = participantsCount.value
    if (!Number.isSafeInteger(count) || count < 1) {
      return 'Укажите целое количество участников от 1'
    }
    const available = selectedSession.value?.available
    return Number.isFinite(available) && count > available ? `Свободных мест: ${available}` : ''
  })

  watch([routeSessionId, () => route.query.excursion_id], ([id]) => {
    formData.value.session_id = id;
    showErrors.value = false;
    bookingError.value = '';
  });

  function onParticipantsInput(event) {
    const input = event.target
    if (/^[0-9]*$/.test(input.value)) {
      formData.value.participants_count = input.value
    } else {
      input.value = formData.value.participants_count
    }
  }

  function changeParticipants(delta) {
    const count = participantsCount.value
    const current = Number.isSafeInteger(count) ? count : 0
    const next = Math.max(1, current + delta)
    if (Number.isSafeInteger(next)) formData.value.participants_count = String(next)
  }

  function formatSessionDate(session) {
    const d = new Date(session.start_datetime);
    return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' });
  }

  function formatSessionTime(session) {
    const d = new Date(session.start_datetime);
    return d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
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
    const cleanPhone = (formData.value.phone_number || '').replace(/[^\d+]/g, '');

    if (!phoneRegex.test(cleanPhone)) {
      errors.value.phone_number = 'Введите корректный номер телефона';
    } else {
      errors.value.phone_number = '';
    }
    formData.value.phone_number = cleanPhone;
  };

  const handleSubmit = async () => {
    if (!selectedSession.value) return;
    showErrors.value = true;
    bookingError.value = '';

    validateName();
    validateEmail();
    validatePhone();

    const hasErrors = Object.values(errors.value).some(error => error !== '');

    if (hasErrors || participantsError.value) {
      return;
    }
    try {
      await store.PostReservation(JSON.stringify({
        ...formData.value,
        participants_count: participantsCount.value,
      }));
      await notification('Бронирование прошло успешно!', 'positive');
      router.push('/profile');
    } catch (error) {
      bookingError.value = getApiErrorMessage(error, 'Не удалось забронировать. Попробуйте ещё раз.');
    }
  };
  </script>

  <style scoped>
  .event-details-error {
    display: grid;
    min-height: 100vh;
    padding: 100px 16px 32px;
    gap: 16px;
    align-content: center;
    justify-items: center;
    text-align: center;
  }

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
    background: white;
    color: #9E9E9E;
    touch-action: manipulation;
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

  .booking-error {
    color: #b42318;
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

  @media (max-width: 768px) {
    h5{
      font-size: 16px;
    }
    .participants--btn:hover {
      background-color: white;
    }
    .participants--btn:active {
      background-color: #F25C03;
    }
  }

  .sessions-section {
    margin-bottom: 30px;
    width: 100%;
  }

  .sessions-section > span {
    display: block;
    color: #9E9E9E;
    margin-bottom: 15px;
    font-size: 16px;
  }

  .sessions-list {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
  }

  .session-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 10px 15px;
    border: 2px solid #FFD6BD;
    border-radius: 12px;
    background-color: #fff;
    cursor: pointer;
    transition: all 0.2s ease;
    min-width: 120px;
  }

  .session-card:hover:not(:disabled) {
    border-color: #F25C03;
    box-shadow: 0 4px 12px rgba(242, 92, 3, 0.15);
  }

  .session-card--active {
    border-color: #F25C03;
    background-color: #FFF5EF;
    box-shadow: 0 4px 12px rgba(242, 92, 3, 0.2);
  }

  .session-card:disabled, .session-card--full {
    opacity: 0.6;
    cursor: not-allowed;
    border-color: #eee;
    background-color: #fafafa;
  }

  .session-date {
    font-size: 14px;
    font-weight: 700;
    color: #333;
  }

  .session-time {
    font-size: 13px;
    color: #666;
    margin-bottom: 5px;
  }

  .session-seats {
    font-size: 12px;
    color: #4CAF50;
    font-weight: 600;
  }

  .session-seats--low {
    color: #FF9800;
  }

  .session-card--full .session-seats {
    color: #F44336;
  }
  </style>
