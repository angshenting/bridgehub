import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for auth tokens (when implemented)
api.interceptors.request.use(
  (config) => {
    // Add auth token when available
    // const token = getAuthToken()
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`
    // }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle authentication errors
      console.error('Authentication error')
    }
    return Promise.reject(error)
  }
)

// API function helpers
export const apiClient = {
  // Players
  getPlayers: (params?: { skip?: number; limit?: number; status?: string }) =>
    api.get('/players', { params }),
  getPlayer: (id: number) => api.get(`/players/${id}`),
  getPlayerMasterpoints: (id: number) => api.get(`/players/${id}/masterpoints`),
  getPlayerRatings: (id: number) => api.get(`/players/${id}/ratings`),
  
  // Events
  getEvents: (params?: { skip?: number; limit?: number; status?: string }) =>
    api.get('/events', { params }),
  getRecentEvents: (days: number = 30) => api.get('/events/recent', { params: { days } }),
  getEvent: (id: number) => api.get(`/events/${id}`),
  getEventResults: (id: number) => api.get(`/events/${id}/results`),
  
  // Results
  getResultsByEvent: (eventId: number) => api.get(`/results/event/${eventId}`),
  getPlayerResults: (playerId: number) => api.get(`/results/player/${playerId}`),
  getLeaderboard: (period: string = 'all') => api.get('/results/leaderboard', { params: { period } }),
  
  // Organizations
  getOrganizations: () => api.get('/organizations'),
  getOrganization: (id: number) => api.get(`/organizations/${id}`),
  
  // Health check
  healthCheck: () => axios.get(`${API_BASE_URL}/health`),
}