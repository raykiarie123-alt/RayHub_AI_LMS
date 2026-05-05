import api from './api';

export const resourceApi = {
  getResources: (params) => api.get('/resources/', { params }),
  getResource: (id) => api.get(`/resources/${id}`),
  summarizeResource: (id) => api.post(`/resources/${id}/summarize`),

  // Documents
  uploadDocument: (formData) => api.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getDocuments: (params) => api.get('/documents/', { params }),
  deleteDocument: (id) => api.delete(`/documents/${id}`),

  // YouTube
  ingestYouTube: (data) => api.post('/youtube/ingest', data),
  summarizeYouTube: (data) => api.post('/youtube/summarize', data),
  getYouTubeResources: () => api.get('/youtube/resources'),

  // Web
  ingestWeb: (data) => api.post('/web/ingest', data),
  summarizeWeb: (data) => api.post('/web/summarize', data),
};