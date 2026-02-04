import axios, { AxiosError, type AxiosResponse } from 'axios'
import type { APIError } from './types'

// Create Axios instance with base configuration
export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
})

// Request interceptor (for adding auth tokens, etc.)
apiClient.interceptors.request.use(
  (config) => {
    // You can add auth headers here if needed in the future
    // const token = localStorage.getItem('auth_token')
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`
    // }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor (for centralized error handling)
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  (error: AxiosError<APIError>) => {
    // Handle different error types
    if (error.response) {
      // Server responded with error status
      const apiError: APIError = {
        detail: error.response.data?.detail || error.message,
        status_code: error.response.status,
      }

      // Log error for debugging
      console.error('API Error:', apiError)

      // You can add toast notifications here
      // toast.error(apiError.detail)

      return Promise.reject(apiError)
    } else if (error.request) {
      // Request made but no response received (network error)
      const networkError: APIError = {
        detail: 'Network error: Unable to reach the server',
        status_code: 0,
      }
      console.error('Network Error:', networkError)
      return Promise.reject(networkError)
    } else {
      // Something happened in setting up the request
      const unknownError: APIError = {
        detail: error.message || 'Unknown error occurred',
        status_code: -1,
      }
      console.error('Unknown Error:', unknownError)
      return Promise.reject(unknownError)
    }
  }
)

export default apiClient
