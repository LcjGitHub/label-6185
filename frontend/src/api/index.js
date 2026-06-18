import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

/** @typedef {{ id: number, name: string, difficulty: string, region: string, mileage: number, days: number }} Route */
/** @typedef {{ id: number, route_id: number, type: '水源' | '休息', coordinates: string, notes: string, reliability?: '高' | '中' | '低' | null }} Marker */

export const routeApi = {
  /** @param {string} [region] @returns {Promise<Route[]>} */
  list: (region) => api.get('/routes', { params: { region } }).then((r) => r.data),
  /** @returns {Promise<string[]>} */
  regions: () => api.get('/routes/regions').then((r) => r.data),
  /** @param {number} id @returns {Promise<Route>} */
  get: (id) => api.get(`/routes/${id}`).then((r) => r.data),
  /** @param {{ name: string, difficulty: string, region: string, mileage?: number, days?: number }} data @returns {Promise<Route>} */
  create: (data) => api.post('/routes', data).then((r) => r.data),
  /** @param {number} id @param {{ name: string, difficulty: string, region: string, mileage?: number, days?: number }} data @returns {Promise<Route>} */
  update: (id, data) => api.put(`/routes/${id}`, data).then((r) => r.data),
  /** @param {number} id */
  remove: (id) => api.delete(`/routes/${id}`),
}

export const statsApi = {
  get: () => api.get('/stats').then((r) => r.data),
}

export const markerApi = {
  /** @param {number} routeId @returns {Promise<Marker[]>} */
  list: (routeId) => api.get(`/routes/${routeId}/markers`).then((r) => r.data),
  /** @param {number} routeId @param {{ type: string, coordinates: string, notes?: string, reliability?: string | null }} data @returns {Promise<Marker>} */
  create: (routeId, data) => api.post(`/routes/${routeId}/markers`, data).then((r) => r.data),
  /** @param {number} id @param {{ type: string, coordinates: string, notes?: string, reliability?: string | null }} data @returns {Promise<Marker>} */
  update: (id, data) => api.put(`/markers/${id}`, data).then((r) => r.data),
  /** @param {number} id */
  remove: (id) => api.delete(`/markers/${id}`),
}

export default api
