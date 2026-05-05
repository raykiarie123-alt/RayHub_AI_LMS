import api from './api';

export const ragApi = {
  ask: (data) => api.post('/rag/ask', data),
  askResource: (data) => api.post('/rag/ask-resource', data),
  askTopic: (data) => api.post('/rag/ask-topic', data),
  getHistory: () => api.get('/rag/history'),
  deleteChat: (id) => api.delete(`/rag/history/${id}`),
};


