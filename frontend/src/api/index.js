import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

/** @typedef {{ id: number, name: string, difficulty: string, region: string, mileage: number, days: number, marker_count: number }} Route */
/** @typedef {{ id: number, route_id: number, type: '水源' | '休息', coordinates: string, notes: string, reliability?: '高' | '中' | '低' | null }} Marker */
/** @typedef {{ id: number, route_id: number, name: string, is_required: number }} Equipment */

export const routeApi = {
  /** @param {{ name?: string, region?: string, difficulty?: string }} params @returns {Promise<Route[]>} */
  list: (params = {}) => api.get('/routes', { params }).then((r) => r.data),
  /** @returns {Promise<string[]>} */
  regions: () => api.get('/routes/regions').then((r) => r.data),
  /** @returns {Promise<string[]>} */
  difficulties: () => api.get('/routes/difficulties').then((r) => r.data),
  /** @param {number} id @returns {Promise<Route>} */
  get: (id) => api.get(`/routes/${id}`).then((r) => r.data),
  /** @param {{ name: string, difficulty: string, region: string, mileage?: number, days?: number }} data @returns {Promise<Route>} */
  create: (data) => api.post('/routes', data).then((r) => r.data),
  /** @param {number} id @param {{ name: string, difficulty: string, region: string, mileage?: number, days?: number }} data @returns {Promise<Route>} */
  update: (id, data) => api.put(`/routes/${id}`, data).then((r) => r.data),
  /** @param {number} id */
  remove: (id) => api.delete(`/routes/${id}`),
  /** @param {number} id @returns {Promise<Route>} */
  clone: (id) => api.post(`/routes/${id}/clone`).then((r) => r.data),
  /** @param {number} id @returns {Promise<string>} */
  export: (id) => api.get(`/routes/${id}/export`, { responseType: 'text' }).then((r) => r.data),
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

export const equipmentApi = {
  /** @param {number} routeId @returns {Promise<Equipment[]>} */
  list: (routeId) => api.get(`/routes/${routeId}/equipment`).then((r) => r.data),
  /** @param {number} routeId @param {{ name: string, isRequired: number }} data @returns {Promise<Equipment>} */
  create: (routeId, data) => api.post(`/routes/${routeId}/equipment`, data).then((r) => r.data),
  /** @param {number} id */
  remove: (id) => api.delete(`/equipment/${id}`),
}

export default api
