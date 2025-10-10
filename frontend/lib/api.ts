import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance
export const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Add auth token if available
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('auth_token');
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }

    // Add session ID for chat
    const sessionId = typeof window !== 'undefined' ? localStorage.getItem('chat_session_id') : null;
    if (sessionId && config.headers) {
      config.headers['X-Session-ID'] = sessionId;
    }

    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error: AxiosError) => {
    // Handle specific error cases
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // Unauthorized - redirect to login
          if (typeof window !== 'undefined') {
            localStorage.removeItem('auth_token');
            window.location.href = '/login';
          }
          break;
        case 403:
          // Forbidden
          console.error('Access forbidden:', error.response.data);
          break;
        case 404:
          // Not found
          console.error('Resource not found:', error.response.data);
          break;
        case 429:
          // Too many requests
          console.error('Rate limit exceeded:', error.response.data);
          break;
        case 500:
          // Server error
          console.error('Server error:', error.response.data);
          break;
        default:
          console.error('API error:', error.response.data);
      }
    } else if (error.request) {
      // Request made but no response
      console.error('No response from server:', error.request);
    } else {
      // Request setup error
      console.error('Request error:', error.message);
    }

    return Promise.reject(error);
  }
);

// API Methods for Phase 1: Video Commerce Platform
export const videoAPI = {
  // Get featured video
  getFeatured: () => api.get('/videos/featured'),

  // Get all videos
  getVideos: (params?: {
    page?: number;
    limit?: number;
    category?: string;
  }) => api.get('/videos', { params }),

  // Get video by ID
  getById: (id: string) => api.get(`/videos/${id}`),

  // Track video view
  trackView: (videoId: string) => api.post(`/videos/${videoId}/view`),

  // Like/unlike video
  toggleLike: (videoId: string) => api.post(`/videos/${videoId}/like`),
};

// API Methods for Products
export const productAPI = {
  // Get all products
  getProducts: (params?: {
    search?: string;
    category?: string;
    min_price?: number;
    max_price?: number;
    sort_by?: string;
    page?: number;
    limit?: number;
  }) => api.get('/products', { params }),

  // Get product by ID
  getById: (id: string) => api.get(`/products/${id}`),

  // Get products by video
  getByVideo: (videoId: string) => api.get(`/videos/${videoId}/products`),
};

// API Methods for Phase 2: Maeju Chat
export const chatAPI = {
  // Initialize chat session
  init: (data: { user_preferences?: Record<string, any> }) =>
    api.post('/chat/init', data),

  // Send message
  sendMessage: (data: {
    session_id?: string;
    message: string;
    context?: Record<string, any>;
  }) => api.post('/chat/message', data),

  // Get chat history
  getHistory: (sessionId: string) => api.get(`/chat/history/${sessionId}`),

  // Clear chat session
  clearSession: (sessionId: string) => api.delete(`/chat/session/${sessionId}`),
};

// API Methods for Phase 3: CAMEO Generation
export const cameoAPI = {
  // Generate CAMEO video
  generate: (data: {
    occasion: string;
    recipient_name: string;
    personal_message: string;
    product_ids: string[];
    tone: string;
    delivery_date?: string;
  }) => api.post('/cameo/generate', data),

  // Get CAMEO status
  getStatus: (cameoId: string) => api.get(`/cameo/${cameoId}/status`),

  // Get user's CAMEOs
  getUserCAMEOs: () => api.get('/cameo/user'),

  // Download CAMEO
  download: (cameoId: string) => api.get(`/cameo/${cameoId}/download`, {
    responseType: 'blob',
  }),
};

// API Methods for Checkout
export const checkoutAPI = {
  // Get cart
  getCart: () => api.get('/cart'),

  // Add to cart
  addToCart: (data: { product_id: string; quantity: number }) =>
    api.post('/cart/add', data),

  // Remove from cart
  removeFromCart: (itemId: string) => api.delete(`/cart/${itemId}`),

  // Update cart item
  updateCart: (itemId: string, quantity: number) =>
    api.put(`/cart/${itemId}`, { quantity }),

  // Create checkout session
  createSession: (data: {
    email: string;
    shipping_info: Record<string, any>;
    items: any[];
    success_url: string;
    cancel_url: string;
  }) => api.post('/checkout/create-session', data),

  // Get checkout session
  getSession: (sessionId: string) => api.get(`/checkout/session/${sessionId}`),

  // Confirm payment
  confirmPayment: (sessionId: string) =>
    api.post(`/checkout/confirm/${sessionId}`),
};

// API Methods for AR Experience
export const arAPI = {
  // Get AR model for product
  getModel: (productId: string) => api.get(`/ar/${productId}/model`),

  // Track AR interaction
  trackInteraction: (productId: string, data: Record<string, any>) =>
    api.post(`/ar/${productId}/track`, data),
};

// Utility function to handle file uploads
export const uploadFile = async (
  file: File,
  onProgress?: (progress: number) => void
): Promise<any> => {
  const formData = new FormData();
  formData.append('file', file);

  return api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const progress = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        onProgress(progress);
      }
    },
  });
};

// Health check
export const healthCheck = () => api.get('/health');

export default api;
