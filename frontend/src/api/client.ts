import axios from 'axios';

// Default FastAPI Port
const API_BASE_URL = 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // 120s — multi-layer LLM pipeline can take 30-60s with local models
});

export const ChatAPI = {
  sendMessage: async (message: string) => {
    const response = await apiClient.post('/chat/message', { message });
    return response.data;
  },
};

export const MemoryAPI = {
  getMemories: async (skip = 0, limit = 100) => {
    const response = await apiClient.get(`/memory?skip=${skip}&limit=${limit}`);
    return response.data;
  },
  deleteMemory: async (id: string) => {
    const response = await apiClient.delete(`/memory/${id}`);
    return response.data;
  },
};

export const ToolsAPI = {
  getSchemas: async () => {
    const response = await apiClient.get('/tools');
    return response.data;
  },
  getStatus: async () => {
    const response = await apiClient.get('/tools/status');
    return response.data;
  }
};
