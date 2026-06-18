import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

/** @typedef {{ id: number, name: string, difficulty: string }} Route */
/** @typedef {{ id: number, route_id: number, type: '水源' | '休息', coordinates: string, notes: string }} Marker */

export const routeApi = {
  /** @returns {Promise<Route[]>} */
  list: () => api.get('/routes').then((r) => r.data),
  /** @param {number} id @returns {Promise<Route>} */
  get: (id) => api.get(`/routes/${id}`).then((r) => r.data),
  /** @param {{ name: string, difficulty: string }} data @returns {Promise<Route>} */
  create: (data) => api.post('/routes', data).then((r) => r.data),
  /** @param {number} id @param {{ name: string, difficulty: string }} data @returns {Promise<Route>} */
  update: (id, data) => api.put(`/routes/${id}`, data).then((r) => r.data),
  /** @param {number} id */
  remove: (id) => api.delete(`/routes/${id}`),
}

export const markerApi = {
  /** @param {number} routeId @returns {Promise<Marker[]>} */
  list: (routeId) => api.get(`/routes/${routeId}/markers`).then((r) => r.data),
  /** @param {number} routeId @param {{ type: string, coordinates: string, notes?: string }} data @returns {Promise<Marker>} */
  create: (routeId, data) => api.post(`/routes/${routeId}/markers`, data).then((r) => r.data),
  /** @param {number} id @param {{ type: string, coordinates: string, notes?: string }} data @returns {Promise<Marker>} */
  update: (id, data) => api.put(`/markers/${id}`, data).then((r) => r.data),
  /** @param {number} id */
  remove: (id) => api.delete(`/markers/${id}`),
}

export default api
