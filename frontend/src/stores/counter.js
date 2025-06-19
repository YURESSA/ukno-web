import { defineStore } from 'pinia'
import axios from 'axios'

// export const baseUrl = 'http://127.0.0.1:5000/'

export const baseUrl = 'http://141.8.198.79/'

export const useDataStore = defineStore('data', {
  state: () => ({
    auth_key: '',
    role: '',
    excursions: [],
    residentExcursions: [],
    excursionDetail: [],
    profileData: [],
    reservationsData: [],
  }),
  actions: {
    setTokenRole(auth_key, role) {
      this.auth_key = auth_key
      this.role = role
    },
    clearTokenRole() {
      this.auth_key = ''
      this.role = ''
    },
    deletEvent() {
      this.residentExcursions = []
    },
    async PostNewUser(jsonData) {
      try {
        const response = await axios.post(`${baseUrl}/api/user/register`, jsonData, {
          headers: {
            'Content-Type': 'application/json',
          },
        })
        console.log('Успешная регистрация:', response.data)
      } catch (error) {
        console.error('Ошибка при регистрации:', error.response?.data || error.message)
        throw error
      }
    },
    async PostLoginUser(jsonData) {
      try {
        const response = await axios.post(`${baseUrl}/api/user/login`, jsonData, {
          headers: {
            'Content-Type': 'application/json',
          },
        })
        console.log('Успешный вход:', response.data)
        this.setTokenRole(response.data.access_token, response.data.role)
        console.log(this.auth_key)
      } catch (error) {
        console.error('Ошибка при входе:', error.response?.data || error.message)
        throw error
      }
    },
    async PostLoginResident(jsonData) {
      try {
        const response = await axios.post(`${baseUrl}/api/resident/login`, jsonData, {
          headers: {
            'Content-Type': 'application/json',
          },
        })
        console.log('Успешный вход:', response.data)
        this.setTokenRole(response.data.access_token, response.data.role)
        console.log(this.auth_key)
      } catch (error) {
        console.error('Ошибка при входе резидента:', error.response?.data || error.message)
        throw error
      }
    },
    async PutPassword(jsonData) {
      try {
        const response = await axios.put(`${baseUrl}/api/resident/profile`, jsonData, {
          headers: {
            Authorization: `Bearer ${this.auth_key}`,
            'Content-Type': 'application/json',
          },
        })
        console.log('Успешная смена пароля:', response.data)
      } catch (error) {
        console.error('Ошибка при смене пароля:', error.response?.data || error.message)
        throw error
      }
    },
    async PostLoginAdmin(jsonData) {
      try {
        const response = await axios.post(`${baseUrl}/api/admin/login`, jsonData, {
          headers: {
            'Content-Type': 'application/json',
          },
        })
        console.log('Успешный вход:', response.data)
        this.setTokenRole(response.data.access_token, response.data.role)
        console.log(this.auth_key)
      } catch (error) {
        console.error('Ошибка при входе:', error.response?.data || error.message)
        throw error
      }
    },
    async FetchExcursions() {
      try {
        const response = await axios.get(`${baseUrl}/api/user/excursions`)
        console.log('Данные успешно получены:', response.data)
        this.excursions = response.data
      } catch (error) {
        console.error('Ошибка при получении данных:', error.response?.data || error.message)
        throw error
      }
    },
    async GetFilterExcursions(props) {
      try {
        const response = await axios.get(`${baseUrl}/api/user/excursions?${props}`)
        console.log(response)
        console.log('Данные успешно получены:', response.data)
        this.excursions = response.data
      } catch (error) {
        console.error('Ошибка при получении данных:', error.response?.data || error.message)
        throw error
      }
    },
    async FetchExcursionDetail(excursion_id) {
      try {
        const response = await axios.get(`${baseUrl}/api/user/excursions_detail/${excursion_id}`)
        console.log('Данные успешно получены:', response.data)
        this.excursionDetail = response.data
      } catch (error) {
        console.error('Ошибка при получении данных:', error.response?.data || error.message)
        throw error
      }
    },
    async PostReservation(jsonData) {
      try {
        const response = await axios.post(`${baseUrl}/api/user/reservations`, jsonData, {
          headers: {
            Authorization: `Bearer ${this.auth_key}`,
            'Content-Type': 'application/json',
          },
        })
        console.log('Успешно забронировано:', response.data)
      } catch (error) {
        console.log(this.auth_key)
        console.error('Ошибка при бронировании:', error.response?.data || error.message)
        throw error
      }
    },
    async GetProfile() {
      try {
        const response = await axios.get(`${baseUrl}/api/user/profile`, {
          headers: {
            Authorization: `Bearer ${this.auth_key}`,
          },
        })
        console.log('Данные профиля успешно получены:', response.data)
        this.profileData = response.data
      } catch (error) {
        console.error('Ошибка при получении данных профиля:', error.response?.data || error.message)
        throw error
      }
    },
    async GetResidentProfile() {
      try {
        const response = await axios.get(`${baseUrl}/api/resident/profile`, {
          headers: {
            Authorization: `Bearer ${this.auth_key}`,
          },
        })
        console.log('Данные профиля успешно получены:', response.data)
        this.profileData = response.data
      } catch (error) {
        console.error('Ошибка при получении данных профиля:', error.response?.data || error.message)
        throw error
      }
    },
    async GetUserReservations() {
      try {
        const response = await axios.get(`${baseUrl}/api/user/reservations`, {
          headers: {
            Authorization: `Bearer ${this.auth_key}`,
          },
        })
        console.log('Данные бронирования успешно получены:', response.data)
        this.reservationsData = response.data
      } catch (error) {
        console.error(
          'Ошибка при получении данных бронирования:',
          error.response?.data || error.message,
        )
        throw error
      }
    },
    async DeletReservation(jsonData) {
      try {
        const response = await axios.delete(`${baseUrl}/api/user/reservations`, jsonData, {
          headers: {
            Authorization: `Bearer ${this.auth_key}`,
            'Content-Type': 'application/json',
          },
        })
        console.log('Данные бронирования успешно удалены:', response.data)
        // this.reservationsData = response.data
      } catch (error) {
        console.error(
          'Ошибка при удалении данных бронирования:',
          error.response?.data || error.message,
        )
        throw error
      }
    },
    async PostNewEvent(formData) {
      try {
        const response = await axios.post(`${baseUrl}/api/resident/excursions`, formData, {
          headers: {
            Authorization: `Bearer ${this.auth_key}`,
            'Content-Type': 'multipart/form-data', // Важно для FormData!
          },
        })
        console.log('Upload success:', response.data)
      } catch (error) {
        console.error('Ошибка при создании:', error.response?.data || error.message)
        throw error
      }
    },
    async FetchResidentEvents() {
      try {
        const response = await axios.get(`${baseUrl}/api/resident/excursions`, {
          headers: {
            Authorization: `Bearer ${this.auth_key}`,
          },
        })
        console.log('Данные успешно получены:', response.data)
        this.residentExcursions = response.data
        console.log(response.data)
      } catch (error) {
        console.error('Ошибка при получении данных:', error.response?.data || error.message)
        throw error
      }
    },
    async DeletSession(eventId, sessionId) {
      try {
        const response = await axios.delete(
          `${baseUrl}/api/resident/excursions/${eventId}/sessions/${sessionId}`,
          {
            headers: {
              Authorization: `Bearer ${this.auth_key}`,
            },
          },
        )
        console.log('Сессия успешно удалена:', response.data)
      } catch (error) {
        console.error('Ошибка при удалении:', error.response?.data || error.message)
        throw error
      }
    },
  },
  getters: {
    getExcursions: (state) => state.excursions,
    getExcursionDetail: (state) => state.excursionDetail,
    getResidentEvents: (state) => state.residentExcursions,
  },
  persist: {
    key: 'data-store',
    storage: window.localStorage,
    paths: ['auth_key', 'excursions'],
  },
})
