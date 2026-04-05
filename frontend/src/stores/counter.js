import { defineStore } from 'pinia'
import axios from 'axios'
import router from '@/router'

export const baseUrl = import.meta.env.VITE_FRONTEND_URL;

export const useDataStore = defineStore('data', {
  state: () => ({
    auth_key: '',
    role: '',
    excursions: [],
    residentExcursions: [],
    excursionDetail: [],
    profileData: [],
    reservationsData: [],
    newsData: [],
    partnersData: [],
    excursionsStats: [],
    users: [],
    categories: [],
    format: [],
    age: [],
    adminExcursions: [],
    adminReservations: [],
    teamData: [],
    project: [],
    culturalSpace: [],
    history: []
  }),
  actions: {
    setTokenRole(auth_key, role) {
      this.auth_key = auth_key
      this.role = role
    },
    clearTokenRole() {
      this.auth_key = ''
      this.role = ''
      this.profileData = []
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
      } catch (error) {
        console.error('Ошибка при регистрации:', error.response?.data || error.message)
        throw error
      }
    },
    async PostLoginUser(jsonData) {
      try {
        const response = await axios.post(`${baseUrl}/api/login`, jsonData, {
          headers: {
            'Content-Type': 'application/json',
          },
        })
        this.setTokenRole(response.data.access_token, response.data.role)
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
        this.setTokenRole(response.data.access_token, response.data.role)
      } catch (error) {
        console.error('Ошибка при входе резидента:', error.response?.data || error.message)
        throw error
      }
    },
    async PutPassword(jsonData, url) {
      try {
        const response = await axios.put(`${baseUrl}${url}`, jsonData, {
          headers: {
            Authorization: `Bearer ${this.auth_key}`,
            'Content-Type': 'application/json',
          },
        })
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
        this.setTokenRole(response.data.access_token, response.data.role)
      } catch (error) {
        console.error('Ошибка при входе:', error.response?.data || error.message)
        throw error
      }
    },
    async FetchExcursions() {
      try {
        const response = await axios.get(`${baseUrl}/api/user/excursions`)
        this.excursions = response.data
      } catch (error) {
        console.error('Ошибка при получении данных:', error.response?.data || error.message)
        throw error
      }
    },
    async GetFilterExcursions(props) {
      try {
        const response = await axios.get(`${baseUrl}/api/user/excursions?${props}`)
        this.excursions = response.data
      } catch (error) {
        console.error('Ошибка при получении данных:', error.response?.data || error.message)
        throw error
      }
    },
    async FetchExcursionDetail(excursion_id) {
      try {
        const response = await axios.get(`${baseUrl}/api/user/excursions_detail/${excursion_id}`)
        this.excursionDetail = response.data
      } catch (error) {
        console.error('Ошибка при получении данных:', error.response?.data || error.message)
        throw error
      }
    },
    async FetchExcursionDetailResident(excursion_id) {
      try {
        const response = await axios.get(`${baseUrl}/api/resident/excursions/${excursion_id}`,
          {
            headers: {
              'Authorization': `Bearer ${this.auth_key}`
            }
          }
        );
        this.excursionDetail = response.data
      } catch (error) {
        console.error('Ошибка при получении данных:', error.response?.data || error.message)
        throw error
      }
    },
    async PostReservation(jsonData) {
      try {
        const response = await axios.post(`${baseUrl}/api/user/v2/reservations`, jsonData, {
          headers: {
            Authorization: `Bearer ${this.auth_key}`,
            'Content-Type': 'application/json',
          },
        })
        if (response.data.payment_url) {
          window.location.href = response.data.payment_url;
        }
      } catch (error) {
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
        this.reservationsData = response.data
      } catch (error) {
        console.error(
          'Ошибка при получении данных бронирования:',
          error.response?.data || error.message,
        )
        throw error
      }
    },
    async DeleteReservation(delet_id) {
      try {
        const jsonData = JSON.stringify(delet_id)
        const response = await axios.delete(`${baseUrl}/api/user/v2/reservations`, {
          data: jsonData,
          headers: {
            Authorization: `Bearer ${this.auth_key}`,
            'Content-Type': 'application/json',
          },
        })
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
            'Content-Type': 'multipart/form-data',
          },
        })
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
        this.residentExcursions = response.data
      } catch (error) {
        console.error('Ошибка при получении данных:', error.response?.data || error.message)
        throw error
      }
    },
    async DeletEvent(eventId, sessionId) {
      try {
        const response = await axios.delete(
          `${baseUrl}/api/resident/excursions/${eventId}`,
          {
            headers: {
              Authorization: `Bearer ${this.auth_key}`,
            },
          },
        )
      } catch (error) {
        console.error('Ошибка при удалении:', error.response?.data || error.message)
        throw error
      }
    },
    async DeleteSession(eventId, sessionId) {
      try {
        const response = await axios.delete(
          `${baseUrl}/api/resident/excursions/${eventId}/sessions/${sessionId}`,
          {
            headers: {
              Authorization: `Bearer ${this.auth_key}`,
            },
          },
        )
      } catch (error) {
        console.error('Ошибка при удалении:', error.response?.data || error.message)
        throw error
      }
    },
    async DeletePhoto(eventId, photoId) {
      try {
        const response = await axios.delete(
          `${baseUrl}/api/resident/excursions/${eventId}/photos/${photoId}`,
          {
            headers: {
              Authorization: `Bearer ${this.auth_key}`,
            },
          },
        )
      } catch (error) {
        console.error('Ошибка при удалении фото:', error.response?.data || error.message)
        throw error
      }
    },
    async PatchSessionData(excursion_id, jsonData) {
      try {
        const response = await axios.patch(`${baseUrl}/api/resident/excursions/${excursion_id}`, jsonData, {
          headers: {
            Authorization: `Bearer ${this.auth_key}`,
            'Content-Type': 'application/json'
          },
        })
      } catch (error) {
        console.error('Ошибка при обновлении данных:', error.response?.data || error.message)
        throw error
      }
    },
    async PostNewPhoto(excursion_id, formData) {
      try {
        const response = await axios.post(`${baseUrl}/api/resident/excursions/${excursion_id}/photos`, formData, {
          headers: {
            Authorization: `Bearer ${this.auth_key}`,
          },
        })
      } catch (error) {
        console.error('Ошибка при добавлении фото:', error.response?.data || error.message)
        throw error
      }
    },
    async PostNewSession(excursion_id, jsonData) {
      try {
        const response = await axios.post(`${baseUrl}/api/resident/excursions/${excursion_id}/sessions`, jsonData, {
          headers: {
            Authorization: `Bearer ${this.auth_key}`,
            'Content-Type': 'application/json'
          },
        })
      } catch (error) {
        console.error('Ошибка при создании:', error.response?.data || error.message)
        throw error
      }
    },
    async FetchNews() {
      try {
        const response = await axios.get(`${baseUrl}/api/user/news`)
        this.newsData = response.data
      } catch (error) {
        console.error('Ошибка при получении новостей:', error.response?.data || error.message)
        throw error
      }
    },
    async FetchPartners() {
      try {
        const response = await axios.get(`${baseUrl}/api/references/partners`)
        this.partnersData = response.data
      } catch (error) {
        console.error('Ошибка при получении партнёров:', error.response?.data || error.message)
        throw error
      }
    },
    async FetchExcursionsStats(){
      try {
        const response = await axios.get(`${baseUrl}/api/references/excursion-stats`)
        this.excursionsStats = response.data
      } catch (error) {
        console.error('Ошибка при получении данных:', error.response?.data || error.message)
        throw error
      }
    },
    // Админка
    async FetchUsers(){
      try {
        const response = await axios.get(`${baseUrl}/api/admin/users`, {
          headers: {
            Authorization: `Bearer ${this.auth_key}`,
          },
        })
        console.log('Данные успешно получены:', response.data)
        this.users = response.data
      } catch (error) {
        console.error('Ошибка при получении данных:', error.response?.data || error.message)
        throw error
      }
    },
    async PostAdminNewUser(jsonData) {
      try {
        const response = await axios.post(`${baseUrl}/api/admin/users`, jsonData, {
          headers: {
            Authorization: `Bearer ${this.auth_key}`,
            'Content-Type': 'application/json'
          },
        })
        console.log('Пользователь успешно добавлен:', response.data)
      } catch (error) {
        console.error('Ошибка при создании:', error.response?.data || error.message)
        throw error
      }
    },
    async PutAdminUser(jsonData, email) {
      try {
        const response = await axios.put(`${baseUrl}/api/admin/users/detail/${email}`, jsonData, {
          headers: {
            Authorization: `Bearer ${this.auth_key}`,
            'Content-Type': 'application/json',
          },
        })
        console.log('Успешная смена данных пользователя:', response.data)
      } catch (error) {
        console.error('Ошибка при смене данных пользователя:', error.response?.data || error.message)
        throw error
      }
    },
    async DeleteAdminUser(email) {
      try {
        const response = await axios.delete(
          `${baseUrl}/api/admin/users/detail/${email}`,
          {
            headers: {
              Authorization: `Bearer ${this.auth_key}`,
            },
          },
        )
        console.log('Пользователь успешно удален:', response.data)
      } catch (error) {
        console.error('Ошибка при удалении :', error.response?.data || error.message)
        throw error
      }
    },
    async FetchCategories(){
      try {
        const response = await axios.get(`${baseUrl}/api/references/categories`, {
          headers: {
            Authorization: `Bearer ${this.auth_key}`,
          },
        })
        console.log('Данные успешно получены:', response.data)
        this.categories = response.data
      } catch (error) {
        console.error('Ошибка при получении данных:', error.response?.data || error.message)
        throw error
      }
    },
    async deleteCatigories(id) {
      try {
        const response = await axios.delete(
          `${baseUrl}/api/references/categories/${id}`,
          {
            headers: {
              Authorization: `Bearer ${this.auth_key}`,
            },
          },
        )
        console.log('Категория успешно удален:', response.data)
      } catch (error) {
        console.error('Ошибка при удалении категории:', error.response?.data || error.message)
        throw error
      }
    },
    async PostAdminNewCategories(jsonData) {
      try {
        const response = await axios.post(`${baseUrl}/api/references/categories`, jsonData, {
          headers: {
            Authorization: `Bearer ${this.auth_key}`,
            'Content-Type': 'application/json'
          },
        })
        console.log('Категория успешно добавлена:', response.data)
      } catch (error) {
        console.error('Ошибка при создании:', error.response?.data || error.message)
        throw error
      }
    },
    async FetchFormat(){
      try {
        const response = await axios.get(`${baseUrl}/api/references/format-types`, {
          headers: {
            Authorization: `Bearer ${this.auth_key}`,
          },
        })
        console.log('Данные успешно получены:', response.data)
        this.format = response.data
      } catch (error) {
        console.error('Ошибка при получении данных:', error.response?.data || error.message)
        throw error
      }
    },
    async PostAdminNewFormat(jsonData) {
      try {
        const response = await axios.post(`${baseUrl}/api/references/format-types`, jsonData, {
          headers: {
            Authorization: `Bearer ${this.auth_key}`,
            'Content-Type': 'application/json'
          },
        })
        console.log('Формат успешно добавлен:', response.data)
      } catch (error) {
        console.error('Ошибка при создании:', error.response?.data || error.message)
        throw error
      }
    },
    async deleteFormat(id) {
      try {
        const response = await axios.delete(
          `${baseUrl}/api/references/format-types/${id}`,
          {
            headers: {
              Authorization: `Bearer ${this.auth_key}`,
            },
          },
        )
        console.log('Формат успешно удален:', response.data)
      } catch (error) {
        console.error('Ошибка при удалении формата:', error.response?.data || error.message)
        throw error
      }
    },
    async FetchAge(){
      try {
        const response = await axios.get(`${baseUrl}/api/references/age-categories`, {
          headers: {
            Authorization: `Bearer ${this.auth_key}`,
          },
        })
        console.log('Данные успешно получены:', response.data)
        this.age = response.data
      } catch (error) {
        console.error('Ошибка при получении данных:', error.response?.data || error.message)
        throw error
      }
    },
    async PostAdminNewAge(jsonData) {
      try {
        const response = await axios.post(`${baseUrl}/api/references/age-categories`, jsonData, {
          headers: {
            Authorization: `Bearer ${this.auth_key}`,
            'Content-Type': 'application/json'
          },
        })
        console.log('Возраст успешно добавлен:', response.data)
      } catch (error) {
        console.error('Ошибка при создании:', error.response?.data || error.message)
        throw error
      }
    },
    async deleteAge(id) {
      try {
        const response = await axios.delete(
          `${baseUrl}/api/references/age-categories/${id}`,
          {
            headers: {
              Authorization: `Bearer ${this.auth_key}`,
            },
          },
        )
        console.log('Возраст успешно удален:', response.data)
      } catch (error) {
        console.error('Ошибка при удалении возраста:', error.response?.data || error.message)
        throw error
      }
    },
    async FetchAdminExcursion(){
      try {
        const response = await axios.get(`${baseUrl}/api/admin/excursions`, {
          headers: {
            Authorization: `Bearer ${this.auth_key}`,
          },
        })
        console.log('Данные успешно получены:', response.data)
        this.adminExcursions = response.data
      } catch (error) {
        console.error('Ошибка при получении данных:', error.response?.data || error.message)
        throw error
      }
    },
    async PostAdminNewExcursion(jsonData) {
      try {
        const response = await axios.post(`${baseUrl}/api/admin/excursions`, jsonData, {
          headers: {
            Authorization: `Bearer ${this.auth_key}`,
            'Content-Type': 'application/json'
          },
        })
        console.log('Экскурсия успешно добавлена:', response.data)
      } catch (error) {
        console.error('Ошибка при создании события:', error.response?.data || error.message)
        throw error
      }
    },
    async deleteAdminExcursion(id) {
      try {
        const response = await axios.delete(
          `${baseUrl}/api/admin/excursions/${id}`,
          {
            headers: {
              Authorization: `Bearer ${this.auth_key}`,
            },
          },
        )
        console.log('Событие успешно удалено:', response.data)
      } catch (error) {
        console.error('Ошибка при удалении события:', error.response?.data || error.message)
        throw error
      }
    },
    async PostNewExcursion(formData) {
      try {
        const dto = JSON.parse(formData.get('data'))
        console.log('DTO to backend:', dto, typeof dto.category_id, dto.category_id)
        const response = await axios.post(`${baseUrl}/api/admin/excursions`, formData, {
          headers: {
            Authorization: `Bearer ${this.auth_key}`,
            'Content-Type': 'multipart/form-data',
          },
        })
        console.log('Upload success:', response.data)
      } catch (error) {
        console.error('Ошибка при создании:', error.response?.data || error.message)
        console.error('status', error.response?.status)
        console.error('data', error.response?.data)
        throw error
      }
    },

    async PatchExcursion(excursionId, payload) {
      return axios.patch(`${baseUrl}/api/admin/excursions/${excursionId}`, payload, {
        headers: {
          Authorization: `Bearer ${this.auth_key}`,
          'Content-Type': 'application/json'
        }
      })
    },

    async PostExcursionPhoto(excursionId, file) {
      const fd = new FormData()
      fd.append('photo', file)
      return axios.post(`${baseUrl}/api/admin/excursions/${excursionId}/photos`, fd, {
        headers: { Authorization: `Bearer ${this.auth_key}` }
      })
    },

    async DeleteExcursionPhoto(excursionId, photoId) {
      return axios.delete(`${baseUrl}/api/admin/excursions/${excursionId}/photos/${photoId}`, {
        headers: { Authorization: `Bearer ${this.auth_key}` }
      })
    },

    async PostExcursionSession(excursionId, payload) {
      return axios.post(`${baseUrl}/api/admin/excursions/${excursionId}/sessions`, payload, {
        headers: { Authorization: `Bearer ${this.auth_key}` }
      })
    },

    async PatchExcursionSession(excursionId, sessionId, payload) {
      return axios.patch(`${baseUrl}/api/admin/excursions/${excursionId}/sessions/${sessionId}`, payload, {
        headers: { Authorization: `Bearer ${this.auth_key}` }
      })
    },

    async DeleteExcursionSession(excursionId, sessionId) {
      return axios.delete(`${baseUrl}/api/admin/excursions/${excursionId}/sessions/${sessionId}`, {
        headers: { Authorization: `Bearer ${this.auth_key}` }
      })
    },
    async FetchAdminNews() {
      try {
        const response = await axios.get(`${baseUrl}/api/admin/news`, {
          headers: {
            Authorization: `Bearer ${this.auth_key}`,
          },
        })
        console.log('Данные успешно получены:', response.data)
        this.newsData = response.data
      } catch (error) {
        console.error('Ошибка при получении данных:', error.response?.data || error.message)
        throw error
      }
    },
    async PostAdminNews(formData) {
      return axios.post(`${baseUrl}api/admin/news`, formData, {
        headers: { Authorization: `Bearer ${this.auth_key}` }
      })
    },
    async PutAdminNews(newsId, formData) {
      try {
        const response = await axios.put(`${baseUrl}api/admin/news/${newsId}`, formData, {
          headers: { Authorization: `Bearer ${this.auth_key}` }
        })
        console.log('Успешная смена данных новости:', response.data)
      } catch (error) {
        console.error('Ошибка при смене данных новости:', error.response?.data || error.message)
        throw error
      }
    },
    async DeleteAdminNews(newsId) {
      const apiBase = baseUrl.replace(/\/$/, '');
      return axios.delete(`${apiBase}/api/admin/news/${newsId}`, {
        headers: { Authorization: `Bearer ${this.auth_key}` }
      });
    },

    async DeleteAdminNewsPhoto(newsId, photoId) {
      const apiBase = baseUrl.replace(/\/$/, '');
      return axios.delete(`${apiBase}/api/admin/news/${newsId}/photos/${photoId}`, {
        headers: { Authorization: `Bearer ${this.auth_key}` }
      });
    },

    async PostAdminNewsPhoto(newsId, file) {
      const formData = new FormData();
      formData.append('photo', file); // Ключ из Swagger: photo

      return axios.post(`${baseUrl}/api/admin/news/${newsId}/photos`, formData, {
        headers: { Authorization: `Bearer ${this.auth_key}` }
      });
    },

    async FetchAdminReservations() {
      try {
        const response = await axios.get(`${baseUrl}/api/admin/reservations`, {
          headers: {
            Authorization: `Bearer ${this.auth_key}`,
          },
        })
        console.log('Данные успешно получены:', response.data)
        this.adminReservations = response.data
      } catch (error) {
        console.error('Ошибка при получении данных:', error.response?.data || error.message)
        throw error
      }
    },


    async FetchAdminReservationDetails(id) {
      try {
        const response = await axios.get(`${baseUrl}/api/admin/reservations/${id}`, {
          headers: {
            Authorization: `Bearer ${this.auth_key}`,
          },
        })
        console.log('Данные успешно получены:', response.data)
        return response.data
      } catch (error) {
        console.error('Ошибка при получении данных:', error.response?.data || error.message)
        throw error
      }
    },

    async DeleteAdminReservation(reservationId) {
      const apiBase = baseUrl.replace(/\/$/, '')
      return axios.delete(`${apiBase}/api/admin/reservations/${reservationId}`, {
        headers: { Authorization: `Bearer ${this.auth_key}` }
      })
    },
    async FetchTeam() {
      try {
        const response = await axios.get(`${baseUrl}/api/references/team`, {
          headers: {
            Authorization: `Bearer ${this.auth_key}`,
          },
        })
        console.log('Данные успешно получены:', response.data)
        this.teamData = response.data
      } catch (error) {
        console.error('Ошибка при получении данных:', error.response?.data || error.message)
        throw error
      }
    },
    async AddTeamMember(formData) {
      try {
        const response = await axios.post(`${baseUrl}/api/references/team`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data', // Важно для фото
            'Authorization': `Bearer ${this.auth_key}`,
          },
        });
        await this.FetchTeam(); // Обновляем список после добавления
        return response.data;
      } catch (error) {
        console.error('Ошибка при добавлении:', error.response?.data || error.message);
        throw error;
      }
    },
    async UpdateTeamMember(id, formData) {
      try {
        const response = await axios.put(`${baseUrl}/api/references/team/${id}`, formData, {
          headers: { Authorization: `Bearer ${this.auth_key}` }
        });
        console.log('Успешная смена данных:', response.data)
        await this.FetchTeam();
      } catch (error) {
        console.error('Ошибка при смене данных:', error.response?.data || error.message)
        throw error
      }
    },
    async DeleteTeamMember(id) {
      try {
        await axios.delete(`${baseUrl}/api/references/team/${id}`, {
          headers: {
            'Authorization': `Bearer ${this.auth_key}`,
          },
        });
        await this.FetchTeam(); // Обновляем список после удаления
      } catch (error) {
        console.error('Ошибка при удалении:', error.response?.data || error.message);
        throw error;
      }
    },
    async FetchProject() {
      try {
        const response = await axios.get(`${baseUrl}/api/references/projects`, {
          headers: {
            Authorization: `Bearer ${this.auth_key}`,
          },
        })
        this.project = response.data
      } catch (error) {
        console.error('Ошибка при получении данных:', error.response?.data || error.message)
        throw error
      }
    },
    async FetchCulturalSpace() {
      try {
        const response = await axios.get(`${baseUrl}/api/references/cultural-space`)
        this.culturalSpace = response.data
      } catch (error) {
        console.error('Ошибка при получении данных:', error.response?.data || error.message)
        throw error
      }
    },
    async AddCulturalSpace(formData) {
      try {
        const response = await axios.post(`${baseUrl}/api/references/cultural-space`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data', // Важно для фото
            'Authorization': `Bearer ${this.auth_key}`,
          },
        });
        await this.FetchCulturalSpace(); // Обновляем список после добавления
        return response.data;
      } catch (error) {
        console.error('Ошибка при добавлении:', error.response?.data || error.message);
        throw error;
      }
    },
    async UpdateCulturalSpaceText(id, payload) {
      try {
        const response = await axios.put(`${baseUrl}/api/references/cultural-space/${id}`, payload, {
          headers: { Authorization: `Bearer ${this.auth_key}` }
        });
        console.log('Успешная смена данных:', response.data)
        await this.FetchCulturalSpace();
      } catch (error) {
        console.error('Ошибка при смене данных:', error.response?.data || error.message)
        throw error
      }
    },

    async UpdateCulturalSpacePhoto(id, formData) {
      // Фото обновляется через отдельный POST эндпоинт
      return await axios.post(`${baseUrl}/api/references/cultural-space/${id}/photo`, formData)
    },

    async DeleteCulturalSpace(id) {
      return await axios.delete(`${baseUrl}/api/references/cultural-space/${id}`)
    },
    async FetchHistory() {
      try {
        const response = await axios.get(`${baseUrl}/api/references/history`)
        this.history = response.data
      } catch (error) {
        console.error('Ошибка при получении данных:', error.response?.data || error.message)
        throw error
      }
    },
    async PostTeam({ full_name, description, photoFile }) {
      const apiBase = baseUrl.replace(/\/$/, '')
      const fd = new FormData()
      fd.append('full_name', full_name)
      if (description != null) fd.append('description', description)
      if (photoFile) fd.append('photo', photoFile)

      return axios.post(`${apiBase}/api/references/team`, fd, {
        headers: { Authorization: `Bearer ${this.auth_key}` }
      })
    },

    async DeleteTeam(id) {
      const apiBase = baseUrl.replace(/\/$/, '')
      return axios.delete(`${apiBase}/api/references/team/${id}`, {
        headers: { Authorization: `Bearer ${this.auth_key}` }
      })
    },
  },
  getters: {
    getProfileData: (state) => state.profileData,
    getExcursions: (state) => state.excursions,
    getExcursionDetail: (state) => state.excursionDetail,
    getResidentEvents: (state) => state.residentExcursions,
    getNews: (state) => state.newsData,
    getPartners: (state) => state.partnersData,
    getExcursionsStats: (state) => state.excursionsStats,
    getUsers: (state) => (state).users,
    getCategories: (state) => (state).categories,
    getFormat: (state) => (state).format,
    getAge: (state) => state.age,
    getAdminExcursion: (state) => state.adminExcursions,
    getAdminreservation: (state) => state.adminReservations,
    getTeamData: (s) => s.teamData,
    getProject: (s) => s.project,
    getCulturalSpace: (s) => s.culturalSpace,
    getHistory: (s) => s.history
  },
  persist: {
    key: 'data-store',
    storage: window.localStorage,
    paths: ['auth_key', 'excursionsStats'],
  },
})
