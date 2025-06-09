import { defineStore } from 'pinia'
import axios from 'axios'

export const baseUrl = 'http://127.0.0.1:5000/'

export const useDataStore = defineStore('data', {
  state: () => ({
    auth_key: '',
    excursions: [],
    excursionDetail: [],
  }),
  actions: {
    setToken(auth_key) {
      this.auth_key = auth_key
    },
    clearToken() {
      this.auth_key = ''
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
        this.setToken(response.data.access_token)
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
  },
  getters: {
    getExcursions: (state) => state.excursions,
    getExcursionDetail: (state) => state.excursionDetail,
  },
  persist: {
    key: 'data-store',
    storage: window.localStorage,
    paths: ['auth_key', 'excursions'],
  },
})
